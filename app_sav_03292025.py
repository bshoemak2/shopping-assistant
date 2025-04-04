# Trigger redeploy to fix SSL issue - March 2025
from flask import Flask, request, jsonify, render_template, redirect, url_for
import logging
from datetime import datetime
import sqlite3
import os
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
logging.basicConfig(filename='app.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s')

app.static_folder = 'static'

# Configure Flask-Mail with environment variables and new app-specific password
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'bshoemak2@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'vzug hygx grwt frkn')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME', 'bshoemak2@gmail.com')

mail = Mail(app)

# Initialize SQLite database for email storage
def init_db():
    conn = sqlite3.connect('emails.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS subscribers
                 (email TEXT PRIMARY KEY, signup_date TEXT)''')
    conn.commit()
    conn.close()

init_db()

def fetch_amazon_products(product_names):
    # Updated mock API response to match searchable products in home.html
    mock_api_response = {
        "laptop": {
            "price": 999.99,
            "rating": 4.5,
            "reviews": ["Fast performance", "Battery could be better", "Great for work"],
            "amazon_url": "https://amzn.to/4kVu4dW",
            "is_search_page": False
        },
        "yoga mat": {
            "price": 29.99,
            "rating": 4.5,
            "reviews": ["Non-slip", "Thin padding", "Easy to carry"],
            "amazon_url": "https://amzn.to/41SGXN5",
            "is_search_page": False
        },
        "beef tallow": {
            "price": 19.99,
            "rating": 4.3,
            "reviews": ["Great for cooking", "Strong smell", "Good quality"],
            "amazon_url": "https://amzn.to/41WPu1H",
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

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/blog/<post_slug>')
def blog_post(post_slug):
    # Mock blog posts for SEO with quirky long-tail keywords
    blog_posts = {
        "best-gag-gift-for-brothers-wedding": {
            "title": "The Best Gag Gift for Your Brother’s Wedding (He’ll Laugh, She’ll Cringe!)",
            "meta_description": "Need the best gag gift for your brother’s wedding? Check out these hilarious Amazon finds that’ll make him laugh!",
            "content": """
                <h2>Make His Big Day Hilarious!</h2>
                <p>Weddings are all about love, but who says you can’t add a little laughter? Here are our top picks for gag gifts that’ll have your brother (and the groomsmen) in stitches.</p>
                <ul>
                    <li><strong>Fart Whistles:</strong> Slip this under his chair for a reception surprise! <a href="https://amzn.to/4kQ39A7" target="_blank">Get it on Amazon</a>.</li>
                    <li><strong>Expresso Cups in Poo Colors:</strong> Wrap his real gift in this for a laugh. <a href="https://amzn.to/4kVaBtW" target="_blank">Shop now</a>.</li>
                </ul>
                <p>Check out more funny ideas on our <a href="/">homepage</a>!</p>
            """
        },
        "funny-office-prank-ideas": {
            "title": "Funny Office Prank Ideas to Make Your Boss LOL—Top Amazon Picks",
            "meta_description": "Looking for funny office prank ideas? These Amazon prank products will have your coworkers laughing this April Fools’ Day!",
            "content": """
                <h2>Prank Your Way to Office Legend Status!</h2>
                <p>April Fools’ Day is coming, and it’s time to bring some humor to the office. Here are our favorite prank ideas and products to pull them off.</p>
                <ul>
                    <li><strong>Fake Poop:</strong> Place this on your boss’s desk for a scream-worthy moment! <a href="https://amzn.to/4hEoA4v" target="_blank">Get it on Amazon</a>.</li>
                    <li><strong>Fart Whistles:</strong> A classic that never fails. <a href="https://amzn.to/4kQ39A7" target="_blank">Shop now</a>.</li>
                </ul>
                <p>Want more ideas? Visit our <a href="/">homepage</a> for more funny products!</p>
            """
        }
    }
    post = blog_posts.get(post_slug, None)
    if not post:
        return render_template('404.html'), 404
    return render_template('blog_post.html', post=post)

@app.route('/subscribe', methods=['POST'])
def subscribe():
    try:
        email = request.form.get('email')
        if not email:
            logging.error("No email provided in subscription request")
            return jsonify({"error": "Email is required"}), 400
        
        # Store email in SQLite database
        conn = sqlite3.connect('emails.db')
        c = conn.cursor()
        c.execute("INSERT INTO subscribers (email, signup_date) VALUES (?, ?)",
                  (email, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        conn.close()
        
        # Send welcome email with freebie
        try:
            msg = Message(
                subject="Your Prank Cheat Sheet Is Here! Let the Fun Begin 🎉",
                recipients=[email],
                body=f"""
                Hey there,

                Welcome to the Prank Party! 🎉 Here's your free "Ultimate Prank Cheat Sheet":
                Download it here: {url_for('static', filename='prank_cheat_sheet.pdf', _external=True)}

                Stay tuned for our monthly blast—next up, the dumbest Amazon gag gifts you’ll love!

                To manage your subscription, visit: {url_for('manage_subscription', _external=True)}

                Happy pranking,
                The Shopping Assistant Team
                """
            )
            mail.send(msg)
            logging.info(f"Welcome email sent to {email}")
        except Exception as email_error:
            logging.error(f"Failed to send welcome email to {email}: {str(email_error)}")
            return jsonify({"error": f"Failed to send welcome email: {str(email_error)}"}), 500
        
        logging.info(f"New subscriber: {email}")
        return redirect(url_for('thank_you'))
    except sqlite3.IntegrityError:
        logging.warning(f"Email already exists: {email}")
        return jsonify({"error": "Email already subscribed"}), 400
    except Exception as e:
        logging.error(f"Error in subscribe: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/manage-subscription', methods=['GET', 'POST'])
def manage_subscription():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            return render_template('manage_subscription.html', message="Please enter an email address.")

        # Check if the email exists in the database
        conn = sqlite3.connect('emails.db')
        c = conn.cursor()
        c.execute("SELECT signup_date FROM subscribers WHERE email = ?", (email,))
        result = c.fetchone()
        conn.close()

        if result:
            signup_date = result[0]
            message = f"You are subscribed since {signup_date}."
            return render_template('manage_subscription.html', message=message, email=email, subscribed=True)
        else:
            message = "You are not subscribed with this email."
            return render_template('manage_subscription.html', message=message, subscribed=False)

    return render_template('manage_subscription.html')

@app.route('/unsubscribe', methods=['POST'])
def unsubscribe():
    email = request.form.get('email')
    if not email:
        return render_template('manage_subscription.html', message="Please enter an email address.")

    # Remove the email from the database
    conn = sqlite3.connect('emails.db')
    c = conn.cursor()
    c.execute("DELETE FROM subscribers WHERE email = ?", (email,))
    conn.commit()
    conn.close()

    logging.info(f"Unsubscribed: {email}")
    return render_template('manage_subscription.html', message="You have been unsubscribed successfully.", subscribed=False)

@app.route('/thank-you')
def thank_you():
    return render_template('thank_you.html')

@app.route('/find', methods=['POST'])
def find_products():
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
        logging.error(f"Error in find_products: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Script to send monthly email blasts (run as a scheduled task)
def send_monthly_blast():
    # Fetch all subscribers
    conn = sqlite3.connect('emails.db')
    c = conn.cursor()
    c.execute("SELECT email FROM subscribers")
    subscribers = [row[0] for row in c.fetchall()]
    conn.close()
    
    # Example: April Fools' Day blast
    subject = "April Fools’ Pranks That’ll Fool Everyone—Shop Now!"
    body = """
    Hey Prankster,

    April Fools’ Day is here, and we’ve got the best pranks to fool your friends! Check out these hilarious Amazon finds:

    - Fake Poop: Scare your coworker silly! Get it here: https://amzn.to/4hEoA4v
    - Fart Whistles: A classic that never fails. Shop now: https://amzn.to/4kQ39A7

    To manage your subscription, visit: {url}

    Happy pranking,
    The Shopping Assistant Team
    """.format(url=url_for('manage_subscription', _external=True))
    
    for email in subscribers:
        msg = Message(subject=subject, recipients=[email], body=body)
        mail.send(msg)
        logging.info(f"Sent monthly blast to {email}")

# Schedule monthly blast
scheduler = BackgroundScheduler()
scheduler.add_job(func=send_monthly_blast, trigger="cron", day=1, hour=9, minute=0)
scheduler.start()

if __name__ == '__main__':
    try:
        logging.info(f"Starting server at {datetime.now()}")
        app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()