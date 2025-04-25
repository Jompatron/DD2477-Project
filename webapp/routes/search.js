const express = require('express');
const router = express.Router();
const esClient = require('../config/es_config');
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
      const esResponse = await esClient.search({
        index: 'musicxml_intervals',
        body: { size: 10, query: { match_phrase: { tokens_str: { query } } } }
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