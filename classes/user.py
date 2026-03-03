

class User:

    def __init__(self, username, followers_amount, followings_amount, video_amount, email = None, topics=None, followings=None):
        if followings is None:
            followings = []

        if topics is None:
            topics = []

        self.username = username
        self.followers_amount = followers_amount
        self.followings_amount = followings_amount
        self.video_amount = video_amount

        # saved for current user only
        self.email = email
        self.topics = topics
        self.followings = followings

    def __str__(self):
        return f"username='{self.username}'\nfollowers_amount={self.followers_amount}\nfollowings_amount={self.followings_amount}\nvideo_amount={self.video_amount}\nemail='{self.email}'\nfollowings={self.followings}\ntopics={self.topics}"
