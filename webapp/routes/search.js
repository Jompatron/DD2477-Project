const express = require('express');
const router = express.Router();
const esClient = require('../config/es_config');

router.post('/', async (req, res) => {
  // Expecting the JSON body to possibly contain both 'query' and 'composer'
  const { query, composer } = req.body;

  // Build the appropriate query based on the input
  let esQuery;
  if (composer) {
    // If a composer is specified, search specifically on the 'composer' field
    esQuery = {
      match: {
        composer: composer
      }
    };
  } else if (query) {
    // Otherwise, perform a broader multi-field search
    esQuery = {
      multi_match: {
        query: query,
        fields: ["title", "composer", "key", "time_signature", "tokens"]
      }
    };
  } else {
    return res.status(400).json({ error: "Please provide a search parameter." });
  }

  try {
    const result = await esClient.search({
      index: 'musicxml',  // Make sure this index name matches your indexing logic
      body: {
        query: esQuery
      }
    });
    res.json(result.body.hits.hits);
  } catch (error) {
    console.error('Elasticsearch query error:', error);
    res.status(500).json({ error: 'Search error' });
  }
});

module.exports = router;
