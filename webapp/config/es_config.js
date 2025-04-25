const { Client } = require('@elastic/elasticsearch');
const ES_NODE = process.env.ES_NODE || 'http://elasticsearch:9200';
console.log(`Using Elasticsearch node: ${ES_NODE}`);
const client = new Client({ node: ES_NODE });
module.exports = client;