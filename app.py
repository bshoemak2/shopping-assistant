from flask import Flask, render_template, request, jsonify
import sqlite3
import requests
from bs4 import BeautifulSoup
import random
import time
import logging
import sys

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Set up logging to print to console
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

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

product_taglines = {
    "rubber-chicken-purse": "Cluck your way to style!",
    "skeleton-onesie": "Glow spooky, sleep cozy!",
    "burrito-blanket": "Wrap up in taco-tastic glory!",
    "screaming-goat-button": "Baa-ffle your coworkers!",
    "inflatable-tube-man": "Wave away the boring desk vibes!",
    "fake-poop": "For when you want to stink up their day!",
    "toilet-bowl-night-light": "Light up your late-night potty trips!",
    "zombie-garden-gnome": "Creep out your lawn in style!",
    "cat-butt-magnets": "Stick some cheeky charm on your fridge!",
    "wooden-clothes-pins": "Pinch chips or bad vibes!",
    "fart-whistles": "Toot your way to laughs!",
    "bear-claw-pencils": "Write with grizzly flair!",
    "expresso-cups": "Sip from poo-colored perfection!",
    "unicorn-meat": "Mythical munchies for emergencies!",
    "bacon-bandages": "Heal with the power of pork!",
    "bird-feeder": "Feed ‘em upside-down for giggles!",
    "mini-disco-ball": "Party vibes, desk-sized!",
    "dinosaur-taco-holder": "Chomp tacos like a T-Rex!",
    "singing-pasta-timer": "Cook pasta with a serenade!",
    "toaster-grilled-cheese-bags": "Say goodbye to burnt bread!",
    "unicorn-pool-float": "Float like a magical beast!",
    "giant-googly-eyes": "Stick ‘em anywhere for instant chaos!",
    "inflatable-turkey": "Gobble up the Thanksgiving laughs!",
    "singing-fish-plaque": "Your wall’s new karaoke star!",
    "potato-chip-grabber": "Keep your fingers chip-free!",
    "finger-hands": "Tiny hands, big laughs!",
    "banana-phone": "Make calls with fruity flair!",
    "squishy-stress-poop": "Squeeze away your worries!",
    "storm-pooper-decal": "May the farce be with you!",
    "silly-string-shooter": "Spray chaos everywhere!",
    "prank-pregnancy-test": "Shock ‘em with a positive surprise!",
    "invisible-ink-pen": "Write secrets that vanish!",
    "shock-pen": "Zap ‘em with every click!",
    "prank-spider": "Scare ‘em silly with a fake tarantula!",
    "exploding-golf-balls": "Tee off with a bang!",
    "fake-parking-ticket": "Fool ‘em with a fake fine!",
    "squirting-flower-lapel": "Classic clown prank, water style!",
    "itching-powder": "Sneaky scratch for sneaky laughs!",
    "fake-lottery-tickets": "Win big... not really!",
    "prank-hand-buzzer": "Shock ‘em with a handshake!",
    "disappearing-ink": "Spill it, watch it vanish!",
    "fake-cockroach": "Scream-worthy bug for pranks!",
    "banana-bandages": "Heal with a fruity flair!",
    "pineapple-bandages": "Tropical healing fun!",
    "fart-spray": "Stink up the room in style!"
}

def migrate_db():
    conn = None
    try:
        conn = sqlite3.connect('subscribers.db')
        c = conn.cursor()
        c.execute("PRAGMA table_info(reviews)")
        columns = [col[1] for col in c.fetchall()]
        if 'date' not in columns:
            logger.info("Adding date column to reviews table")
            c.execute("ALTER TABLE reviews ADD COLUMN date TEXT")
            c.execute("UPDATE reviews SET date = '2025-05-01' WHERE date IS NULL")
            conn.commit()
            logger.info("Date column added successfully")
        else:
            logger.info("Date column already exists in reviews table")
    except Exception as e:
        logger.error(f"Error migrating database: {e}")
    finally:
        if conn:
            conn.close()

def init_db():
    conn = None
    try:
        conn = sqlite3.connect('subscribers.db')
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS giggle_scores (product_id TEXT UNIQUE, score INTEGER)')
        c.execute('CREATE TABLE IF NOT EXISTS reviews (text TEXT, author TEXT, date TEXT)')
        c.execute('CREATE TABLE IF NOT EXISTS subscribers (email TEXT UNIQUE)')
        conn.commit()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
    finally:
        if conn:
            conn.close()

