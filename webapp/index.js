const express = require('express');
const path = require('path');
const esClient = require('./config/es_config');
const app = express();

app.use(express.json());
app.get('/health', async (req, res) => {
  try { await esClient.ping(); res.json({ status: 'ok' }); }
  catch (e) { res.status(500).json({ status: 'error', error: e.message }); }
});
app.use('/search', require('./routes/search'));
app.use(express.static(path.join(__dirname, 'public')));
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));