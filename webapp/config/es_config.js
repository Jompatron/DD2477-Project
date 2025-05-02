require('dotenv').config()
const { Client } = require('@elastic/elasticsearch');

console.log('🔍 ELASTIC_NODE =', process.env.ELASTIC_NODE);


const esClient = new Client({
  // node: process.env.ELASTIC_NODE, // use the service name from docker-compose
  node: 'http://localhost:9200',
  auth: {
    username: process.env.APP_ES_USERNAME,
    password: process.env.APP_ES_PASSWORD
  }
});

module.exports = esClient;
