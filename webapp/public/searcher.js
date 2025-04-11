// searcher.js

// Wait until the DOM is loaded before adding event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Grab the form elements by their IDs
    const form = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    const searchTypeSelect = document.getElementById('search-type');
    const multiKeyCheckbox = document.getElementById('multi-key');
    const resultsContainer = document.getElementById('search-results');
  
    // Listen for form submission
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
  
      // Get the current values from the controls
      const query = searchInput.value;
      const searchType = searchTypeSelect.value;  // Either "phrase" or "melody"
      const multiKey = multiKeyCheckbox.checked;    // true or false
  
      // Create a payload to send to the backend.
      // You can later customize how each search type is processed on the server.
      const payload = {
        query,
        searchType,
        multiKey
      };
  
      try {
        // Send the payload to your backend search endpoint via POST
        const response = await fetch('/search', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        });
        
        // Parse JSON response from the backend
        const data = await response.json();
  
        // Render your search results (here simply displaying JSON)
        resultsContainer.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
      } catch (error) {
        console.error("Error during search: ", error);
        resultsContainer.textContent = "An error occurred during the search.";
      }
    });
  });
  