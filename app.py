from flask import Flask, render_template, request, jsonify
import sqlite3
import requests
from bs4 import BeautifulSoup
import random
import time

app = Flask(__name__)

products = [
    {"name": "Rubber Chicken Purse - Cluck in Style", "url": "https://amzn.to/4hAMdL5", "image": "https://m.media-amazon.com/images/I/61eiIozbjeL._AC_SY625_.jpg", "id": "rubber-chicken-purse", "score": 8, "category_id": "wearable-pranks"},
    {"name": "Glow-in-the-Dark Skeleton Onesie - Spooky Pajamas", "url": "https://amzn.to/4iQ1Pvh", "image": "https://m.media-amazon.com/images/I/71aihrZ+zKL._AC_SY606_.jpg", "id": "skeleton-onesie", "score": 8, "category_id": "wearable-pranks", "seasonal": "halloween"},
    {"name": "Burrito Blanket - Wrap Yourself in Taco Glory", "url": "https://amzn.to/4ixPvAa", "image": "https://m.media-amazon.com/images/I/71yR0457iSL.__AC_SX300_SY300_QL70_FMwebp_.jpg", "id": "burrito-blanket", "score": 9, "category_id": "wearable-pranks"},
    {"name": "Screaming Goat Button - Instant Stress Relief", "url": "https://amzn.to/4l56Diq", "image": "https://m.media-amazon.com/images/I/61FEGW9sarL._AC_SY355_.jpg", "id": "screaming-goat-button", "score": 8, "category_id": "desk-disasters"},
    {"name": "Inflatable Tube Man - Mini Desktop Wacky Waving Guy", "url": "https://amzn.to/4bSGxLj", "image": "https://m.media-amazon.com/images/I/71xmJjfakxL._SY342_.jpg", "id": "inflatable-tube-man", "score": 7, "category_id": "desk-disasters"},
    {"name": "Fake Poop - Prank Your Friends", "url": "https://amzn.to/4hEoA4v", "image": "https://m.media-amazon.com/images/I/91PrQPk4FyL._AC_SY355_.jpg", "id": "fake-poop", "score": 8, "category_id": "desk-disasters"},
    {"name": "Toilet Bowl Night Light - Glow-in-the-Dark Potty Guide", "url": "https://amzn.to/4hF36V4", "image": "https://m.media-amazon.com/images/I/61SFGMaxFnL._AC_SX522_PIbundle-2,TopRight,0,0_SH20_.jpg", "id": "toilet-bowl-night-light", "score": 8, "category_id": "home-hilarity"},
    {"name": "Zombie Garden Gnome - Undead Lawn Vibes", "url": "https://amzn.to/4ipnOJH", "image": "https://m.media-amazon.com/images/I/71mviXHjQgS._AC_SX425_.jpg", "id": "zombie-garden-gnome", "score": 7, "category_id": "home-hilarity", "seasonal": "halloween"},
    {"name": "Cat Butt Magnets - Fridge Decoration Gone Wild", "url": "https://amzn.to/4iUjSQZ", "image": "https://m.media-amazon.com/images/I/71CROrMofmL._AC_SX425_.jpg", "id": "cat-butt-magnets", "score": 7, "category_id": "home-hilarity"},
    {"name": "Wooden Clothes Pins for Sealing Potato Chip Bags and Pinching People with Bad Mojo", "url": "https://amzn.to/4hBxujc", "image": "https://m.media-amazon.com/images/I/61uIdPamR6L._AC_SX425_.jpg", "id": "wooden-clothes-pins", "score": 7, "category_id": "all-products"},
    {"name": "Fart Whistles, Loads of Fun", "url": "https://amzn.to/4kQ39A7", "image": "https://m.media-amazon.com/images/I/51QxdnNilYL.__AC_SX300_SY300_QL70_FMwebp_.jpg", "id": "fart-whistles", "score": 9, "category_id": "all-products"},
    {"name": "Bear Claw Pencils, The Only Pencil You Ever Need", "url": "https://amzn.to/4kRem3n", "image": "https://m.media-amazon.com/images/I/71X1uUeYU2L._AC_SX425_.jpg", "id": "bear-claw-pencils", "score": 6, "category_id": "all-products"},
    {"name": "Expresso Cups in Poo Colors", "url": "https://amzn.to/4kVaBtW", "image": "https://m.media-amazon.com/images/I/71GUx8MpJWL._AC_SX425_.jpg", "id": "expresso-cups", "score": 8, "category_id": "all-products"},
    {"name": "Unicorn Meat (Canned) - Emergency Snack for Mythical Cravings", "url": "https://amzn.to/4iTYRG5", "image": "https://m.media-amazon.com/images/I/91Ve0ydEERL._AC_SY450_.jpg", "id": "unicorn-meat", "score": 10, "category_id": "all-products"},
    {"name": "Bacon Bandages - Heal with Pork Power", "url": "https://amzn.to/4bWHClp", "image": "https://m.media-amazon.com/images/I/81KgbHqXyeL._AC_SY450_.jpg", "id": "bacon-bandages", "score": 6, "category_id": "all-products"},
    {"name": "Bird Feeder - Watch Them Hang Upside Down", "url": "https://amzn.to/4ixKqYC", "image": "https://m.media-amazon.com/images/I/719qCXCgbpL._AC_SX425_.jpg", "id": "bird-feeder", "score": 7, "category_id": "all-products"},
    {"name": "Mini Disco Ball - Instant Party Vibes", "url": "https://amzn.to/4bZsWC2", "image": "https://m.media-amazon.com/images/I/81p24UOT9dL._AC_SX522_.jpg", "id": "mini-disco-ball", "score": 9, "category_id": "all-products"},
    {"name": "Dinosaur Taco Holder - Prehistoric Dining", "url": "https://amzn.to/4kVwlWw", "image": "https://m.media-amazon.com/images/I/51FFY2fXBqL._AC_SX425_.jpg", "id": "dinosaur-taco-holder", "score": 9, "category_id": "all-products"},
    {"name": "Singing Pasta Timer - Croons While You Cook", "url": "https://amzn.to/4hx9r4M", "image": "https://m.media-amazon.com/images/I/411B+NTv+nL._AC_SX425_.jpg", "id": "singing-pasta-timer", "score": 8, "category_id": "all-products"},
    {"name": "Toaster Grilled Cheese Bags - Burnt Bread Begone", "url": "https://amzn.to/4bZyeNU", "image": "https://m.media-amazon.com/images/I/61owFWwQFPL._AC_SX425_.jpg", "id": "toaster-grilled-cheese-bags", "score": 7, "category_id": "all-products"},
    {"name": "Unicorn Pool Float - Float Like a Mythical Beast", "url": "https://amzn.to/41S2SUK", "image": "https://m.media-amazon.com/images/I/618RJXWFfnL._AC_SX355_.jpg", "id": "unicorn-pool-float", "score": 9, "category_id": "all-products"},
    {"name": "Giant Googly Eyes - Stick Them Anywhere for Instant Chaos", "url": "https://amzn.to/4i5b2PL", "image": "https://m.media-amazon.com/images/I/71rS6vz+spL._AC_SY450_.jpg", "id": "giant-googly-eyes", "score": 8, "category_id": "all-products"},
    {"name": "Inflatable Turkey - Thanksgiving Prank Ready", "url": "https://amzn.to/3DV7tNV", "image": "https://m.media-amazon.com/images/I/71nUz2u5CkL._AC_SX355_.jpg", "id": "inflatable-turkey", "score": 7, "category_id": "all-products", "seasonal": "thanksgiving"},
    {"name": "Singing Fish Plaque - Wall-Mounted Karaoke Star", "url": "https://amzn.to/3FIVhAv", "image": "https://m.media-amazon.com/images/I/612hK94HC7L._AC_SY355_.jpg", "id": "singing-fish-plaque", "score": 9, "category_id": "all-products"},
    {"name": "Potato Chip Grabber - Keep Your Fingers Clean", "url": "https://amzn.to/3DHPsTg", "image": "https://m.media-amazon.com/images/I/51TTLEJ+msS._AC_SX450_.jpg", "id": "potato-chip-grabber", "score": 6, "category_id": "all-products"},
    {"name": "Finger Hands - Tiny Hands for Your Fingers", "url": "https://amzn.to/4j498Qe", "image": "https://m.media-amazon.com/images/I/81yTHIedbdS._AC_SY355_.jpg", "id": "finger-hands", "score": 8, "category_id": "all-products"},
    {"name": "Banana Phone - Make Calls with a Fruit", "url": "https://amzn.to/4iFZWl4", "image": "https://m.media-amazon.com/images/I/51u7vtBZNYL._AC_SX679_.jpg", "id": "banana-phone", "score": 8, "category_id": "all-products"},
    {"name": "Squishy Stress Poop - Squeeze Away Your Worries", "url": "https://amzn.to/3XYJrby", "image": "https://m.media-amazon.com/images/I/31AaP2nasYL._AC_SX355_.jpg", "id": "squishy-stress-poop", "score": 7, "category_id": "all-products"},
    {"name": "Stormtrooper Inspired Storm Pooper Parody Vinyl Decal", "url": "https://amzn.to/4c8lggL", "image": "https://m.media-amazon.com/images/I/713feRDA2GL._AC_SX425_.jpg", "id": "storm-pooper-decal", "score": 8, "category_id": "all-products"},
    {"name": "Silly String Shooter - Spray Chaos Everywhere", "url": "https://amzn.to/4l41QNZ", "image": "https://m.media-amazon.com/images/I/81IikTQycAL._AC_SY355_.jpg", "id": "silly-string-shooter", "score": 9, "category_id": "all-products"},
    {"name": "Prank Pregnancy Test - Always Positive for Maximum Shock", "url": "https://amzn.to/3FGAspn", "image": "https://m.media-amazon.com/images/I/71p43VT8P3L._AC_SY450_.jpg", "id": "prank-pregnancy-test", "score": 9, "category_id": "all-products", "seasonal": "april-fools"},
    {"name": "Invisible Ink Pen - Write Secret Messages That Disappear", "url": "https://amzn.to/3DXswiK", "image": "https://m.media-amazon.com/images/I/81ChKmEdHrL._AC_SX355_.jpg", "id": "invisible-ink-pen", "score": 7, "category_id": "all-products"},
    {"name": "Shock Pen - Give a Jolt with Every Click", "url": "https://amzn.to/428bSFk", "image": "https://m.media-amazon.com/images/I/61C472C3EvL._AC_SY355_.jpg", "id": "shock-pen", "score": 8, "category_id": "all-products"},
    {"name": "Prank Spider - Realistic Tarantula to Scare Everyone", "url": "https://amzn.to/422vPgz", "image": "https://m.media-amazon.com/images/I/812Q16keLLL._AC_SX466_.jpg", "id": "prank-spider", "score": 9, "category_id": "all-products", "seasonal": "halloween"},
    {"name": "Exploding Golf Balls - Tee Off with a Bang", "url": "https://amzn.to/43pmDFx", "image": "https://m.media-amazon.com/images/I/9192btAkakL._AC_SY450_.jpg", "id": "exploding-golf-balls", "score": 7, "category_id": "all-products"},
    {"name": "Fake Parking Ticket - Fool Your Friends with a Fine", "url": "https://amzn.to/4hTpNVw", "image": "https://m.media-amazon.com/images/I/81T+xOqOfoL._AC_SY355_.jpg", "id": "fake-parking-ticket", "score": 8, "category_id": "all-products"},
    {"name": "Squirting Flower Lapel - Classic Clown Prank", "url": "https://amzn.to/4j6rIac", "image": "https://m.media-amazon.com/images/I/41czfTBHxoL._AC_.jpg", "id": "squirting-flower-lapel", "score": 7, "category_id": "all-products"},
    {"name": "Itching Powder - Sneaky Prank for a Good Scratch", "url": "https://amzn.to/4iJLVCT", "image": "https://m.media-amazon.com/images/I/51NRqanqZsL._AC_SY355_.jpg", "id": "itching-powder", "score": 7, "category_id": "all-products"},
    {"name": "Fake Lottery Tickets - Win Big (Not Really!)", "url": "https://amzn.to/42c21yp", "image": "https://m.media-amazon.com/images/I/810O2ezzcRL._AC_SX355_.jpg", "id": "fake-lottery-tickets", "score": 9, "category_id": "all-products"},
    {"name": "Prank Hand Buzzer - Shake Hands, Get a Shock", "url": "https://amzn.to/4ccTsrA", "image": "https://m.media-amazon.com/images/I/61N30-9dOgL._AC_SY355_.jpg", "id": "prank-hand-buzzer", "score": 8, "category_id": "all-products"},
    {"name": "Disappearing Ink - Spill It, Watch It Vanish", "url": "https://amzn.to/43uODHN", "image": "https://m.media-amazon.com/images/I/719l-Vo5ajL._AC_SY355_.jpg", "id": "disappearing-ink", "score": 7, "category_id": "all-products"},
    {"name": "Fake Cockroach - Realistic Bug for a Screaming Good Time", "url": "https://amzn.to/3RoizxW", "image": "https://m.media-amazon.com/images/I/71Be0N71mBL._AC_SY355_.jpg", "id": "fake-cockroach", "score": 8, "category_id": "all-products", "seasonal": "halloween"},
    {"name": "Banana Bandages - Heal with Fruit Flair", "url": "https://amzn.to/426U6SO", "image": "https://m.media-amazon.com/images/I/81o05QPkfEL._AC_SX679_.jpg", "id": "banana-bandages", "score": 7, "category_id": "all-products"},
    {"name": "Pineapple Bandages - Tropical Healing Fun", "url": "https://amzn.to/3Y7Ptqg", "image": "https://m.media-amazon.com/images/I/91flowprqVL._AC_SY450_.jpg", "id": "pineapple-bandages", "score": 7, "category_id": "all-products"},
    {"name": "Fart Spray - Stink Up the Room", "url": "https://amzn.to/4hQyAr9", "image": "https://m.media-amazon.com/images/I/91l3YStar6L._AC_SY355_.jpg", "id": "fart-spray", "score": 8, "category_id": "all-products"},
]

