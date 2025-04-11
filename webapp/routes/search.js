const express = require('express');
const router = express.Router();
const esClient = require('../config/es_config');
const { generateTransposedQueries } = require('../utils/melodyUtils');
router.post('/', async (req, res) => {
  const { query, composer, searchType, multiKey } = req.body;
  let esQuery;

  if (composer) {
    esQuery = { match: { composer: composer } };

  } else if (query) {
    if (searchType === 'melody') {
      // Generate transposed queries
      const transposedMelodies = generateTransposedQueries(query);
      
      // Build a bool query that uses a match_phrase for each transposition
      const shouldQueries = transposedMelodies.map(melody =>
        ({ match_phrase: { tokens: melody } })
      );
      
      esQuery = { bool: { should: shouldQueries, minimum_should_match: 1 } };
  } else if (searchType === 'phrase') {
    if (searchType === 'phrase') {
      // Require an exact token phrase match
      esQuery = {
        bool: {
          must: [
            { match_phrase: { tokens: query } }
          ],
          // Optionally boost matches from other fields:
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
    } else {
      // Default search using multi_match on standard fields
      esQuery = {
        multi_match: {
          query: query,
          fields: ["title", "composer", "key", "time_signature", "tokens"]
        }
      };
    }
  } else {
    return res.status(400).json({ error: "Please provide a search parameter." });
  }

  try {
    const result = await esClient.search({
      index: 'musicxml',
      body: { query: esQuery }
    });
    res.json(result.body.hits.hits);
  } catch (error) {
    console.error('Elasticsearch query error:', error);
    res.status(500).json({ error: 'Search error' });
  }
}});

module.exports = router;

