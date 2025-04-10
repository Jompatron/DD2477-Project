const express = require('express');
const path = require('path');
const searchRouter = require('./routes/search');

const app = express();
const PORT = 3000;

// To parse JSON bodies from POST requests
app.use(express.json());

// Serve static files (like index.html)
app.use(express.static(path.join(__dirname, 'public')));

// Route for search functionality
app.use('/search', searchRouter);

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