@app.route('/')
def home():
    current_month = time.localtime().tm_mon
    seasonal_map = {
        4: "april-fools",
        10: "halloween",
        11: "thanksgiving"
    }
    current_season = seasonal_map.get(current_month, None)
    seasonal_highlights = [p for p in products if p.get('seasonal') == current_season] if current_season else []

    wearable_pranks = [p for p in products if p['category_id'] == 'wearable-pranks']
    desk_disasters = [p for p in products if p['category_id'] == 'desk-disasters']
    home_hilarity = [p for p in products if p['category_id'] == 'home-hilarity']
    all_products = products
    popular_picks = [p for p in products if p['id'] in ['bacon-bandages', 'banana-bandages', 'pineapple-bandages']]
    
    conn = sqlite3.connect('subscribers.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS reviews (text TEXT, author TEXT)')
    c.execute('SELECT text, author FROM reviews')
    reviews = [{'text': row[0], 'author': row[1]} for row in c.fetchall()]
    c.execute('CREATE TABLE IF NOT EXISTS mystery_reveals (date TEXT, product_id TEXT)')
    today = time.strftime('%Y-%m-%d')
    c.execute('SELECT product_id FROM mystery_reveals WHERE date = ?', (today,))
    mystery_result = c.fetchone()
    if mystery_result:
        mystery_product = next((p for p in products if p['id'] == mystery_result[0]), None)
    else:
        mystery_product = random.choice(products)
        c.execute('INSERT INTO mystery_reveals (date, product_id) VALUES (?, ?)', (today, mystery_product['id']))
        conn.commit()
    conn.close()
    
    return render_template('home.html', 
                           seasonal_highlights=seasonal_highlights,
                           wearable_pranks=wearable_pranks, 
                           desk_disasters=desk_disasters, 
                           home_hilarity=home_hilarity, 
                           all_products=all_products,
                           popular_picks=popular_picks,
                           reviews=reviews,
                           mystery_product=mystery_product)

