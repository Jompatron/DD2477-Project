const { Client } = require('@elastic/elasticsearch');

const esClient = new Client({
  node: 'http://elasticsearch:9200' // use the service name from docker-compose
});

module.exports = esClient;