def add_taglines(product_list):
    return [{**p, 'tagline': product_taglines.get(p['id'], 'Get ready to prank!')} for p in product_list]

# Run migration on startup
migrate_db()

@app.route('/')
def home():
    logger.debug("Entering home() function")
    
    current_month = time.localtime().tm_mon
    seasonal_map = {4: "april-fools", 10: "halloween", 11: "thanksgiving"}
    current_season = seasonal_map.get(current_month, None)
    seasonal_highlights = [p for p in products if p.get('seasonal') == current_season][:3] if current_season else []

    top_picks = sorted(products, key=lambda x: x['score'], reverse=True)[:5]
    fan_favorites = [p for p in products if p['id'] in ['unicorn-meat', 'burrito-blanket', 'screaming-goat-button']]

    giggle_scores = {}
    reviews = []

    conn = None
    try:
        logger.debug("Connecting to database")
        conn = sqlite3.connect('subscribers.db')
        c = conn.cursor()
        c.execute('SELECT product_id, score FROM giggle_scores')
        giggle_scores = dict(c.fetchall())
        logger.debug(f"Loaded giggle_scores: {giggle_scores}")
        try:
            c.execute('SELECT text, author, date FROM reviews')
            reviews = [{'text': row[0], 'author': row[1], 'date': row[2] or '2025-05-01'} for row in c.fetchall()]
        except sqlite3.OperationalError:
            logger.warning("Date column missing, falling back to text and author only")
            c.execute('SELECT text, author FROM reviews')
            reviews = [{'text': row[0], 'author': row[1], 'date': '2025-05-01'} for row in c.fetchall()]
        logger.debug(f"Loaded {len(reviews)} reviews")
    except Exception as e:
        logger.error(f"Database error in home(): {e}", exc_info=True)
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed")

    logger.debug(f"Rendering template with giggle_scores: {giggle_scores}")
    return render_template('home.html',
                           seasonal_highlights=add_taglines(seasonal_highlights),
                           top_picks=add_taglines(top_picks),
                           fan_favorites=add_taglines(fan_favorites),
                           reviews=reviews,
                           giggle_scores=giggle_scores)

@app.route('/shop', methods=['GET', 'POST'])
def shop():
    query = request.form.get('query', '').lower() if request.method == 'POST' else ''
    category = request.form.get('category', '') if request.method == 'POST' else ''
    filtered_products = [p for p in products if (query in p['name'].lower() or not query) and (p['category_id'] == category or not category)]
    
    giggle_scores = {}
    conn = None
    try:
        conn = sqlite3.connect('subscribers.db')
        c = conn.cursor()
        c.execute('SELECT product_id, score FROM giggle_scores')
        giggle_scores = dict(c.fetchall())
    except Exception as e:
        logger.error(f"Database error in shop(): {e}", exc_info=True)
    finally:
        if conn:
            conn.close()

    return render_template('shop.html', all_products=add_taglines(filtered_products), giggle_scores=giggle_scores)

@app.route('/reviews')
def reviews():
    reviews = []
    conn = None
    try:
        conn = sqlite3.connect('subscribers.db')
        c = conn.cursor()
        try:
            c.execute('SELECT text, author, date FROM reviews')
            reviews = [{'text': row[0], 'author': row[1], 'date': row[2] or '2025-05-01'} for row in c.fetchall()]
        except sqlite3.OperationalError:
            logger.warning("Date column missing, falling back to text and author only")
            c.execute('SELECT text, author FROM reviews')
            reviews = [{'text': row[0], 'author': row[1], 'date': '2025-05-01'} for row in c.fetchall()]
    except Exception as e:
        logger.error(f"Database error in reviews(): {e}", exc_info=True)
    finally:
        if conn:
            conn.close()
    return render_template('reviews.html', reviews=reviews)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/subscribe')
def subscribe_page():
    return render_template('subscribe.html')

