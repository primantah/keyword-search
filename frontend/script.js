let lastPost = null; // To keep track of the last fetched post

document.getElementById('searchForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const keyword = document.getElementById('keyword').value;
    const resultsDiv = document.getElementById('results');
    const loadMoreButton = document.getElementById('loadMore');

    // Clear previous results and reset the last post tracker
    resultsDiv.innerHTML = '';
    lastPost = null;

    // Fetch the first result
    await fetchPosts(username, keyword, resultsDiv, loadMoreButton);
});

document.getElementById('loadMore').addEventListener('click', async () => {
    const username = document.getElementById('username').value;
    const keyword = document.getElementById('keyword').value;
    const resultsDiv = document.getElementById('results');
    const loadMoreButton = document.getElementById('loadMore');

    // Fetch the next result
    await fetchPosts(username, keyword, resultsDiv, loadMoreButton);
});

async function fetchPosts(username, keyword, resultsDiv, loadMoreButton) {
    // Display loading message
    const loadingMessage = document.createElement('p');
    loadingMessage.textContent = 'Loading...';
    resultsDiv.appendChild(loadingMessage);

    try {
        // Send POST request to Flask backend
        const response = await fetch('http://127.0.0.1:5000/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, keyword, last_post: lastPost })
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }

        const data = await response.json();

        // Remove the loading message
        resultsDiv.removeChild(loadingMessage);

        // Handle results
        if (data.message === "Match found") {
            const post = data.result;

            // Append the new result
            const postDiv = document.createElement('div');
            postDiv.innerHTML = `
                <h2>Result</h2>
                <p><strong>Caption:</strong> ${post.caption}</p>
                <p><a href="${post.link}" target="_blank">View Post</a></p>
            `;
            resultsDiv.appendChild(postDiv);

            // Update lastPost for fetching the next result
            lastPost = post.shortcode;

            // Show the "Show Me More" button
            loadMoreButton.style.display = 'block';
        } else {
            const noMoreMessage = document.createElement('p');
            noMoreMessage.textContent = data.message;
            resultsDiv.appendChild(noMoreMessage);

            // Hide the "Show Me More" button
            loadMoreButton.style.display = 'none';
        }
    } catch (error) {
        resultsDiv.removeChild(loadingMessage);
        resultsDiv.innerHTML += `<p>Error: ${error.message}</p>`;
    }
}
