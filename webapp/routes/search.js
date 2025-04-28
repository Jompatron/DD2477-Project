const express = require('express');
const router = express.Router();
const esClient = require('../config/es_config');
// const { generateTransposedQueries } = require('../utils/melodyUtils');

// router.post('/', async (req, res) => {
//   const { query, composer, searchType, multiKey } = req.body;
//   let esQuery;

//   if (composer) {
//     esQuery = { match: { composer: composer } };

//   } else if (query) {
//     if (searchType === 'melody') {
//       // Generate transposed queries
//       const transposedMelodies = generateTransposedQueries(query);
      
//       // Build a bool query that uses a match_phrase for each transposition
//       const shouldQueries = transposedMelodies.map(melody =>
//         ({ match_phrase: { tokens: melody } })
//       );
      
//       esQuery = { bool: { should: shouldQueries, minimum_should_match: 1 } };
//   } else if (searchType === 'phrase') {
//     if (searchType === 'phrase') {
//       // Require an exact token phrase match
//       esQuery = {
//         bool: {
//           must: [
//             { match_phrase: { tokens: query } }
//           ],
//           // Optionally boost matches from other fields:
//           should: [
//             {
//               multi_match: {
//                 query: query,
//                 fields: ["title", "composer", "key", "time_signature"]
//               }
//             }
//           ]
//         }
//       };
//     } else {
//       // Default search using multi_match on standard fields
//       esQuery = {
//         multi_match: {
//           query: query,
//           fields: ["title", "composer", "key", "time_signature", "tokens"]
//         }
//       };
//     }
//   } else {
//     return res.status(400).json({ error: "Please provide a search parameter." });
//   }

//   try {
//     const result = await esClient.search({
//       index: 'musicxml',
//       body: { query: esQuery }
//     });
//     res.json(result.body.hits.hits);
//   } catch (error) {
//     console.error('Elasticsearch query error:', error);
//     res.status(500).json({ error: 'Search error' });
//   }
// }});

// module.exports = router;

const { fingerprintMelody } = require('../utils/melodyUtils');

/**
 * POST /search
 * body: { query, searchType: 'phrase'|'melody'|'rhythm', multiKey }
 */
router.post('/', async (req, res) => {
  const { query, searchType, multiKey } = req.body;
  if (!query) return res.status(400).json({ error: 'Provide body.query' });

  try {
    if (searchType === 'phrase') {
      const esQuery = {
        bool: {
          must: [
            { match_phrase: { tokens: query } }
          ],
          should: [
            {
              multi_match: {
                query: query,
                fields: ["title", "composer", "key", "time_signature"]
              }
            }
          ]
        }
      };

      const esResponse = await esClient.search({
        index: 'musicxml_intervals',
        body: { size: 10, query: esQuery }
      });
      const hits = esResponse.body.hits.hits.map(h => ({
        title: h._source.title,
        composer: h._source.composer,
        score: h._score
      }));
      return res.json({ mode: 'phrase', results: hits });
    }

    if (searchType === 'melody') {
      const tokens = query.trim().split(/\s+/);
      const fp = fingerprintMelody(tokens);
      console.log(`Generated fingerprint (fp): ${fp}`); // Debugging log
      let esResponse = await esClient.search({
        index: 'musicxml_intervals',
        body: { size: 10, query: { match_phrase: { interval_fp: { query: fp } } } }
      });
      let hits = esResponse.body.hits.hits;
      let mode = 'exact';
      if (hits.length === 0) {
        esResponse = await esClient.search({
          index: 'musicxml_intervals',
          body: { size: 10, query: { wildcard: { interval_fp: { value: `*${fp}*` } } } }
        });
        hits = esResponse.body.hits.hits;
        mode = 'wildcard';
      }
      const results = hits.map(h => ({
        title: h._source.title,
        composer: h._source.composer,
        score: h._score
      }));
      return res.json({ mode, query_fp: fp, results });
    }

    if (searchType === 'rhythm') {
      return res.status(501).json({ error: 'Rhythmic search not implemented' });
    }

    return res.status(400).json({ error: 'Invalid searchType' });
  } catch (err) {
    console.error('Search error:', err);
    return res.status(500).json({ error: 'ES search failed', details: err.message });
  }
});

module.exports = router;