@app.route('/videos')
def videos():
    return render_template('videos.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email')
    if not email:
        logger.error("No email provided")
        return jsonify({'message': 'Email required!'}), 400
    
    conn = None
    try:
        logger.debug(f"Subscribing email: {email}")
        conn = sqlite3.connect('subscribers.db')
        c = conn.cursor()
        c.execute('INSERT INTO subscribers (email) VALUES (?)', (email,))
        conn.commit()
        success_html = """
        <div style="background-color: #e6ffe6; padding: 15px; border-radius: 5px; text-align: center;">
            <h3 style="color: #28a745; margin: 0;">🎉 You’re In on the Prank Party!</h3>
            <p style="color: #333;">Welcome, <strong>{email}</strong>! Get ready for some epic shenanigans.</p>
            <a href="/" style="display: inline-block; padding: 8px 16px; background-color: #28a745; color: white; text-decoration: none; border-radius: 5px;">Back to Home</a>
        </div>
        """.format(email=email)
        return success_html, 200
    except sqlite3.IntegrityError:
        logger.warning(f"Email already subscribed: {email}")
        return jsonify({'message': 'Email already subscribed!'}), 400
    except Exception as e:
        logger.error(f"Error in subscribe: {e}", exc_info=True)
        return jsonify({'message': 'Database error occurred!'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/giggle_vote', methods=['POST'])
def giggle_vote():
    product_id = request.form.get('product_id')
    if not product_id:
        logger.error("No product_id provided in giggle_vote")
        return jsonify({'success': False, 'error': 'No product_id provided'}), 400
    
    conn = None
    try:
        logger.debug(f"Recording giggle vote for {product_id}")
        conn = sqlite3.connect('subscribers.db')
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO giggle_scores (product_id, score) VALUES (?, COALESCE((SELECT score FROM giggle_scores WHERE product_id = ?) + 1, 1))', (product_id, product_id))
        conn.commit()
        c.execute('SELECT score FROM giggle_scores WHERE product_id = ?', (product_id,))
        new_score = c.fetchone()[0]
        logger.debug(f"Giggle vote recorded for {product_id}: {new_score}")
        return jsonify({'success': True, 'new_score': new_score})
    except Exception as e:
        logger.error(f"Error in giggle_vote: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/find', methods=['POST'])
def find():
    data = request.get_json()
    products = data.get('products', [])
    comparisons = {}
    try:
        logger.debug(f"Searching for products: {products}")
        for product in products:
            url = f"https://www.amazon.com/s?k={product.replace(' ', '+')}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                logger.error(f"Amazon search failed for {product}: Status {response.status_code}")
                continue
            soup = BeautifulSoup(response.content, 'html.parser')
            item = soup.select_one('.s-result-item')
            if item:
                price = item.select_one('.a-price .a-offscreen')
                price = float(price.text.replace('$', '')) if price else 0.0
                rating = item.select_one('.a-icon-alt')
                rating = float(rating.text.split()[0]) if rating else 0.0
                comparisons[product] = {
                    'price': price,
                    'rating': rating,
                    'review_summary': {'positive': 'Good', 'negative': 'None', 'sentiment_score': 0.5, 'keywords': ['fun']},
                    'amazon_url': url,
                    'is_search_page': True
                }
        logger.debug(f"Search results: {comparisons}")
    except Exception as e:
        logger.error(f"Error in find: {e}", exc_info=True)
        return jsonify({'error': 'Search failed'}), 500
    return jsonify({'comparisons': comparisons})

@app.route('/submit_review', methods=['POST'])
def submit_review():
    data = request.get_json()
    review_text = data.get('text')
    author = data.get('author', 'Anonymous Prankster')
    date = time.strftime('%Y-%m-%d')
    if not review_text:
        logger.error("No review text provided")
        return jsonify({'message': 'Review text required!'}), 400
    
    conn = None
    try:
        logger.debug(f"Submitting review: {review_text} by {author} on {date}")
        conn = sqlite3.connect('subscribers.db')
        c = conn.cursor()
        c.execute('INSERT INTO reviews (text, author, date) VALUES (?, ?, ?)', (review_text, author, date))
        conn.commit()
        logger.info(f"Review submitted successfully: {review_text}")
        return jsonify({'message': 'Review submitted successfully!'}), 200
    except Exception as e:
        logger.error(f"Error in submit_review: {e}", exc_info=True)
        return jsonify({'message': f'Failed to submit review: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    logger.info("Starting Flask app")
    init_db()
    app.run(debug=True)