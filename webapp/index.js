
const express = require('express');
const path = require('path');
const searchRouter = require('./routes/search');

const app = express();
const PORT = 3000;

// To parse JSON bodies from POST requests
app.use(express.json());

app.get('/health', async (req, res) => {
  try { await esClient.ping(); res.json({ status: 'ok' }); }
  catch (e) { res.status(500).json({ status: 'error', error: e.message }); }
});


// Serve static files (like index.html)
app.use(express.static(path.join(__dirname, 'public')));

// Route for search functionality
app.use('/search', searchRouter);

// Serve static XML files from the 'scores' directory
app.use('/scores', express.static('/app/corpus'));

app.get('/score/:id', async (req, res) => {
  const id = req.params.id;
  const result = await getScoreById(id); // Implement this function
  res.type('text/xml').send(result.musicxml);
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});