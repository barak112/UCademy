

class User:

    def __init__(self, username, email, topics=None, followings=None):
        if followings is None:
            followings = []

        if topics is None:
            topics = []

        self.username = username
        self.email = email
        self.followings = followings
        self.topics = topics
        
    def __str__(self):
        return f"username='{self.username}'\nemail='{self.email}'\nfollowings={self.followings}\ntopics={self.topics}"
