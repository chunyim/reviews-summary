from flask import Flask, request, jsonify
from flask_cors import CORS
from review_part import summarize

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})



@app.route('/')
def index():
    return "hello world"


@app.route('/api/summarize', methods=['POST'])
async def summarize_reviews():
    if request.method == 'POST':
        data = request.get_json()
        url =  data.get('url')
        reviews = await summarize.scrape_reviews(url)

        result = summarize.summarize(reviews, summarize.model)
        return jsonify({'reviews': reviews,'result': result})


if __name__ == "__main__":
    app.run(debug=True)

