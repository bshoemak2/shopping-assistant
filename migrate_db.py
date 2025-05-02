import sqlite3
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

def migrate_db():
    conn = None
    try:
        conn = sqlite3.connect('subscribers.db')
        c = conn.cursor()
        # Add date column to reviews table if it doesn't exist
        c.execute("PRAGMA table_info(reviews)")
        columns = [col[1] for col in c.fetchall()]
        if 'date' not in columns:
            logging.info("Adding date column to reviews table")
            c.execute("ALTER TABLE reviews ADD COLUMN date TEXT")
            # Optionally, set a default date for existing reviews
            c.execute("UPDATE reviews SET date = '2025-05-01' WHERE date IS NULL")
            conn.commit()
            logging.info("Date column added successfully")
        else:
            logging.info("Date column already exists in reviews table")
    except Exception as e:
        logging.error(f"Error migrating database: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    migrate_db()