from flask import Flask, request, jsonify, render_template
import logging
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(filename='app.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s')

# Serve static files from 'static' folder
app.static_folder = 'static'

def fetch_amazon_products(product_names):
    # Mock data with 25 items, Amazon ASINs, and mock Walmart URLs, using Associate ID bshoemak-20
    mock_api_response = {
        "wireless earbuds": {
            "price": 49.99,
            "rating": 4.3,
            "reviews": ["Love the sound quality!", "Broke after a month", "Best earbuds ever"],
            "amazon_url": "https://www.amazon.com/dp/B0CXL6KYSN?tag=bshoemak-20",  # Soundcore Liberty 4 NC
            "walmart_url": "https://www.walmart.com/ip/123456789"  # Mock Walmart ID
        },
        "bluetooth speaker": {
            "price": 69.99,
            "rating": 4.6,
            "reviews": ["Awesome bass!", "A bit pricey", "Excellent for parties"],
            "amazon_url": "https://www.amazon.com/dp/B0CBLKSZVH?tag=bshoemak-20",  # JBL Charge 5
            "walmart_url": "https://www.walmart.com/ip/987654321"
        },
        "laptop": {
            "price": 999.99,
            "rating": 4.5,
            "reviews": ["Fast performance", "Battery could be better", "Great for work"],
            "amazon_url": "https://www.amazon.com/dp/B0CRD8X9RJ?tag=bshoemak-20",  # HP 15.6" Laptop
            "walmart_url": "https://www.walmart.com/ip/456789123"
        },
        "coffee maker": {
            "price": 79.99,
            "rating": 4.4,
            "reviews": ["Easy to use", "Leaks sometimes", "Perfect brew"],
            "amazon_url": "https://www.amazon.com/dp/B0BVDG8MJT?tag=bshoemak-20",  # Keurig K-Express
            "walmart_url": "https://www.walmart.com/ip/321654987"
        },
        "headphones": {
            "price": 299.99,
            "rating": 4.8,
            "reviews": ["Amazing noise cancellation", "A bit heavy", "Top-notch sound"],
            "amazon_url": "https://www.amazon.com/dp/B0CXLJSMQD?tag=bshoemak-20",  # Sony WH-1000XM5
            "walmart_url": "https://www.walmart.com/ip/789123456"
        },
        "smartphone": {
            "price": 799.99,
            "rating": 4.7,
            "reviews": ["Great camera", "Expensive", "Smooth interface"],
            "amazon_url": "https://www.amazon.com/dp/B0CNXLPFLL?tag=bshoemak-20",  # Samsung Galaxy S24
            "walmart_url": "https://www.walmart.com/ip/654321789"
        },
        "tablet": {
            "price": 329.99,
            "rating": 4.6,
            "reviews": ["Perfect for streaming", "Screen scratches easily", "Lightweight"],
            "amazon_url": "https://www.amazon.com/dp/B0BNSDR6VR?tag=bshoemak-20",  # Apple iPad 9th Gen
            "walmart_url": "https://www.walmart.com/ip/147258369"
        },
        "smart watch": {
            "price": 199.99,
            "rating": 4.5,
            "reviews": ["Tracks everything", "Battery drains fast", "Sleek design"],
            "amazon_url": "https://www.amazon.com/dp/B0CHH6X6H2?tag=bshoemak-20",  # Fitbit Versa 4
            "walmart_url": "https://www.walmart.com/ip/258369147"
        },
        "gaming console": {
            "price": 499.99,
            "rating": 4.8,
            "reviews": ["Incredible graphics", "Loud fan", "Worth every penny"],
            "amazon_url": "https://www.amazon.com/dp/B0BFK2G1SG?tag=bshoemak-20",  # PlayStation 5
            "walmart_url": "https://www.walmart.com/ip/369147258"
        },
        "tv": {
            "price": 399.99,
            "rating": 4.4,
            "reviews": ["Vivid colors", "Remote is clunky", "Great value"],
            "amazon_url": "https://www.amazon.com/dp/B0C7VBXCHY?tag=bshoemak-20",  # TCL 55" QLED 4K
            "walmart_url": "https://www.walmart.com/ip/741852963"
        },
        "vacuum cleaner": {
            "price": 249.99,
            "rating": 4.6,
            "reviews": ["Powerful suction", "Heavy", "Cleans like a dream"],
            "amazon_url": "https://www.amazon.com/dp/B09NBFVB3S?tag=bshoemak-20",  # Shark NV360 Navigator
            "walmart_url": "https://www.walmart.com/ip/852963741"
        },
        "air fryer": {
            "price": 89.99,
            "rating": 4.5,
            "reviews": ["Crispy food", "Small capacity", "Easy to clean"],
            "amazon_url": "https://www.amazon.com/dp/B07FDJMC9Q?tag=bshoemak-20",  # Ninja AF101
            "walmart_url": "https://www.walmart.com/ip/963741852"
        },
        "blender": {
            "price": 59.99,
            "rating": 4.3,
            "reviews": ["Blends smoothly", "Loud", "Compact design"],
            "amazon_url": "https://www.amazon.com/dp/B014LY7PJQ?tag=bshoemak-20",  # NutriBullet 600W
            "walmart_url": "https://www.walmart.com/ip/147852369"
        },
        "microwave": {
            "price": 119.99,
            "rating": 4.4,
            "reviews": ["Heats evenly", "Buttons wear out", "Good size"],
            "amazon_url": "https://www.amazon.com/dp/B07P5W8Z3P?tag=bshoemak-20",  # Toshiba 1.2 Cu Ft
            "walmart_url": "https://www.walmart.com/ip/258963741"
        },
        "electric kettle": {
            "price": 39.99,
            "rating": 4.5,
            "reviews": ["Boils fast", "Plastic smell", "Stylish"],
            "amazon_url": "https://www.amazon.com/dp/B07SHFZS47?tag=bshoemak-20",  # COSORI 1.7L
            "walmart_url": "https://www.walmart.com/ip/369741852"
        },
        "running shoes": {
            "price": 89.99,
            "rating": 4.6,
            "reviews": ["Super comfortable", "Wear out quickly", "Great support"],
            "amazon_url": "https://www.amazon.com/dp/B09XJLXJL5?tag=bshoemak-20",  # Brooks Ghost 15
            "walmart_url": "https://www.walmart.com/ip/741963852"
        },
        "backpack": {
            "price": 49.99,
            "rating": 4.7,
            "reviews": ["Lots of pockets", "Straps dig in", "Durable"],
            "amazon_url": "https://www.amazon.com/dp/B07FXLGG85?tag=bshoemak-20",  # Matein Travel Backpack
            "walmart_url": "https://www.walmart.com/ip/852741963"
        },
        "sunglasses": {
            "price": 24.99,
            "rating": 4.4,
            "reviews": ["Stylish look", "Fragile", "Good UV protection"],
            "amazon_url": "https://www.amazon.com/dp/B073XJ2M63?tag=bshoemak-20",  # SOJOS Classic Aviator
            "walmart_url": "https://www.walmart.com/ip/963852741"
        },
        "yoga mat": {
            "price": 29.99,
            "rating": 4.5,
            "reviews": ["Non-slip", "Thin padding", "Easy to carry"],
            "amazon_url": "https://www.amazon.com/dp/B07G5QJ2N8?tag=bshoemak-20",  # Gaiam Essentials
            "walmart_url": "https://www.walmart.com/ip/147963852"
        },
        "desk lamp": {
            "price": 34.99,
            "rating": 4.6,
            "reviews": ["Bright light", "Flickers sometimes", "Adjustable"],
            "amazon_url": "https://www.amazon.com/dp/B08D9C2Z2Q?tag=bshoemak-20",  # LED Desk Lamp
            "walmart_url": "https://www.walmart.com/ip/258741963"
        },
        "water bottle": {
            "price": 19.99,
            "rating": 4.7,
            "reviews": ["Keeps water cold", "Leaks if tipped", "Perfect size"],
            "amazon_url": "https://www.amazon.com/dp/B08C7XJ2L5?tag=bshoemak-20",  # Hydro Flask 32 oz
            "walmart_url": "https://www.walmart.com/ip/369852741"
        },
        "cookware set": {
            "price": 129.99,
            "rating": 4.5,
            "reviews": ["Non-stick", "Handles get hot", "Great quality"],
            "amazon_url": "https://www.amazon.com/dp/B07GGM7K2M?tag=bshoemak-20",  # T-fal 12-Piece Set
            "walmart_url": "https://www.walmart.com/ip/741258963"
        },
        "board game": {
            "price": 39.99,
            "rating": 4.8,
            "reviews": ["Fun for all ages", "Rules confusing", "Replayable"],
            "amazon_url": "https://www.amazon.com/dp/B00U26V4VQ?tag=bshoemak-20",  # Ticket to Ride
            "walmart_url": "https://www.walmart.com/ip/852369741"
        },
        "pet bed": {
            "price": 29.99,
            "rating": 4.6,
            "reviews": ["Dogs love it", "Filling shifts", "Soft material"],
            "amazon_url": "https://www.amazon.com/dp/B07N1W5W8H?tag=bshoemak-20",  # Furhaven Pet Bed
            "walmart_url": "https://www.walmart.com/ip/963147852"
        },
        "power bank": {
            "price": 24.99,
            "rating": 4.5,
            "reviews": ["Charges fast", "Bulky", "Reliable"],
            "amazon_url": "https://www.amazon.com/dp/B07CZPZ7QJ?tag=bshoemak-20",  # Anker PowerCore 10000
            "walmart_url": "https://www.walmart.com/ip/147369852"
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
                    "walmart_url": product.get("walmart_url", "#")
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
    app.run(debug=True, host='0.0.0.0', port=5000)