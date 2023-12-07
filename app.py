from flask import Flask, render_template, request, send_file
from myscraper import scrape_search_results

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    brand_name = request.form['brand_name']
    csv_filename = scrape_search_results(brand_name)  # Assuming scrape_search_results returns the filename
    return render_template('index.html', csv_filename=csv_filename)

@app.route('/download/<csv_filename>', methods=['GET'])
def download(csv_filename):
    return send_file(csv_filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
