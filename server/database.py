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
        self._create_reports_table()
        self._create_system_managers_table()

    # ==== db in general ====
    def close(self):
        """
        Closes the database connection.
        :return: Closes the active database connection
        """
        self.conn.close()

    def delete_database(self):
        """
        Close the database connection and delete the database file.
        """
        self.conn.close()
        if os.path.isfile("ucademy.db"):
            os.remove("ucademy.db")

    def print_tables(self):
        """
        Print the first 15 rows of every table in the database for debugging purposes.
        """
        self.cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in self.cur.fetchall()]

        for table in tables:
            print(f"\nTable: {table}")
            self.cur.execute(f"SELECT * FROM {table} LIMIT 15;")
            rows = self.cur.fetchall()
            for row in rows:
                print(row)

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
            password_hash TEXT
        ) """)
        self.conn.commit()



    def _create_videos_table(self):
        """
        Creates the videos table.
        :return: Creates the videos table if it does not already exist.
        """
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                video_id INTEGER PRIMARY KEY AUTOINCREMENT,
                creator TEXT,
                name TEXT,
                description TEXT,
                test_link TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                deleted INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()


    def _create_comments_table(self):
        """
        Creates the comments table.
        :return: Creates the comments table if it does not already exist.
        """
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id INTEGER,
                commenter TEXT,
                comment TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                deleted INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()


    def _create_likes_table(self):
        """
        Creates the likes table.
        :return: Creates the likes table if it does not already exist.
        """
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS likes (
                video_id INTEGER,
                username TEXT,
                PRIMARY KEY (video_id, username)
            )
        """)
        self.conn.commit()


    def _create_following_table(self):
        """
        Creates the following table.
        :return: Creates the following table if it does not already exist.
        """
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS following (
                follower TEXT,
                followed TEXT,
                PRIMARY KEY (follower, followed)
            )
        """)
        self.conn.commit()

    def _create_video_topics_table(self):
        """
        Creates the video_topics table.
        :return: Creates the video_topics table if it does not already exist.
        """
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS video_topics (
                video_id INTEGER,
                topic INTEGER,
                PRIMARY KEY (video_id, topic)
            )
        """)
        self.conn.commit()


    def _create_user_topics_table(self):
        """
        Creates the user_topics table.
        :return: Creates the user_topics table if it does not already exist.
        """
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS user_topics (
                username TEXT,
                topic INTEGER,
                PRIMARY KEY (username, topic)
            )
        """)
        self.conn.commit()


    def _create_watched_videos_table(self):
        """
        Creates the watched_videos table.
        :return: Creates the watched_videos table if it does not already exist.
        """
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS watched_videos (
                username TEXT,
                video_id INTEGER,
                PRIMARY KEY (username, video_id)
            )
        """)
        self.conn.commit()


    def _create_video_hashes_table(self):
        """
        Creates the video_hashes table.
        :return: Creates the video_hashes table if it does not already exist.
        """
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS video_hashes (
                video_id INTEGER PRIMARY KEY,
                video_hash TEXT UNIQUE
            )
        """)
        self.conn.commit()


    def _create_reports_table(self):
        """
        Creates the reports table.
        :return: Creates the reports table if it does not already exist.
        """
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                reporter_name TEXT,
                target_id INTEGER,
                target_type INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                status INTEGER DEFAULT NULL,
                notified INTEGER DEFAULT 0,
                PRIMARY KEY (reporter_name, target_id, target_type)
            )
        """)
        self.conn.commit()


    def _create_system_managers_table(self):
        """
        Creates the system_managers table.
        :return: Creates the system_managers table if it does not already exist.
        """
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS system_managers (
                username TEXT PRIMARY KEY
            )
        """)
        self.conn.commit()

    # ===== users =====

    def remove_user(self, username):
        """
        Removes a user from the database.
        :param username: Username of the user to delete
        """
        self.cur.execute("DELETE FROM users WHERE username = ? COLLATE NOCASE", (username,))
        self.conn.commit()

    def user_exists(self, username):
        """
        Checks whether a user exists.
        :param username: Username to check
        :return: True if the user exists in the users table, False otherwise
        """
        self.cur.execute("SELECT 1 FROM users WHERE username = ? COLLATE NOCASE", (username,))
        return self.cur.fetchone() is not None

    def email_exists(self, email):
        """
        Checks whether an email exists in the database.
        :param email: Email to check
        :return: True if the email exists, False otherwise
        """
        email = email.lower()
        self.cur.execute("SELECT 1 FROM users WHERE email = ? COLLATE NOCASE", (email,))
        return self.cur.fetchone() is not None

    def log_in(self, username, password_hash):
        """
        Validates user login credentials.
        :param username: Username of the user
        :param password_hash: Hashed password to verify
        :return: True if credentials match, False otherwise
        """
        self.cur.execute("SELECT 1 FROM users WHERE username = ? AND password_hash = ?", (
            username, password_hash))
        return self.cur.fetchone() is not None

    def add_user(self, username, email, password_hash):
        """
        Adds a new user to the database.
        :param username: Unique username of the user
        :param email: Email address of the user
        :param password_hash: Hashed password of the user
        :return: Inserts a new row into the users table if the username is available
        """
        added = False
        if not self.user_exists(username):
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
        self.cur.execute("SELECT username FROM users WHERE username LIKE ? COLLATE NOCASE", ("%" + username + "%",))
        return self.cur.fetchall()

    def get_password_hash(self, username):
        """
        Retrieves the password hash of a user.
        :param username: Username of the user
        :return: Password hash if found, otherwise None
        """
        self.cur.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
        res = self.cur.fetchone()
        if res:
            res = res[0]
        return res

    def get_user_email(self, username):
        """
        Retrieves the email of a user.
        :param username: Username of the user
        :return: Email if found, otherwise None
        """
        self.cur.execute("SELECT email FROM users WHERE username = ? COLLATE NOCASE", (username,))
        res = self.cur.fetchone()
        if res:
            res = res[0]
        return res

    def get_username(self, username_or_email):
        """
        :param username_or_email: The username or email address to search for in the users table.
        :return: The first username found matching the given username or email address.
        """
        self.cur.execute("SELECT username FROM users WHERE username = ? COLLATE NOCASE OR email = ? COLLATE NOCASE",
                         (username_or_email, username_or_email))
        username = self.cur.fetchone()
        if username:
            username = username[0]
        return username

    # ===== videos =====

    def get_videos_by_creator(self, username):
        """
        Retrieves video IDs created by a specific user ordered by views.
        :param username: Creator username
        :return: List of video IDs sorted by number of views
        """
        self.cur.execute("""
                         SELECT videos.video_id, COUNT(watched_videos.username) AS views
                         FROM videos
                                  LEFT JOIN watched_videos ON videos.video_id = watched_videos.video_id
                         WHERE videos.creator = ?
                         GROUP BY videos.video_id
                         ORDER BY views DESC
                         """, (username,))

        results = self.cur.fetchall()
        results = [i[0] for i in results]
        return results

    def is_the_video_creator(self, video_id, username):
        """
        Checks if a user is the creator of a video.
        :param video_id: ID of the video
        :param username: Username to check
        :return: True if the user is the creator, False otherwise
        """
        self.cur.execute("SELECT 1 FROM videos WHERE video_id = ? AND creator = ?", (video_id, username))
        return self.cur.fetchone() is not None

    def video_exists(self, video_id):
        """
        Checks if a video exists.
        :param video_id: ID of the video
        :return: True if the video exists, False otherwise
        """
        self.cur.execute("SELECT 1 FROM videos WHERE video_id = ?", (video_id,))
        return self.cur.fetchone() is not None

    def get_specific_video(self, video_id, matter_deleted=True):
        """
        Retrieves a video by ID.
        :param video_id: ID of the video
        :param matter_deleted: A boolean indicating whether deleted videos should be excluded from the results.
        :return: video details: creator, name, desc, created_at, likes_amount, comments_amount
        """
        ret_val = None
        if self.video_exists(video_id) and not (matter_deleted and self.video_deleted(video_id)):
            self.cur.execute("""
                             SELECT videos.creator,
                                    videos.name,
                                    videos.description,
                                    strftime('%d/%m/%Y %H:%M', videos.created_at),
                                    COUNT(DISTINCT likes.username)     AS likes_count,
                                    COUNT(DISTINCT comments.commenter) AS comments_count
                             FROM videos
                                      LEFT JOIN likes ON videos.video_id = likes.video_id
                                      LEFT JOIN comments ON videos.video_id = comments.video_id

                             WHERE videos.video_id = ?
                             GROUP BY videos.video_id
                             """, (video_id,))
            ret_val = self.cur.fetchone()

        return ret_val

    def video_deleted(self, video_id):
        """
        Checks if a video is marked as deleted.
        :param video_id: ID of the video
        :return: True if deleted, False otherwise
        """
        self.cur.execute("SELECT 1 FROM videos WHERE video_id = ? AND deleted = 1", (video_id,))
        return self.cur.fetchone() is not None

    def add_video(self, creator, name, description, test_link=None):
        """
        Adds a new video.
        :param creator: Username of the uploader
        :param name: Video title
        :param description: Video description
        :param test_link: An optional test link for the video.
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
        self.cur.execute("UPDATE videos SET deleted = 1 WHERE video_id = ?", (video_id,))
        self.conn.commit()

    def get_videos_amount(self, username):
        """
        Counts how many videos a user has.
        :param username: Creator username
        :return: Number of videos created by the user
        """
        self.cur.execute("SELECT COUNT(*) FROM videos WHERE creator = ?", (username,))
        return self.cur.fetchone()[0]

    def get_video_test_link(self, video_id):
        """
        Retrieves the test link of a video.
        :param video_id: ID of the video
        :return: Test link if exists, otherwise None
        """
        self.cur.execute("SELECT test_link FROM videos WHERE video_id = ?", (video_id,))
        result = self.cur.fetchone()
        if result:
            result = result[0]
        return result

    def get_videos_with_similar_desc(self, desc):
        """
        Finds videos with similar descriptions.
        :param desc: Description keyword
        :return: List of matching video IDs
        """
        self.cur.execute(
            "SELECT video_id FROM videos WHERE description LIKE ? COLLATE NOCASE",
            ('%' + desc + '%',)
        )

        results = self.cur.fetchall()
        results = [i[0] for i in results]
        return results

    def get_videos_with_similar_name(self, name):
        """
        Finds videos with similar names.
        :param name: Name keyword
        :return: List of matching video IDs
        """
        self.cur.execute(
            "SELECT video_id FROM videos WHERE name LIKE ? COLLATE NOCASE",
            ('%' + name + '%',)
        )
        results = self.cur.fetchall()
        results = [i[0] for i in results]
        return results

    def get_most_viewed_video_for_user(self, username):
        """
        Retrieves the most viewed video the user has not watched yet.
        :param username: Username of the viewer
        :return: Video ID of the most viewed unseen video or None
        """
        self.cur.execute("""
                         SELECT videos.video_id, COUNT(watched_videos.video_id) AS views
                         FROM videos
                                  LEFT JOIN watched_videos ON videos.video_id = watched_videos.video_id
                         WHERE videos.deleted = 0
                           AND NOT EXISTS (SELECT 1
                                           FROM watched_videos
                                           WHERE watched_videos.video_id = videos.video_id
                                             AND watched_videos.username = ?)

                         GROUP BY videos.video_id
                         ORDER BY views DESC

                         """, (username,))

        res = self.cur.fetchone()
        if res:
            res = res[0]
        return res

    def add_comment(self, video_id, commenter_name, comment):
        """
        Adds a new comment to a video
        :param video_id: ID of the video the comment belongs to
        :param commenter_name: the username of the person adding the comment
        :param comment: the content of the comment
        :return: ID of the newly inserted comment
        """
        self.cur.execute("INSERT INTO comments (video_id, commenter, comment) VALUES (?,?,?)",
                         (video_id, commenter_name, comment))
        self.conn.commit()
        return self.cur.lastrowid

    def get_specific_comment(self, comment_id, matter_deleted=True):
        """
            Retrieve a specific comment from the database by its comment_id.
            This method executes a query to retrieve a single comment from the `comments`
            table using the given comment_id.
        :param comment_id: The id of the comment to retrieve.
        :param matter_deleted: A boolean indicating whether deleted comments should be excluded from the results.
        :return: Tuple representing the comment: video_id, comment_id, commenter, comment, created_at
        """
        res = None
        if self.comment_exists(comment_id) and not (matter_deleted and self.comment_deleted(comment_id)):
            self.cur.execute(
                "SELECT comment_id, video_id, commenter, comment, strftime('%d/%m/%Y %H:%M', created_at) FROM comments WHERE comment_id = ?",
                (comment_id,))
            res = self.cur.fetchone()
        return res

    def comment_deleted(self, comment_id):
        """
        Checks if a comment is marked as deleted
        :param comment_id: ID of the comment to check
        :return: True if the comment is deleted, False otherwise
        """
        self.cur.execute("SELECT 1 FROM comments WHERE comment_id = ? AND deleted = 1", (comment_id,))
        return self.cur.fetchone() is not None

    def get_comments(self, video_id, username):
        """
        Retrieves comments for a video.
        :param video_id: ID of the video
        :param username: username of the user requesting the comments
        :return: List of comment rows from the comments table, when the comments of username are first
        """
        self.cur.execute("""
                         SELECT comment_id, video_id, commenter, comment, strftime('%d/%m/%Y %H:%M', created_at)
                         FROM comments
                         WHERE video_id = ?
                           AND deleted = 0
                         ORDER BY CASE WHEN commenter = ? THEN 0 ELSE 1 END, comment_id DESC;""", (video_id, username))
        comments = self.cur.fetchall()
        return comments

    def get_comments_amount(self, video_id):
        """
        Counts the number of non-deleted comments for a video
        :param video_id: ID of the video
        :return: Number of comments for the video
        """
        self.cur.execute("SELECT COUNT(*) FROM comments WHERE video_id = ? and deleted = 0", (video_id,))
        return self.cur.fetchone()[0]

    def delete_comment(self, comment_id):
        """
        Deletes a comment.
        :param comment_id: ID of the comment
        :return: Removes the comment row from the comments table
        """
        self.cur.execute("UPDATE comments SET deleted = 1 WHERE comment_id = ?", (comment_id,))
        self.conn.commit()

    def comment_exists(self, comment_id):
        """
        Checks if a comment exists in the database
        :param comment_id: ID of the comment to check
        :return: True if the comment exists, False otherwise
        """
        self.cur.execute("SELECT 1 FROM comments WHERE comment_id = ?", (comment_id,))
        return self.cur.fetchone() is not None

    def get_video_id_by_comment_id(self, comment_id):
        """
        Retrieves the video ID associated with a specific comment
        :param comment_id: ID of the comment
        :return: Video ID if found, otherwise None
        """
        self.cur.execute("SELECT video_id FROM comments WHERE comment_id = ?", (comment_id,))
        res = self.cur.fetchone()
        if res:
            res = res[0]
        return res

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
        """
        Checks if a user has liked a specific video
        :param video_id: ID of the video
        :param username: Username of the user
        :return: True if the user liked the video, False otherwise
        """
        self.cur.execute("SELECT 1 FROM likes WHERE video_id = ? AND username = ?", (video_id, username))
        return self.cur.fetchone() is not None

    # ===== following =====
    def add_following(self, following, followed):
        """
        Adds a following relationship between two users
        :param following: Username of the follower
        :param followed: Username of the user being followed
        """
        self.cur.execute("INSERT INTO following VALUES (?, ?)", (following, followed))
        self.conn.commit()

    def get_followings(self, username):
        """
        Retrieves a list of users that the given user is following
        :param username: Username of the user
        :return: List of followed usernames
        """
        self.cur.execute("SELECT followed FROM following WHERE follower = ?", (username,))
        followings = [i[0] for i in self.cur.fetchall()]
        return followings  # Return a list of followed usernames

    def get_followers(self, username):
        """
        Retrieves a list of users who follow the given user
        :param username: Username of the user
        :return: List of follower usernames
        """
        self.cur.execute("SELECT following FROM following WHERE followed = ?", (username,))
        followers = [i[0] for i in self.cur.fetchall()]
        return followers

    def remove_following(self, following, followed):
        """
        Removes a following relationship between two users
        :param following: Username of the follower
        :param followed: Username of the user being unfollowed
        """
        self.cur.execute("DELETE FROM follower WHERE following = ? and followed = ?", (following, followed))
        self.conn.commit()

    def is_following(self, following, followed):
        """
        Checks if one user is following another
        :param following: Username of the follower
        :param followed: Username of the user being followed
        :return: True if following, False otherwise
        """
        self.cur.execute("SELECT 1 FROM following WHERE follower = ? and followed = ?", (following, followed))
        return self.cur.fetchone() is not None

    def get_followers_amount(self, username):
        """
        Counts the number of followers a user has
        :param username: Username of the user
        :return: Number of followers
        """
        self.cur.execute("SELECT COUNT(*) FROM following WHERE followed = ?", (username,))
        return self.cur.fetchone()[0]

    def get_following_amount(self, username):
        """
        Counts the number of users a given user is following
        :param username: Username of the user
        :return: Number of followings
        """
        self.cur.execute("SELECT COUNT(*) FROM following WHERE follower = ?", (username,))
        return self.cur.fetchone()[0]

    # ===== video topics =====

    def add_video_topics(self, video_id, topics):
        """
        Adds multiple topics to a video
        :param video_id: ID of the video
        :param topics: iterable of topics to associate with the video
        """
        for topic in topics:
            self.cur.execute("INSERT INTO video_topics VALUES (?,?)", (video_id, topic))
        self.conn.commit()

    def get_video_topics(self, video_id):
        """
        Retrieves all topics associated with a video
        :param video_id: ID of the video
        :return: List of tuples representing video-topic relationships
        """
        self.cur.execute("SELECT * FROM video_topics WHERE video_id = ?", (video_id,))
        return self.cur.fetchall()

    def get_videos_ids_by_topics(self, topics):
        """
        Retrieves video IDs that match any of the given topics
        :param topics: list of topics to filter videos by
        :return: List of video IDs matching the topics
        """
        video_ids = []
        if topics:
            placeholders = ",".join(["?"] * len(topics))
            self.cur.execute(f"SELECT video_id FROM video_topics WHERE topic IN ({placeholders})", (*topics,))
            video_ids = self.cur.fetchall()
            video_ids = [i[0] for i in video_ids]

        return video_ids

    def get_video_for_user_topics(self, username):
        """
        Retrieves a recommended video for a user based on shared topics and popularity
        :param username: Username of the user
        :return: Video ID if found, otherwise None
        """
        self.cur.execute("""
                         SELECT video_topics.video_id,
                                COUNT(watched_videos.username) AS views,
                                COUNT(video_topics.topic)      AS shared_topics

                         FROM user_topics
                                  LEFT JOIN video_topics ON user_topics.topic = video_topics.topic
                                  LEFT JOIN watched_videos ON video_topics.video_id = watched_videos.video_id

                         WHERE EXISTS(SELECT 1
                                      FROM videos
                                      WHERE videos.video_id = video_topics.video_id
                                        AND deleted = 0)
                           AND user_topics.username = ?
                           AND NOT EXISTS (SELECT 1
                                           FROM watched_videos
                                           WHERE watched_videos.video_id = video_topics.video_id
                                             AND watched_videos.username = ?)

                         GROUP BY video_topics.video_id
                         ORDER BY shared_topics DESC, views DESC
                         """, (username, username))

        res = self.cur.fetchone()
        if res:
            res = res[0]
        return res

    def get_video_for_user_filter(self, username, filter):
        """
        Retrieves a recommended video for a user based on a filter of topics
        :param username: Username of the user
        :param filter: list of topics to filter videos
        :return: Video ID if found, otherwise None
        """
        res = None
        if filter:
            place_holders = ("?," * len(filter))[:-1]
            self.cur.execute(
                f"""
                SELECT video_topics.video_id, 
                    COUNT(watched_videos.username) AS views, 
                    COUNT(video_topics.topic) AS shared_topics
                FROM video_topics
                    LEFT JOIN watched_videos ON video_topics.video_id = watched_videos.video_id

                WHERE EXISTS(
                    SELECT 1 FROM videos
                    WHERE videos.video_id = video_topics.video_id AND deleted = 0
                )
                AND video_topics.topic IN ({place_holders})
                AND NOT EXISTS (
                    SELECT 1 FROM watched_videos 
                    WHERE watched_videos.video_id = video_topics.video_id AND watched_videos.username = ?
                )
                GROUP BY video_topics.video_id
                ORDER BY shared_topics, views
            """, (*filter, username))

            res = self.cur.fetchone()
            if res:
                res = res[0]
        return res

    def get_video_for_user(self, username, filter=None):
        """
        Retrieves a recommended video for a user based on filters, topics, or popularity
        :param username: Username of the user
        :param filter: optional list of topics to filter videos
        :return: Video ID of the recommended video
        """
        # returns the most viewed video that the user has not seen and is included in his topics

        if filter:
            res = self.get_video_for_user_filter(username, filter)
            if not res:  # if not videos matching filter
                res = self.get_video_for_user_topics(username)  # use video matching topics
        else:
            res = self.get_video_for_user_topics(username)

        if not res:  # if no video matches filter or topics
            res = self.get_most_viewed_video_for_user(username)

        print("res im db:", res)
        return res

    # ===== user topics =====

    def _add_user_topics(self, username, topics):
        """
        Adds topics to a user's preferences
        :param username: Username of the user
        :param topics: iterable of topics to add
        """
        for topic in topics:
            self.cur.execute("INSERT INTO user_topics VALUES (?, ?)", (username, topic))
        self.conn.commit()

    def _remove_user_topics(self, username, topics):
        """
        Removes topics from a user's preferences
        :param username: Username of the user
        :param topics: iterable of topics to remove
        """
        for topic in topics:
            self.cur.execute("DELETE FROM user_topics WHERE username = ? AND topic = ?", (username, topic))
        self.conn.commit()

    def get_user_topics(self, username):
        """
        Retrieves all topics associated with a user
        :param username: Username of the user
        :return: List of topics
        """
        self.cur.execute("SELECT topic FROM user_topics WHERE username = ?", (username,))
        topics = self.cur.fetchall()
        return [t[0] for t in topics]

    def set_user_topics(self, username, new_topics):
        """
        Updates a user's topics by adding new ones and removing old ones
        :param username: Username of the user
        :param new_topics: list of new topics to set
        """
        old_topics = self.get_user_topics(username)
        to_add_topics = set(new_topics) - set(old_topics)
        to_remove_topics = set(old_topics) - set(new_topics)

        self._add_user_topics(username, to_add_topics)
        self._remove_user_topics(username, to_remove_topics)

    # ===== Watched videos =====

    def add_watched_video(self, username, video_id):
        """
        Adds a record of a user watching a video
        :param username: Username of the user
        :param video_id: ID of the watched video
        """
        self.cur.execute("INSERT INTO watched_videos VALUES (?,?)", (username, video_id))
        self.conn.commit()

    def get_watched_videos(self, username):
        """
        Retrieves all videos watched by a user
        :param username: Username of the user
        :return: List of video IDs watched by the user
        """
        self.cur.execute("SELECT video_id FROM watched_videos WHERE username = ?", (username,))
        return self.cur.fetchall()

    def get_amount_of_views(self, video_id):
        """
        Counts how many times a video has been watched
        :param video_id: ID of the video
        :return: Number of views for the video
        """
        self.cur.execute("SELECT COUNT(*) FROM watched_videos WHERE video_id = ?", (video_id,))
        return self.cur.fetchone()[0]

    def has_watched_video(self, username, video_id):
        """
        Checks if a user has watched a specific video
        :param username: Username of the user
        :param video_id: ID of the video
        :return: True if the user has watched the video, False otherwise
        """
        self.cur.execute("SELECT 1 FROM watched_videos WHERE username = ? AND video_id = ?", (username, video_id))
        return self.cur.fetchone() is not None

    def order_ids_by_views(self, video_ids):
        """
        Orders a list of video IDs by their view count in descending order
        :param video_ids: iterable of video IDs to sort
        :return: List of video IDs sorted by views
        """
        video_ids = list(video_ids)
        results = []
        if video_ids:
            ids_query_insert_placeholder = ",".join("?" * len(video_ids))
            self.cur.execute(f"""

            SELECT videos.video_id, COUNT(watched_videos.username) AS views
            FROM videos LEFT JOIN watched_videos ON videos.video_id = watched_videos.video_id
            WHERE videos.video_id IN ({ids_query_insert_placeholder})
            GROUP BY videos.video_id
            ORDER BY views DESC

            """, (*video_ids,))

            results = self.cur.fetchall()
            results = [i[0] for i in results]

        return results

    def videos_user_has_not_watched(self, username, video_ids):
        """
        Filters out videos that a user has already watched
        :param username: Username of the user
        :param video_ids: iterable of video IDs to check
        :return: a list of video IDs the user has not watched
        """
        result_ids = []
        if video_ids:
            potential_videos_ids_placeholder = ",".join("?" * len(video_ids))
            self.cur.execute(f"""SELECT videos.video_id FROM videos
             LEFT JOIN watched_videos ON videos.video_id = watched_videos.video_id AND watched_videos.username = ?
              WHERE videos.video_id IN ({potential_videos_ids_placeholder}) AND watched_videos.video_id IS NULL""",
                             (username, *video_ids))

            result_ids = self.cur.fetchall()
            result_ids = [x[0] for x in result_ids]

        return result_ids

    def remove_watched_videos_for_user(self, username):
        self.cur.execute("DELETE FROM watched_videos WHERE username = ?", (username, ))

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

    # ===== reports =====

    def set_report_notified(self, username, id, type):
        """
        Sets a report as notified.
        :param username: Username of the user who reported
        :param id: ID of the target (video or comment)
        :param type: Type of the target (VIDEO_REPORT or COMMENT_REPORT)
        """
        self.cur.execute(
            "UPDATE reports SET notified = 1 WHERE reporter_name = ? AND target_id = ? AND target_type = ?",
            (username, id, type))
        self.conn.commit()

    def has_user_reported(self, username, id, type):
        """
        Checks if a user has already reported a specific target
        :param username: Username of the reporter
        :param id: ID of the reported target
        :param type: Type of the target
        :return: True if the user has reported, False otherwise
        """
        self.cur.execute("SELECT 1 FROM reports WHERE reporter_name = ? AND target_id = ? AND target_type = ?",
                         (username, id, type))
        return self.cur.fetchone() is not None

    def add_report(self, reporter_name, target_id, target_type):
        """
        Adds a report to the database.
        :param reporter_name: Name of the user reporting
        :param target_id: ID of the video or comment being reported
        :param target_type: Type of the target (VIDEO_REPORT or COMMENT_REPORT)
        :return: Inserts a new row into the reports table
        """
        self.cur.execute("INSERT INTO reports (reporter_name, target_id, target_type) VALUES (?,?,?)",
                         (reporter_name, target_id, target_type))
        self.conn.commit()

    def get_report_status_and_created_at(self, username, target_id, target_type):
        """
        Retrieves the status and creation time of a specific report
        :param username: Username of the reporter
        :param target_id: ID of the reported target
        :param target_type: Type of the target
        :return: Tuple containing status and formatted creation time
        """
        self.cur.execute(
            "SELECT status, strftime('%d/%m/%Y %H:%M', created_at) FROM reports WHERE target_id = ? AND target_type = ? AND reporter_name = ?",
            (target_id, target_type, username))
        return self.cur.fetchone()

    def get_reports(self):
        """
        Retrieves all reports from the database.
        :return: Returns all reports from the reports table
        """
        self.cur.execute("""SELECT target_id, target_type, COUNT(*) AS reports_amount
                            FROM reports
                            GROUP BY target_id, target_type
                            ORDER BY reports_amount DESC""")

        # self.cur.execute("SELECT * FROM reports")
        return self.cur.fetchall()

    def get_report_usernames_and_times(self, target_id, target_type):
        """
        Retrieves all reporters and report times for a specific target
        :param target_id: ID of the reported target
        :param target_type: Type of the target
        :return: List of tuples containing reporter usernames and times
        """
        self.cur.execute(
            "SELECT reporter_name, strftime('%d/%m/%Y %H:%M', created_at) FROM reports WHERE (target_id, target_type) = (?,?)",
            (target_id, target_type))
        return self.cur.fetchall()

    def get_reporters(self, target_id, target_type):
        """
        Retrieves usernames of all users who reported a specific target
        :param target_id: ID of the reported target
        :param target_type: Type of the target
        :return: List of reporter usernames
        """
        self.cur.execute(
            "SELECT reporter_name FROM reports WHERE (target_id, target_type) = (?,?)",
            (target_id, target_type))
        res = self.cur.fetchall()
        if res:
            res = [i[0] for i in res]
        return res

    def set_report_status(self, target_id, target_type, status):
        """
        Updates the status of reports for a specific target
        :param target_id: ID of the reported target
        :param target_type: Type of the target
        :param status: New status to set
        """
        self.cur.execute("UPDATE reports SET status = ? WHERE (target_id, target_type) = (?,?)",
                         (status, target_id, target_type))
        self.conn.commit()

    def get_not_notified_reports(self, username):
        """
        Retrieves reports that have not yet been notified to the user
        :param username: Username of the reporter
        :return: List of pending report notifications
        """
        self.cur.execute(
            "SELECT target_id, target_type, reporter_name FROM reports WHERE reporter_name = ? and status IS NOT NULL and notified = 0",
            (username,))
        return self.cur.fetchall()

    def delete_report(self, username, id, type):
        """
        Deletes a report from the database.
        :param username: The username of the reporter.
        :param id: The ID of the target
        :param type: The type of the target (0 for comment or 1 for video).
        :return: Deletes a report from the reports table
        """
        self.cur.execute("DELETE FROM reports WHERE reporter_name = ? AND target_id = ? AND target_type  = ?", (username, id, type))
        self.conn.commit()

    def is_report_concluded(self, id, type):
        """
        Checks if a report has been concluded (has a status)
        :param id: ID of the reported target
        :param type: Type of the target
        :return: True if the report has a status, False otherwise
        """
        self.cur.execute("SELECT 1 FROM reports WHERE target_id = ? AND target_type = ? AND status IS NOT NULL",
                         (id, type))
        return self.cur.fetchone() is not None

    # ===== system_managers =====
    def add_system_manager(self, username):
        """
        Adds a user as a system manager
        :param username: Username to promote
        """
        self.cur.execute("INSERT INTO system_managers (username) VALUES (?)", (username,))
        self.conn.commit()

    def is_system_manager(self, username):
        """
        Checks if a user is a system manager
        :param username: Username to check
        :return: True if the user is a system manager, False otherwise
        """
        self.cur.execute("SELECT 1 FROM system_managers WHERE username=?", (username,))
        return self.cur.fetchone() is not None

    def get_system_managers(self):
        """
        Retrieves all system managers
        :return: List of usernames of system managers
        """
        self.cur.execute("SELECT username FROM system_managers")
        return [row[0] for row in self.cur.fetchall()]


