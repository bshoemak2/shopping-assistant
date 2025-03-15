from flask import Flask, request, jsonify, render_template
import logging
from datetime import datetime
from amazon_paapi import AmazonApi  # Requires 'pip install python-amazon-paapi'

app = Flask(__name__)
logging.basicConfig(filename='app.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s')

# Amazon API credentials (replace with your own)
ACCESS_KEY = "YOUR_ACCESS_KEY"  # From Amazon Associates
SECRET_KEY = "YOUR_SECRET_KEY"
ASSOCIATE_TAG = "YOUR_ASSOCIATE_TAG"
COUNTRY = "US"  # Adjust for your marketplace

# Initialize Amazon API client (commented out until credentials are added)
# amazon = AmazonApi(ACCESS_KEY, SECRET_KEY, ASSOCIATE_TAG, COUNTRY)

# Mock Amazon data for testing without credentials
def fetch_amazon_products(product_names):
    mock_api_response = {
        "wireless earbuds": {
            "price": 49.99,
            "rating": 4.3,
            "reviews": ["Love the sound quality!", "Broke after a month", "Best earbuds ever"]
        },
        "bluetooth speaker": {
            "price": 69.99,
            "rating": 4.6,
            "reviews": ["Awesome bass!", "A bit pricey", "Excellent for parties"]
        }
    }
    return {name: mock_api_response.get(name, {}) for name in product_names}

# Enhanced review analysis
def analyze_reviews(reviews):
    positive_words = ["great", "love", "best", "awesome", "excellent"]
    negative_words = ["broke", "poor", "pricey", "bad", "terrible"]
    positive = sum(1 for r in reviews if any(w in r.lower() for w in positive_words))
    negative = sum(1 for r in reviews if any(w in r.lower() for w in negative_words))
    keywords = {}
    for review in reviews:
        for word in review.lower().split():
            if word in positive_words + negative_words:
                keywords[word] = keywords.get(word, 0) + 1
    return {
        "positive": positive,
        "negative": negative,
        "keywords": keywords
    }

# Serve the frontend
@app.route('/')
def home():
    return render_template('index.html')

# API endpoint for product comparison
@app.route('/compare', methods=['POST'])
def compare_products():
    try:
        data = request.get_json()
        product_names = data.get('products', [])
        
        logging.info(f"Received request to compare: {product_names}")
        
        if not product_names:
            logging.error("No products provided")
            return jsonify({"error": "No products provided"}), 400
        
        products = fetch_amazon_products(product_names)  # Replace with amazon.search_items() later
        comparisons = {}
        for name, product in products.items():
            if product:
                review_summary = analyze_reviews(product["reviews"])
                comparisons[name] = {
                    "price": product["price"],
                    "rating": product["rating"],
                    "review_summary": review_summary
                }
            else:
                logging.warning(f"Product not found: {name}")
        
        logging.debug(f"Comparison result: {comparisons}")
        return jsonify({"comparisons": comparisons}), 200
    
    except Exception as e:
        logging.error(f"Error in compare_products: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    logging.info(f"Starting server at {datetime.now()}")
    app.run(debug=True, host='0.0.0.0', port=5000)