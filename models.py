# models.py - FIXED (Auto-creates database if missing)
import pymysql
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_PORT

def get_db_connection():
    """Establish a connection to the MySQL database."""
    try:
        connection = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            port=MYSQL_PORT,
            cursorclass=pymysql.cursors.DictCursor,
            charset='utf8mb4'
        )
        return connection
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def ensure_database_exists():
    """Connect without specifying a database and create it if it doesn't exist."""
    try:
        # Connect to MySQL without selecting a database
        connection = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            port=MYSQL_PORT,
            charset='utf8mb4'
        )
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB}")
            print(f"✅ Database '{MYSQL_DB}' ensured (created if missing).")
        connection.close()
        return True
    except Exception as e:
        print(f"Error ensuring database exists: {e}")
        return False

def init_db():
    """Create tables if they don't exist."""
    # First, ensure the database exists
    if not ensure_database_exists():
        return False
    
    # Now connect to the specific database
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            # Profiles Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    headline TEXT,
                    about TEXT,
                    experience TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Topics Table (Content Matrix)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS topics (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    niche VARCHAR(255),
                    topic_name VARCHAR(255),
                    funnel_stage VARCHAR(50),
                    content_type VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Posts Table (PAS Framework)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    topic_id INT,
                    hook TEXT,
                    problem TEXT,
                    agitate TEXT,
                    solution TEXT,
                    cta TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
                )
            """)
            # Visuals Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS visuals (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    post_id INT,
                    slide_1 TEXT,
                    slide_2 TEXT,
                    slide_3 TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
                )
            """)
            # Analytics Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analytics (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    post_title VARCHAR(255),
                    impressions INT,
                    clicks INT,
                    reactions INT,
                    comments INT,
                    engagement_rate DECIMAL(5,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        conn.commit()
        print("✅ All tables created successfully!")
        return True
    except Exception as e:
        print(f"DB Init Error: {e}")
        return False
    finally:
        conn.close()

# --- CRUD for Profiles ---
def save_profile(headline, about, experience):
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM profiles")  # Keep only latest
            cursor.execute(
                "INSERT INTO profiles (headline, about, experience) VALUES (%s, %s, %s)",
                (headline, about, experience)
            )
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        print(f"Save Profile Error: {e}")
        return None
    finally:
        conn.close()

def get_latest_profile():
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM profiles ORDER BY id DESC LIMIT 1")
            return cursor.fetchone()
    except Exception as e:
        print(f"Get Profile Error: {e}")
        return None
    finally:
        conn.close()

# --- CRUD for Topics ---
def save_topic(niche, topic_name, funnel_stage, content_type):
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO topics (niche, topic_name, funnel_stage, content_type) VALUES (%s, %s, %s, %s)",
                (niche, topic_name, funnel_stage, content_type)
            )
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        print(f"Save Topic Error: {e}")
        return None
    finally:
        conn.close()

def get_topics_by_niche(niche):
    conn = get_db_connection()
    if not conn: return []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM topics WHERE niche = %s ORDER BY id DESC", (niche,))
            return cursor.fetchall()
    except Exception as e:
        print(f"Get Topics Error: {e}")
        return []
    finally:
        conn.close()

# --- CRUD for Posts ---
def save_post(topic_id, hook, problem, agitate, solution, cta):
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO posts (topic_id, hook, problem, agitate, solution, cta) VALUES (%s, %s, %s, %s, %s, %s)",
                (topic_id, hook, problem, agitate, solution, cta)
            )
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        print(f"Save Post Error: {e}")
        return None
    finally:
        conn.close()

def get_posts_by_topic(topic_id):
    conn = get_db_connection()
    if not conn: return []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM posts WHERE topic_id = %s", (topic_id,))
            return cursor.fetchall()
    except Exception as e:
        print(f"Get Posts Error: {e}")
        return []
    finally:
        conn.close()

# --- CRUD for Visuals ---
def save_visual(post_id, slide_1, slide_2, slide_3):
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO visuals (post_id, slide_1, slide_2, slide_3) VALUES (%s, %s, %s, %s)",
                (post_id, slide_1, slide_2, slide_3)
            )
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        print(f"Save Visual Error: {e}")
        return None
    finally:
        conn.close()

def get_visual_by_post(post_id):
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM visuals WHERE post_id = %s ORDER BY id DESC LIMIT 1", (post_id,))
            return cursor.fetchone()
    except Exception as e:
        print(f"Get Visual Error: {e}")
        return None
    finally:
        conn.close()

# --- CRUD for Analytics ---
def save_analytics(post_title, impressions, clicks, reactions, comments, engagement_rate):
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO analytics (post_title, impressions, clicks, reactions, comments, engagement_rate) VALUES (%s, %s, %s, %s, %s, %s)",
                (post_title, impressions, clicks, reactions, comments, engagement_rate)
            )
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        print(f"Save Analytics Error: {e}")
        return None
    finally:
        conn.close()

def get_all_analytics():
    conn = get_db_connection()
    if not conn: return []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM analytics ORDER BY engagement_rate DESC")
            return cursor.fetchall()
    except Exception as e:
        print(f"Get Analytics Error: {e}")
        return []
    finally:
        conn.close()