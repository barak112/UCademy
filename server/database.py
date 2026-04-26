import sqlite3
from datetime import datetime


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

    def print_tables(self):
        """
        Print the first 40 rows of every table in the database for debugging purposes.
        """
        self.cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in self.cur.fetchall()]

        for table in tables:
            print(f"\nTable: {table}")
            self.cur.execute(f"SELECT * FROM {table} LIMIT 40;")
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
                created_at TIMESTAMP DEFAULT (datetime('now','localtime')),
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

    def is_correct_username_and_password_hash(self, username, password_hash):
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

    def get_similar_usernames(self, username):
        """
        Retrieves users whose usernames contain the username inputted
        :param username: Username to check
        :return: List of matching usernames
        """
        self.cur.execute("SELECT username FROM users WHERE username LIKE ? COLLATE NOCASE", ("%" + username + "%",))
        res = self.cur.fetchall()
        if res:
            res = [i[0] for i in res]
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
        :return: video details: creator, name, description, created_at, likes_amount, comments_amount
        """
        query = """
                         SELECT videos.creator,
                                videos.name,
                                videos.description,
                                strftime('%d/%m/%Y %H:%M', videos.created_at),
                               (SELECT COUNT(*) FROM likes WHERE video_id = videos.video_id) AS likes_count,
                               (SELECT COUNT(*) FROM comments WHERE video_id = videos.video_id) AS comments_count
                         FROM videos

                         WHERE videos.video_id = ?
                         """
        if matter_deleted:
            query += "AND videos.deleted = 0"

        print("video id in get specific video: ", video_id)
        self.cur.execute(query, (video_id,))

        ret_val = self.cur.fetchone()
        return ret_val


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

    def search_videos(self, name_or_desc, topics):
        query = """SELECT videos.video_id,
            
            (
            CASE WHEN videos.name LIKE ? THEN 2 ELSE 0 END +
            CASE WHEN videos.description LIKE ? THEN 1 ELSE 0 END
            ) AS score,
            
            COUNT(DISTINCT watched_videos.username) AS views
            
            FROM videos
            LEFT JOIN watched_videos ON videos.video_id = watched_videos.video_id
            """

        if topics:
            placeholders = ("?," * len(topics))[:-1]
            query+= f"""
            JOIN video_topics ON videos.video_id = video_topics.video_id 
             AND video_topics.topic IN ({placeholders})
            """

        query += """
            WHERE videos.deleted = 0
            GROUP BY videos.video_id
            HAVING score > 0
            ORDER BY score DESC, views DESC
            """
        params = [f"%{name_or_desc}%", f"%{name_or_desc}%"]
        if topics:
            params.extend(topics)

        self.cur.execute(query, params)

        res = self.cur.fetchall()
        res = [i[0] for i in res]
        return res


    def get_best_like_views_ratio_video_for_user(self, username):
        """
        Retrieves the most viewed video the user has not watched yet.
        :param username: Username of the viewer
        :return: Video ID of the most viewed unseen video or None
        """
        self.cur.execute("""
                         SELECT videos.video_id,
                         
                         CASE 
                            WHEN COUNT(DISTINCT watched_videos.username) < 10 THEN 0.5
                            ELSE CAST(COUNT(DISTINCT likes.username) AS FLOAT) /
                            NULLIF(COUNT(DISTINCT watched_videos.username), 0)
                         END AS likes_views_ratio
                   
                         FROM videos
                                  LEFT JOIN watched_videos ON videos.video_id = watched_videos.video_id
                                  LEFT JOIN likes ON videos.video_id = likes.video_id

                         WHERE videos.deleted = 0
                           AND NOT EXISTS (SELECT 1
                                           FROM watched_videos
                                           WHERE watched_videos.video_id = videos.video_id
                                             AND watched_videos.username = ?)

                         GROUP BY videos.video_id
                         ORDER BY likes_views_ratio DESC

                         """, (username,))

        res = self.cur.fetchone()
        if res:
            res = res[0]
        return res

    # ===== comments =====

    def add_comment(self, video_id, commenter_name, comment):
        """
        Adds a new comment to a video
        :param video_id: ID of the video the comment belongs to
        :param commenter_name: the username of the person adding the comment
        :param comment: the content of the comment
        :return: ID of the newly inserted comment
        """
        self.cur.execute("INSERT INTO comments (video_id, commenter, comment) VALUES (?,?,?) RETURNING comment_id, created_at",
                         (video_id, commenter_name, comment))
        comment_id, created_at = self.cur.fetchone()
        self.conn.commit()
        created_at = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
        created_at = created_at.strftime("%d/%m/%Y %H:%M")

        return comment_id, created_at

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
        if self.comment_exists(comment_id) and not (matter_deleted and self.is_comment_deleted(comment_id)):
            self.cur.execute(
                "SELECT comment_id, video_id, commenter, comment, strftime('%d/%m/%Y %H:%M', created_at) FROM comments WHERE comment_id = ?",
                (comment_id,))
            res = self.cur.fetchone()
        return res

    def is_comment_deleted(self, comment_id):
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
        Retrieves a recommended video for a user based on shared topics and likes to views ratio
        :param username: Username of the user
        :return: Video ID if found, otherwise None
        """
        self.cur.execute("""
                         SELECT video_topics.video_id,
                                COUNT(DISTINCT video_topics.topic)      AS shared_topics,
                                
                               CASE 
                                   WHEN COUNT(DISTINCT watched_videos.username) < 10 THEN 0.5
                                   ELSE CAST(COUNT(DISTINCT likes.username) AS FLOAT) /
                                        NULLIF(COUNT(DISTINCT watched_videos.username), 0)
                               END AS likes_views_ratio

                         FROM user_topics
                                  LEFT JOIN video_topics ON user_topics.topic = video_topics.topic
                                  LEFT JOIN watched_videos ON video_topics.video_id = watched_videos.video_id
                                  LEFT JOIN likes ON video_topics.video_id = likes.video_id
                                
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
                         ORDER BY shared_topics + likes_views_ratio*5 DESC
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
            placeholders = ("?," * len(filter))[:-1]
            self.cur.execute(
                f"""
                SELECT video_topics.video_id, 
                   COUNT(video_topics.topic) AS shared_topics,
                   
                   CASE 
                       WHEN COUNT(DISTINCT watched_videos.username) < 10 THEN 0.5
                       ELSE CAST(COUNT(DISTINCT likes.username) AS FLOAT) /
                            NULLIF(COUNT(DISTINCT watched_videos.username), 0)
                   END AS likes_views_ratio
                
                    
                FROM video_topics
                  LEFT JOIN watched_videos ON video_topics.video_id = watched_videos.video_id
                  LEFT JOIN likes ON video_topics.video_id = likes.video_id
                                
                WHERE EXISTS(
                    SELECT 1 FROM videos
                    WHERE videos.video_id = video_topics.video_id AND deleted = 0
                )
                AND video_topics.topic IN ({placeholders})
                AND NOT EXISTS (
                    SELECT 1 FROM watched_videos 
                    WHERE watched_videos.video_id = video_topics.video_id AND watched_videos.username = ?
                )
                GROUP BY video_topics.video_id
                ORDER BY shared_topics + likes_views_ratio*5 DESC
            """, (*filter, username))

            res = self.cur.fetchone()
            if res:
                res = res[0]
        return res

    def get_video_for_user(self, username, filter=None):
        """
        Retrieves video_id of a recommended video for a user based on filters, topics, or popularity
        :param username: Username of the user
        :param filter: optional list of topics to filter videos
        :return: Video ID of the recommended video
        """
        # returns the best video for the user that he has not seen

        res = None
        print(filter, bool(filter))
        if filter:
            res = self.get_video_for_user_filter(username, filter)

        if not res: # if not filter or no videos matching filter
            res = self.get_video_for_user_topics(username)

        if not res:  # if no video matches filter or topics
            res = self.get_best_like_views_ratio_video_for_user(username)

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

    # print(db.search_videos("ella", []))

    # # --- users ---
    # db.cur.execute("DROP TABLE IF EXISTS users")
    # db._create_users_table()
    # db.add_user("Barak", "barak@gmail.com", "5f4dcc3b5aa765d61d8327deb882cf99") # password = password
    # db.add_user("Alon", "alon@gmail.com",   "5f4dcc3b5aa765d61d8327deb882cf99")
    # db.add_user("Ella", "ella@gmail.com",   "5f4dcc3b5aa765d61d8327deb882cf99")

    # # --- videos ---
    db.cur.execute("DROP TABLE IF EXISTS videos")
    db._create_videos_table()
    # db.add_video("Alon", "Alon's video 3", "Video about Alon 3", "test link1")
    # db.add_video("Barak", "Barak's video", "Video about Barak", "test link2")
    desc = "Welcome back to the channel, food lovers, flavor chasers, and culinary adventurers from every corner of the globe! Today we are doing something absolutely incredible, something that is going to completely blow your mind, change the way you think about lunchtime forever, and honestly might just become your new all-time favorite thing to make in the kitchen. That's right — we are making the one, the only, the legendary, the jaw-dropping, the utterly irresistible SUSHI SANDWICH. You heard that correctly. We are taking everything you know and love about traditional Japanese sushi — the perfectly seasoned rice, the fresh sliced fish, the creamy avocado, the crisp cucumber, the rich umami flavors — and we are combining it with the most universally beloved lunch format known to humankind: the classic, handheld, easy-to-eat sandwich. The result? Pure, absolute, unhinged culinary genius. Now, you might be sitting there thinking — in its more traditional form, has been taking the internet, food blogs, bento boxes, and trendy café menus completely by storm over the past few years, and once you try it, you will completely understand why. This is not a gimmick. This is not a weird food mashup that sounds cool but tastes terrible. This is a genuinely, deeply, profoundly delicious eating experience that you absolutely owe it to yourself to try at least once — though we promise, once will never be enough. So what exactly goes into a sushi sandwich? Great question, and we are so glad you asked, because this is where things get really exciting. At its core, the sushi sandwich is built on a foundation of perfectly cooked Japanese short-grain rice that has been seasoned with the holy trinity of sushi rice flavoring: rice vinegar, sugar, and salt. This rice is the backbone of the entire dish. It needs to be sticky enough to hold together when you slice through it, fluffy enough to not feel like a dense brick in your mouth, and flavorful enough to complement every single ingredient layered on top of it. Getting the rice right is the most important step in this entire recipe, and we are going to walk you through it in complete, exhaustive, foolproof detail so that even if you have never cooked a single grain of sushi rice in your entire life, you will nail it on your very first try. Once your rice is ready, the real fun begins — and that's the assembly. We're talking layers, people. Beautiful, colorful, flavor-packed layers. First, we lay down a sheet of nori — that's the toasted seaweed that gives sushi its signature oceanic, slightly smoky, deeply savory flavor. Then comes a thick, even layer of that gorgeous sushi rice. Then we start piling on the fillings, and oh boy, are we going all out today. We've got silky, sashimi-grade fresh salmon that practically melts on your tongue. We've got buttery, ripe avocado sliced thin and fanned out like a little green sunset. We've got crisp, refreshing cucumber cut into matchsticks for that essential crunch. We've got fluffy, sweet crab salad mixed with just a touch of Japanese mayo — that's the Kewpie brand, for those of you who don't know, and if you haven't experienced Kewpie mayo yet, please stop everything you are doing and go get some immediately, because it will change your life. We've got pickled daikon radish for a little tang and brightness. We've got thin slices of creamy, spicy tuna mix for an extra punch of flavor. And to finish it all off, we are drizzling on a homemade spicy sriracha mayo and a little drizzle of soy sauce glaze that ties every single element together into one perfect, cohesive, harmonious bite. Then — and this is the most satisfying part of the entire process — we wrap the whole thing tightly in plastic wrap, press it gently so everything melds together, and then we slice it right down the middle to reveal that absolutely stunning cross-section. If you've ever seen one of those viral sushi sandwich videos online where you watch the knife cut through and every single layer is perfectly visible and it just looks like edible art — that is exactly what we are going for today. And trust us, when you finally cut into yours and see those layers of rice, fish, avocado, and cucumber stacked up like a masterpiece, you are going to feel like the most talented chef on the entire planet, and you will absolutely deserve that feeling. But we don't stop there, because this video is not just a recipe video — it's a complete deep dive into the world of sushi sandwiches. We're going to talk about the history and origins of this dish, tracing it back to Japanese convenience stores and bento culture, explaining how the humble onigirazu evolved over the decades and eventually exploded into the global food scene. We're going to talk about all the different variations you can make — the vegetarian version loaded with roasted sweet potato, avocado, and pickled vegetables; the classic spicy tuna version for those of you who like a little heat; the breakfast version with tamagoyaki (that's Japanese rolled egg omelette) and fresh cucumber; the super indulgent wagyu beef version for special occasions; and even a dessert sushi sandwich version featuring sweet rice, fresh mango, and coconut cream that is honestly out of this world. We're also going to give you our top tips and tricks for making the perfect sushi sandwich every single time, no matter your skill level. We'll talk about how to choose the freshest fish at the market, what to look for, what to avoid, and how to store it properly. We'll explain the difference between various types of soy sauce and when to use each one. We'll go over all the essential tools you need — and, more importantly, the tools you absolutely don't need, because we believe great food should be accessible to everyone, not just people with fancy, expensive kitchen gadgets. We'll answer the most frequently asked questions about sushi sandwiches, like: Can I make this ahead of time? How do I keep the nori from getting soggy? What's the best way to pack it for lunch? Can I freeze it? Is it safe to eat raw fish at home? And so much more. And for those of you who are nervous about working with raw fish — first of all, we totally understand, and we respect that concern — we've got a whole section of this video dedicated to cooked and pescatarian-friendly alternatives that are just as delicious, just as beautiful, and just as satisfying as the raw fish versions. Shrimp tempura sushi sandwiches, anyone? Or how about a teriyaki chicken sushi sandwich with a sweet and sticky glaze, crunchy cabbage slaw, and a swipe of wasabi mayo? These options are absolutely incredible, incredibly easy to make, and guaranteed to convert even the most sushi-skeptical person in your household into a total believer. We're also going to take a little detour in this video to talk about the broader world of Japanese sandwich culture, because it is genuinely one of the most fascinating and delicious culinary traditions in the entire world. Japan takes sandwiches incredibly seriously. From the iconic tamago sando (that pillowy egg salad sandwich on crustless milk bread that has become one of the most beloved food trends of the decade) to the fruit sando (yes, a sandwich filled with whipped cream and fresh fruit that is somehow one of the best things you'll ever eat in your life), Japanese sandwich culture is rich, creative, meticulous, and completely worth exploring. Understanding this context will make you appreciate your sushi sandwich on a whole new level, and we think you're really going to enjoy this little food history journey we're taking together. By the end of this video, you're going to walk away with a complete, detailed, easy-to-follow recipe for the most incredible sushi sandwich you've ever tasted. You're going to have a full toolkit of tips, tricks, and variations to make this dish your own. You're going to have a deeper appreciation for Japanese food culture and the beautiful creativity that drives it. And most importantly, you're going to have a dish that will absolutely impress anyone you make it for — whether that's your family at the dinner table, your coworkers at a lunch potluck, your friends at a party, or just yourself on a quiet afternoon when you want to make something special and treat yourself to a truly extraordinary meal. So if you're as excited as we are — and we know you are, because how could you not be — make sure you hit that LIKE button, leave us a comment down below telling us which sushi sandwich variation you're most excited to try, and SUBSCRIBE to the channel so you never miss a single video. We post new recipes, food history deep dives, kitchen tips, and culinary adventures every single week, and we would absolutely love to have you as part of this community. Now, let's stop talking and start cooking — because your ultimate sushi sandwich is waiting, and trust us, it is so worth it. Let's go"
    # db.add_video("Ella", "Ella's video", desc, "test link3")
    # db.add_video("Ella", "Ella's video 2", "Video about Ella 2 ", "test link4")
    # db.add_video("Ella", "Ella's video 2", "Video about Ella 2", "test link5")

    db.add_video("Barak", "Alon's video 3", "Video about Alon 3", "test link1")
    db.add_video("Barak", "Barak's video", "Video about Barak", "test link2")
    db.add_video("Barak", "Ella's video", desc, "test link3")
    db.add_video("Barak", "Ella's video 2", "Video about Ella 2 ", "test link4")
    db.add_video("Barak", "Ella's video 2", "Video about Ella 2", "test link5")
    db.add_video("Barak", "Ella's video 2", "Video about Ella 2", "test link5")
    db.add_video("Barak", "Ella's video 2", "Video about Ella 2", "test link5")


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
    # db.add_video_topics(4,[15])

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
