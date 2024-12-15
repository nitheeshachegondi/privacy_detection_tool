from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
import requests
import hashlib
import os
import json
from datetime import datetime

app = Flask(__name__)

# Load predefined piracy hashes (hardcoded piracy database)
with open('pirated_hashes.json', 'r') as file:
    PIRATED_HASHES = json.load(file)

# Directory to store generated reports
REPORTS_DIR = 'reports'
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)


# Route for Home Page
@app.route('/')
def index():
    return render_template('index.html')


# Route for Text Analysis
@app.route('/text_analysis', methods=['POST'])
def text_analysis():
    url = request.form['url']
    keyword = request.form['keyword']
    report = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "url": url, "keyword": keyword}

    try:
        # Fetch the web page content
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()

        # Search for the keyword
        positions = [i for i in range(len(text)) if text.startswith(keyword, i)]
        if positions:
            report['text_matches'] = [{"position": pos, "context": text[max(0, pos-30):pos+30]} for pos in positions]
            report['result'] = "Potential Piracy Detected: Keyword found."
        else:
            report['result'] = "No piracy detected for the keyword."

    except Exception as e:
        report['result'] = f"Error fetching URL: {str(e)}"

    # Save report
    save_report(report)
    return jsonify(report)


# Route for Image Analysis
@app.route('/image_analysis', methods=['POST'])
def image_analysis():
    image = request.files['image']
    report = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "filename": image.filename}

    try:
        # Generate image hash
        image_hash = hashlib.sha256(image.read()).hexdigest()
        if image_hash in PIRATED_HASHES:
            report['result'] = "Potential Piracy Detected: Uploaded image matches pirated content."
        else:
            report['result'] = "No piracy detected for the uploaded image."

    except Exception as e:
        report['result'] = f"Error processing image: {str(e)}"

    # Save report
    save_report(report)
    return jsonify(report)


# Save Report to a File
def save_report(report):
    filename = os.path.join(REPORTS_DIR, f"report_{datetime.now().timestamp()}.json")
    with open(filename, 'w') as file:
        json.dump(report, file, indent=4)


# Start Flask Server
if __name__ == '__main__':
    app.run(debug=True)