if __name__ == "__main__":
    db = DataBase()

    # db.print_tables()
    print("\n\n")

    # --- testing ---



    # # --- users ---
    db.cur.execute("DROP TABLE IF EXISTS users")
    db._create_users_table()
    # db.add_user("Barak", "barak@gmail.com", "482c811da5d5b4bc6d497ffa98491e38")
    # db.add_user("Alon", "alon@gmail.com",   "482c811da5d5b4bc6d497ffa98491e38")
    # db.add_user("Ella", "ella@gmail.com",   "482c811da5d5b4bc6d497ffa98491e38")

    # # --- videos ---
    # db.cur.execute("DROP TABLE IF EXISTS videos")
    # db._create_videos_table()
    # db.add_video("Alon", "Alon's video 3", "Video about Alon 3", "test link1")
    # db.add_video("Barak", "Barak's video", "Video about Barak", "test link2")
    # db.add_video("Ella", "Ella's video", "Video about Ella", "test link3")
    # db.add_video("Ella", "Ella's video 2", "Video about Ella 2 ", "test link4")
    # db.add_video("Ella", "Ella's video 2", "Video about Ella 2", "test link5")

    # db.delete_video(5)
    # # --- comments ---
    # db.cur.execute("DROP TABLE IF EXISTS comments")
    # db._create_comments_table()
    # db.add_comment(1, "Barak", "Barak comments on 1")
    # db.add_comment(1, "Alon", "Alon comments on 1")
    # db.add_comment(2, "Alon", "Alon comments on 2")

    # print(db.get_comments(1))

    # # --- likes ---
    # db.cur.execute("DROP TABLE IF EXISTS likes")
    # db._create_likes_table()
    # db.add_video_like(1, "Barak")
    # db.add_video_like(1, "Alon")
    # db.add_video_like(2, "Alon")

    # # --- following ---
    # db.cur.execute("DROP TABLE IF EXISTS following")
    # db._create_following_table()
    # db.add_following("Barak", "Alon")
    # db.add_following("Alon", "Barak")

    # # --- video_topics ---
    # db.cur.execute("DROP TABLE IF EXISTS video_topics")
    # db._create_video_topics_table()
    # db.add_video_topics(1, [15,23,3])
    # db.add_video_topics(2, [2,5,4])
    # db.add_video_topics(3,[2,3])
    # db.add_video_topics(4,[2,5])
    # db.add_video_topics(5,[15])
    # print("video_id: ",db.get_video_for_user("Barak", [7]))
    # print("video_id:", db.get_most_viewed_video_for_user("Barak"))
    # # --- user_topics ---
    # db.cur.execute("DROP TABLE IF EXISTS user_topics")
    # db._create_user_topics_table()
    # db.set_user_topics("Barak", [5])
    # db.set_user_topics("Alon", [4,5,6])

    # # --- watched_videos ---
    # db.cur.execute("DROP TABLE IF EXISTS watched_videos")
    # db._create_watched_videos_table()
    # db.add_watched_video("Ella", 5)

    # # --- video_hashes ---
    # db.cur.execute("DROP TABLE IF EXISTS video_hashes")
    # db._create_video_hashes_table()
    # if not db.hash_exists("abc123"):
    #     db.add_video_hash(1, "abc123")
    #
    # print("Hash exists:", db.hash_exists("abc123"))

    # # --- reports ---
    # db.cur.execute("DROP TABLE IF EXISTS reports")
    # db._create_reports_table()
    # db.add_report("Alon",1,0)
    # db.set_report_status(1,0, 0)
    # db.add_report("Alon",1,0)
    # db.add_report("Ella",1,0)
    # db.add_report("Barak",1,1)
    # db.add_report("Alon",2,1)
    # db.add_report("Ella",1,1)

    # print("get reports:")
    # print(db.get_reports())

    # print(db.get_reporters(1,0))

    # # --- system_managers ---
    # db.cur.execute("DROP TABLE IF EXISTS system_managers")
    # db._create_system_managers_table()
    # db.add_system_manager("Barak")

    # print(db.get_system_managers())

    db.print_tables()
    db.close()
