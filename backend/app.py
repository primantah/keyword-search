from flask import Flask, request, jsonify
import instaloader
from flask_cors import CORS  # type: ignore
import webbrowser
import threading

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def fetch_latest_post_with_keyword(username, keyword, last_post):
    loader = instaloader.Instaloader()

    try:
        profile = instaloader.Profile.from_username(loader.context, username)
        found_last_post = last_post is None  # Start searching immediately if no last post is provided

        for post in profile.get_posts():
            if not found_last_post:
                # Skip posts until we reach the last_post
                if post.shortcode == last_post:
                    found_last_post = True
                continue

            caption = post.caption or ""
            if keyword.lower() in caption.lower():
                return {
                    "message": "Match found",
                    "result": {
                        "caption": caption,
                        "link": f"https://www.instagram.com/p/{post.shortcode}/",
                        "shortcode": post.shortcode
                    }
                }
        
        return {"message": "No more matching posts found", "result": None}

    except Exception as e:
        return {"error": str(e)}

# Add a root route for `/`
@app.route('/')
def home():
    return "Keyword Search API is running. Use the `/search` endpoint with a POST request to search for Instagram posts."

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    username = data['username']
    keyword = data['keyword']
    last_post = data.get('last_post')  # Optional parameter

    response = fetch_latest_post_with_keyword(username, keyword, last_post)
    return jsonify(response)

# Add a flag to prevent the browser from opening twice
browser_launched = False

def open_browser():
    global browser_launched
    if not browser_launched:
        # Mark as launched
        browser_launched = True
        # Automatically open the frontend in the default browser
        url = "http://127.0.0.1:8000"  # Local server address for the frontend
        webbrowser.open(url)

if __name__ == '__main__':
    # Serve the frontend (index.html) using a local HTTP server
    def run_http_server():
        import http.server
        import socketserver
        import os

        PORT = 8000
        DIRECTORY = os.path.join(os.path.dirname(__file__), '../frontend')  # Updated path to 'frontend'

        class CustomHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=DIRECTORY, **kwargs)

        with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
            print(f"Serving frontend on http://127.0.0.1:{PORT}")
            httpd.serve_forever()

    # Start the frontend server in a new thread
    threading.Thread(target=run_http_server, daemon=True).start()

    # Open the browser to the frontend only once
    threading.Thread(target=open_browser, daemon=True).start()

    # Start the Flask backend
    app.run(debug=True)
