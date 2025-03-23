from flask import Flask, request, jsonify, render_template
import logging
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(filename='app.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s')

app.static_folder = 'static'

def fetch_amazon_products(product_names):
    mock_api_response = {
        "laptop": {
            "price": 999.99,
            "rating": 4.5,
            "reviews": ["Fast performance", "Battery could be better", "Great for work"],
            "amazon_url": "https://amzn.to/4huW45a",
            "is_search_page": True
        },
        "yoga mat": {
            "price": 29.99,
            "rating": 4.5,
            "reviews": ["Non-slip", "Thin padding", "Easy to carry"],
            "amazon_url": "https://amzn.to/41RTeRT",
            "is_search_page": False
        },
        "board game": {
            "price": 39.99,
            "rating": 4.8,
            "reviews": ["Super fun", "Long playtime", "Great for families"],
            "amazon_url": "https://amzn.to/4bWdt5K",
            "is_search_page": False
        },
        "beef tallow": {
            "price": 19.99,
            "rating": 4.3,
            "reviews": ["Great for cooking", "Strong smell", "Good quality"],
            "amazon_url": "https://amzn.to/4ivkVHn",
            "is_search_page": False
        }
    }
    return {name: mock_api_response.get(name, {}) for name in product_names}

def analyze_reviews(reviews):
    positive_words = {"great": 1, "love": 1, "best": 1.5, "awesome": 1, "excellent": 1}
    negative_words = {"broke": -1, "poor": -1, "pricey": -0.5, "bad": -1, "terrible": -1}
    sentiment_score = 0
    keywords = {}
    for review in reviews:
        for word in review.lower().split():
            if word in positive_words:
                sentiment_score += positive_words[word]
                keywords[word] = keywords.get(word, 0) + 1
            elif word in negative_words:
                sentiment_score += negative_words[word]
                keywords[word] = keywords.get(word, 0) + 1
    positive = sum(1 for r in reviews if any(w in r.lower() for w in positive_words))
    negative = sum(1 for r in reviews if any(w in r.lower() for w in negative_words))
    return {
        "positive": positive,
        "negative": negative,
        "keywords": keywords,
        "sentiment_score": round(sentiment_score, 2)
    }

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/compare')
def compare_page():
    return render_template('compare.html')

@app.route('/compare', methods=['POST'])
def compare_products():
    try:
        data = request.get_json()
        product_names = data.get('products', [])
        logging.info(f"POST request received with products: {product_names}")
        if not product_names:
            logging.error("No products provided in POST request")
            return jsonify({"error": "No products provided"}), 400
        products = fetch_amazon_products(product_names)
        logging.info(f"Fetched products: {products}")
        comparisons = {}
        for name, product in products.items():
            if product:
                review_summary = analyze_reviews(product["reviews"])
                comparisons[name] = {
                    "price": product["price"],
                    "rating": product["rating"],
                    "review_summary": review_summary,
                    "amazon_url": product.get("amazon_url", "#"),
                    "is_search_page": product.get("is_search_page", False)
                }
            else:
                logging.warning(f"Product not found: {name}")
        if not comparisons:
            logging.warning("No valid products found")
            return jsonify({"error": "No matching products"}), 404
        logging.debug(f"Returning comparisons: {comparisons}")
        return jsonify({"comparisons": comparisons}), 200
    except Exception as e:
        logging.error(f"Error in compare_products: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    logging.info(f"Starting server at {datetime.now()}")
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)