@app.route('/find', methods=['POST'])
def find():
    data = request.get_json()
    products = data.get('products', [])
    comparisons = {}
    for product in products:
        url = f"https://www.amazon.com/s?k={product.replace(' ', '+')}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            item = soup.select_one('.s-result-item')
            if item:
                price = item.select_one('.a-price .a-offscreen')
                price = float(price.text.replace('$', '')) if price else 0.0
                rating = item.select_one('.a-icon-alt')
                rating = float(rating.text.split()[0]) if rating else 0.0
                reviews = ["Sample review"]
                comparisons[product] = {
                    'price': price,
                    'rating': rating,
                    'review_summary': {'positive': 'Good', 'negative': 'None', 'sentiment_score': 0.5, 'keywords': ['fun']},
                    'amazon_url': url,
                    'is_search_page': True
                }
    return jsonify({'comparisons': comparisons})

@app.route('/submit_review', methods=['POST'])
def submit_review():
    data = request.get_json()
    review_text = data.get('text')
    author = data.get('author', 'Anonymous Prankster')
    if review_text:
        conn = sqlite3.connect('subscribers.db')
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS reviews (text TEXT, author TEXT)')
        c.execute('INSERT INTO reviews (text, author) VALUES (?, ?)', (review_text, author))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Review submitted successfully!'}), 200
    return jsonify({'message': 'Review text required!'}), 400

@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email')
    if email:
        conn = sqlite3.connect('subscribers.db')
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS subscribers (email TEXT UNIQUE)')
        try:
            c.execute('INSERT INTO subscribers (email) VALUES (?)', (email,))
            conn.commit()
            return jsonify({'message': 'Subscribed successfully!'}), 200
        except sqlite3.IntegrityError:
            return jsonify({'message': 'Email already subscribed!'}), 400
        finally:
            conn.close()
    return jsonify({'message': 'Email required!'}), 400

if __name__ == '__main__':
    app.run(debug=True)