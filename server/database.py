import hashlib
import hmac
import os
import sqlite3


class DataBase:
    def __init__(self):
        """
        Opens a connection to the SQLite database and initializes all tables.
        :return: Creates all required tables in the database if they do not exist
        """
        self.conn = sqlite3.connect("ucademy.db")
        self.cur = self.conn.cursor()

        self._create_users_table()
        self._create_videos_table()
        self._create_comments_table()
        self._create_likes_table()
        self._create_following_table()
        self._create_video_topics_table()
        self._create_user_topics_table()
        self._create_watched_videos_table()
        self._create_video_hashes_table()

    def close(self):
        """
        Closes the database connection.
        :return: Closes the active database connection
        """
        self.conn.close()

    # ===== table creation =====

    def _create_users_table(self):
        """
        Creates the users table.
        :return: Creates the users table if it does not already exist
        """
        self.cur.execute("""
                         CREATE TABLE IF NOT EXISTS users (
                                                              username TEXT PRIMARY KEY,
                                                              email TEXT,
                                                              password TEXT
                         )
                         """)
        self.conn.commit()

    def _create_videos_table(self):
        """
        Creates the videos table.
        :return: Creates the videos table if it does not already exist
        """
        self.cur.execute("""CREATE TABLE IF NOT EXISTS videos (
                                                                  video_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                  creator TEXT,
                                                                  name TEXT,
                                                                  description TEXT,
                                                                  test_link TEXT
                            )
                         """)
        self.conn.commit()

    def _create_comments_table(self):
        """
        Creates the comments table.
        :return: Creates the comments table if it does not already exist
        """
        self.cur.execute("""CREATE TABLE IF NOT EXISTS comments (
                                                                    comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                    video_id INTEGER,
                                                                    commenter TEXT,
                                                                    comment TEXT
                            )
                         """)
        self.conn.commit()

    def _create_likes_table(self):
        """
        Creates the likes table.
        :return: Creates the likes table if it does not already exist
        """
        self.cur.execute("""CREATE TABLE IF NOT EXISTS likes (
                                                                 video_id INTEGER,
                                                                 username TEXT,
                                                                 PRIMARY KEY (video_id, username)
            )
                         """)
        self.conn.commit()

    def _create_following_table(self):
        """
        Creates the following table.
        :return: Creates the following table if it does not already exist
        """
        self.cur.execute("""CREATE TABLE IF NOT EXISTS following (
                                                                     following TEXT,
                                                                     followed TEXT,
                                                                     PRIMARY KEY (following, followed)
            )
                         """)
        self.conn.commit()

    def _create_video_topics_table(self):
        """
        Creates the video_topics table.
        :return: Creates the video_topics table if it does not already exist
        """
        self.cur.execute("""CREATE TABLE IF NOT EXISTS video_topics (
                                                                        video_id INTEGER,
                                                                        topic INTEGER,
                                                                        PRIMARY KEY (video_id, topic)
            )
                         """)
        self.conn.commit()

    def _create_user_topics_table(self):
        """
        Creates the user_topics table.
        :return: Creates the user_topics table if it does not already exist
        """
        self.cur.execute("""CREATE TABLE IF NOT EXISTS user_topics (
                                                                       username TEXT,
                                                                       topic INTEGER,
                                                                       PRIMARY KEY (username, topic)
            )
                         """)
        self.conn.commit()

    def _create_watched_videos_table(self):
        """
        Creates the watched_videos table.
        :return: Creates the watched_videos table if it does not already exist
        """
        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS watched_videos (
                                                             username TEXT,
                                                             video_id INTEGER,
                                                             PRIMARY KEY (username, video_id)
                )
            """)
        self.conn.commit()

    def _create_video_hashes_table(self):
        """
        Creates the video_hashes table.
        :return: Creates the video_hashes table if it does not already exist
        """
        self.cur.execute("""CREATE TABLE IF NOT EXISTS video_hashes (
                                                                        video_id INTEGER PRIMARY KEY,
                                                                        video_hash TEXT UNIQUE
                            )
                         """)
        self.conn.commit()

    # ===== users =====

    def user_exists(self, username):
        """
        Checks whether a user exists.
        :param username: Username to check
        :return: True if the user exists in the users table, False otherwise
        """
        self.cur.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        return self.cur.fetchone() is not None

    def email_exists(self, email):
        self.cur.execute("SELECT 1 FROM users WHERE email = ?", (email,))
        return self.cur.fetchone() is not None

    def  add_user(self, username, email, password_hash):
        """
        Adds a new user to the database.
        :param username: Unique username of the user
        :param email: Email address of the user
        :param password_hash: Hashed password of the user
        :return: Inserts a new row into the users table if the username is available
        """
        added = False
        if not self.user_exists(username) and not self.email_exists(email):
            self.cur.execute("INSERT INTO users VALUES (?,?,?)", (username, email, password_hash))
            self.conn.commit()
            added = True
        return added

    def get_all_usernames(self):
        """
        Retrieves all users.
        :return: List of all usernames from the users table
        """
        self.cur.execute("SELECT username FROM users")
        return [row[0] for row in self.cur.fetchall()]


    def get_similar_usernames(self, username):
        """
        Retrieves users whose usernames start with a prefix.
        :param username: Username prefix
        :return: List of matching usernames
        """
        self.cur.execute("SELECT username FROM users WHERE username LIKE ? COLLATE NOCASE", ("%"+ username + "%",))
        return self.cur.fetchall()

    def log_in(self, username_or_email, password_hash):
        self.cur.execute("SELECT password FROM users WHERE username = ? OR email = ?", (username_or_email, username_or_email))
        stored_password_hash = self.cur.fetchone()[0]
        return self.verify_password(password_hash, stored_password_hash)

    @staticmethod
    def verify_password(password: str, stored: str) -> bool:
        algo, iters, salt_hex, dk_hex = stored.split("$")
        iterations = int(iters)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(dk_hex)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(dk, expected)

    def get_user_email(self, username):
        self.cur.execute("SELECT email FROM users WHERE username = ?", (username,))
        return self.cur.fetchone()[0]

    def get_username(self, username_or_email):
        """
        :param username_or_email: The username or email address to search for in the users table.
        :return: The first username found matching the given username or email address.
        """
        self.cur.execute("SELECT username FROM users WHERE username = ? OR email = ?", (username_or_email, username_or_email))
        return self.cur.fetchone()[0]

    # ===== videos =====

    def get_specific_video(self, video_id):
        """
        Retrieves a video by ID.
        :param video_id: ID of the video
        :return: Video row from the videos table or None if not found
        """
        self.cur.execute("SELECT * FROM videos WHERE video_id = ?", (video_id,))
        return self.cur.fetchall()


    def add_video(self, creator, name, description, test_link):
        """
        Adds a new video.
        :param creator: Username of the uploader
        :param name: Video title
        :param description: Video description
        :return: Inserts a new row into the videos table
        """
        self.cur.execute("INSERT INTO videos (creator, name, description, test_link) VALUES (?,?,?,?)",
                         (creator, name, description, test_link))
        self.conn.commit()
        video_id = self.cur.lastrowid
        return video_id


    def delete_video(self, video_id):
        """
        Deletes a video.
        :param video_id: ID of the video
        :return: Removes the video row from the videos table
        """
        self.cur.execute("DELETE FROM videos WHERE video_id = ?", (video_id,))
        self.conn.commit()

    def get_video_amount(self, username):
        self.cur.execute("SELECT COUNT(*) FROM videos WHERE creator = ?", (username,))

    def get_video_text_link(self, video_id):
        self.cur.execute("SELECT test_link FROM videos WHERE video_id = ?", (video_id,))
        return self.cur.fetchone()[0]

    def get_videos_with_similar_desc(self, desc):
        self.cur.execute(
            "SELECT * FROM videos WHERE desc LIKE ? COLLATE NOCASE",
            ('%' + desc + '%',)
        )
        return self.cur.fetchall()

    def get_videos_with_similar_name(self, name):
        self.cur.execute(
            "SELECT * FROM videos WHERE desc LIKE ? COLLATE NOCASE",
            ('%' + name + '%',)
        )
        return self.cur.fetchall()

    # ===== comments =====

    def get_comments(self, video_id):
        """
        Retrieves comments for a video.
        :param video_id: ID of the video
        :return: List of comment rows from the comments table
        """
        self.cur.execute("SELECT * FROM comments WHERE video_id = ?", (video_id,))
        return self.cur.fetchall()

    def get_comments_amount(self, video_id):
        self.cur.execute("SELECT COUNT(*) FROM comments WHERE video_id = ?", (video_id,))
        return self.cur.fetchall()

    def delete_comment(self, comment_id):
        """
        Deletes a comment.
        :param comment_id: ID of the comment
        :return: Removes the comment row from the comments table
        """
        self.cur.execute("DELETE FROM comments WHERE comment_id = ?", (comment_id,))
        self.conn.commit()

    # ===== likes =====

    def add_video_like(self, video_id, username):
        """
        Adds a like to a video.
        :param video_id: ID of the liked video
        :param username: Username of the liking user
        :return: Inserts a new row into the likes table
        """
        self.cur.execute("INSERT INTO likes VALUES (?,?)", (video_id, username))
        self.conn.commit()

    def remove_video_like(self, video_id, username):
        """
        Removes a like from a video.
        :param video_id: ID of the video
        :param username: Username of the user
        :return: Deletes the like row from the likes table
        """
        self.cur.execute("DELETE FROM likes WHERE video_id = ? AND username = ?", (video_id, username))
        self.conn.commit()

    def get_video_likes_amount(self, video_id):
        """
        Counts likes on a video.
        :param video_id: ID of the video
        :return: Number of likes for the video
        """
        self.cur.execute("SELECT COUNT(*) FROM likes WHERE video_id = ?", (video_id,))
        return self.cur.fetchone()[0]

    def is_liked_by_user(self, video_id, username):
        self.cur.execute("SELECT 1 FROM likes WHERE video_id = ? AND username = ?",(video_id, username))
        return self.cur.fetchone()[0]

    # ===== following =====
    def add_following(self, following, followed):
        self.cur.execute("INSERT INTO following VALUES (?, ?)", (following, followed))
        self.conn.commit()

    def get_followings(self, username):
        self.cur.execute("SELECT followed FROM following WHERE following = ?", (username,))
        followings = self.cur.fetchall()
        return [f[0] for f in followings]  # Return a list of followed usernames

    def get_followers(self, username):
        followers = self.cur.fetchall()
        self.cur.execute("SELECT following FROM following WHERE followed = ?", (username,))
        return followers

    def remove_following(self, following, followed):
        self.cur.execute("DELETE FROM following WHERE following = ? and followed = ?", (following, followed))
        self.conn.commit()

    def is_following(self, following, followed):
        self.cur.execute("SELECT 1 FROM following WHERE following = ? and followed = ?", (following, followed))
        return self.cur.fetchone() is not None

    def get_followers_amount(self, username):
        self.cur.execute("SELECT COUNT(*) FROM followers WHERE followed = ?", (username,))
        return self.cur.fetchone()[0]

    def get_following_amount(self, username):
        self.cur.execute("SELECT COUNT(*) FROM followers WHERE following = ?", (username,))

    # ===== video topics =====

    def add_video_topics(self, video_id, topics):
        self.cur.execute("INSERT INTO topics VALUES (?,?)", (video_id, topics))
        self.conn.commit()

    def get_video_topics(self, video_id):
        self.cur.execute("SELECT * FROM topics WHERE video_id = ?", (video_id,))
        return self.cur.fetchall()

    def get_videos_ids_by_topics(self, topics):
        video_ids = []
        if topics:
            placeholders = ",".join(["?"] * len(topics))
            query = f"SELECT video_id FROM topics WHERE topic IN ({placeholders})"
            self.cur.execute(query, topics)
            video_ids = self.cur.fetchall()

        return video_ids

    # ===== user topics =====

    def _add_user_topics(self, username, topics):
        for topic in topics:
            self.cur.execute("INSERT INTO user_topics VALUES (?, ?)", (username, topic))
        self.conn.commit()

    def _remove_user_topics(self, username, topics):
        for topic in topics:
            self.cur.execute("DELETE FROM user_topics WHERE username = ? AND topic = ?", (username, topic))
        self.conn.commit()

    def get_user_topics(self, username):
        self.cur.execute("SELECT topic FROM user_topics WHERE username = ?", (username,))
        topics = self.cur.fetchall()
        return [t[0] for t in topics]

    def set_topics(self, username, new_topics):
        old_topics = self.get_user_topics(username)
        to_add_topics = set(new_topics) - set(old_topics)
        to_remove_topics = set(old_topics) - set(new_topics)

        print("topic lists:",to_add_topics, to_remove_topics)

        self._add_user_topics(username, to_add_topics)
        self._remove_user_topics(username, to_remove_topics)

    # ===== Watched videos =====

    def add_watched_video(self, username, video_id):
        self.cur.execute("INSERT INTO watched_videos VALUES (?,?)", (username, video_id))
        self.conn.commit()

    def get_watched_videos(self, username):
        self.cur.execute("SELECT watched FROM watched_videos WHERE username = ?", (username,))
        return self.cur.fetchall()

    def get_amount_of_views(self, video_id):
        self.cur.execute("SELECT COUNT(*) FROM watched_videos WHERE video_id = ?", (video_id,))
        return self.cur.fetchone()[0]

    def has_watched_video(self, username, video_id):
        self.cur.execute("SELECT 1 FROM watched_videos WHERE username = ? AND video_id = ?", (username, video_id))
        return self.cur.fetchone() is not None

    def order_ids_by_views(self, video_ids):
        self.cur.execute("SELECT video_id FROM watched_videos WHERE video_id = ?, ORDER BY views", (video_ids,))
        return self.cur.fetchall()


    # ===== video hashes =====

    def add_video_hash(self, video_id, video_hash):
        """
        Stores a hash for a video file.
        :param video_id: ID of the video
        :param video_hash: Hash of the video file
        :return: Inserts a new row into the video_hashes table
        """
        self.cur.execute("INSERT INTO video_hashes VALUES (?,?)", (video_id, video_hash))
        self.conn.commit()

    def remove_video_hash(self, video_id):
        """
        Removes a video hash.
        :param video_id: ID of the video
        :return: Deletes the corresponding row from the video_hashes table
        """
        self.cur.execute("DELETE FROM video_hashes WHERE video_id = ?", (video_id,))
        self.conn.commit()

    def hash_exists(self, video_hash):
        """
        Checks if a video hash already exists.
        :param video_hash: Hash to check
        :return: True if the hash exists in the video_hashes table, False otherwise
        """
        self.cur.execute("SELECT 1 FROM video_hashes WHERE video_hash = ?", (video_hash,))
        return self.cur.fetchone() is not None


    def delete_database(self):
        self.conn.close()
        os.remove("ucademy.db")

    def print_tables(self):
        # Get all table names
        self.cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in self.cur.fetchall()]

        # Print first 5 rows of each table
        for table in tables:
            print(f"\nTable: {table}")
            self.cur.execute(f"SELECT * FROM {table} LIMIT 5;")
            rows = self.cur.fetchall()
            for row in rows:
                print(row)

if __name__ == "__main__":
    db = DataBase()

    # --- users ---
    if db.add_user("admin", "admin@example.com", "hashed_password"):
        print("User added")
    else:
        print("User already exists")

    print("All users:", db.get_all_usernames())

    # --- videos ---
    db.add_video("admin", "First Video", "This is a test video")
    video = db.get_specific_video(1)
    print("Video 1:", video)

    # --- likes ---
    db.add_video_like(1, "admin")
    print("Likes on video 1:", db.get_video_likes_amount(1))

    # --- hashes ---
    if not db.hash_exists("abc123"):
        db.add_video_hash(1, "abc123")

    print("Hash exists:", db.hash_exists("abc123"))

    db.close()
