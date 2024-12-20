# Required Libraries
from flask import Flask, request, jsonify, render_template
import hashlib
import os
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from werkzeug.utils import secure_filename
from difflib import SequenceMatcher

# Initialize Flask App
app = Flask(__name__)

# Configurations
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Utility Functions

def fetch_text_from_url(url):
    """
    Fetch text content from a URL.
    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup.get_text()
        return None
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return None

def hash_image(image_path):
    """
    Generate a SHA-256 hash for an image file.
    """
    hasher = hashlib.sha256()
    with open(image_path, 'rb') as img:
        buf = img.read()
        hasher.update(buf)
    return hasher.hexdigest()

def similar(a, b):
    """
    Check similarity between two strings using SequenceMatcher.
    """
    return SequenceMatcher(None, a, b).ratio()

# Simulated piracy data for text and image analysis
PIRACY_KEYWORDS = ["pirated", "illegal download", "torrent", "free movie"]
SIMULATED_IMAGE_HASHES = ["d2d2d2d2f4f4f4f4b1b1b1b1c3c3c3c3", "e3e3e3e3a4a4a4a4d5d5d5d5f6f6f6f6"]

# Routes

@app.route('/')
def index():
    """
    Render the homepage with forms for text and image analysis.
    """
    return render_template('index.html')

@app.route('/detect-text', methods=['POST'])
def detect_text():
    """
    Analyze text content from a URL for piracy-related keywords.
    """
    data = request.get_json()
    url = data.get('url')
    keyword = data.get('keyword')

    if not url or not keyword:
        return jsonify({"error": "URL and keyword are required."}), 400

    # Fetch the text content from the URL
    text_content = fetch_text_from_url(url)
    if not text_content:
        return jsonify({"error": "Failed to fetch content from URL."}), 400

    # Search for keyword and similar words in the content
    matches = []
    if keyword.lower() in text_content.lower():
        matches.append(keyword)

    for word in PIRACY_KEYWORDS:
        if similar(word.lower(), keyword.lower()) > 0.8:
            matches.append(word)

    if matches:
        return jsonify({
            "message": "Potential Piracy Detected",
            "matches": matches,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    else:
        return jsonify({
            "message": "No piracy detected in the text.",
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

@app.route('/detect-image', methods=['POST'])
def detect_image():
    """
    Analyze uploaded image for piracy by comparing its hash.
    """
    if 'image' not in request.files:
        return jsonify({"error": "No file uploaded."}), 400

    image = request.files['image']
    if image.filename == '':
        return jsonify({"error": "No selected file."}), 400

    # Save the uploaded image
    filename = secure_filename(image.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(file_path)

    # Generate hash and check against simulated piracy database
    image_hash = hash_image(file_path)

    if image_hash in SIMULATED_IMAGE_HASHES:
        os.remove(file_path)  # Clean up
        return jsonify({
            "message": "Potential Piracy Detected",
            "pirated": True,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    else:
        os.remove(file_path)  # Clean up
        return jsonify({
            "message": "No piracy detected in the image.",
            "pirated": False,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

# Run the App
if __name__ == '__main__':
    app.run(debug=True)
