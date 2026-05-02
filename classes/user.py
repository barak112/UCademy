

class User:

    def __init__(self, username, followers_amount, followings_amount, videos_ids, email = None, topics=None, followings=None):
        """
        Represents a user's profile with relevant social metrics and optional additional details.

        The class includes information about the user's social footprint, such as the number of
        followers, following users, and published videos.

        Current user info also includes email, topics list and followings list

        :param username: The user's name.
        :param followers_amount: The number of the user's followers.
        :param followings_amount: The number of users that the user follows.
        :param videos_ids: The ids of the videos this user has uploaded.
        :param email: (Optional) The email associated with the current user.
        :param topics: (Optional) A list of topics the current user is interested in.
        :param followings: (Optional) A list of other users that the current user is following.
        """
        if followings is None:
            followings = []

        if topics is None:
            topics = []

        self.username = username
        self.followers_amount = followers_amount
        self.followings_amount = followings_amount
        self.videos_ids = videos_ids

        # saved for current user only
        self.email = email
        self.topics = topics
        self.followings = followings

    def get_video_amount(self):
        """
        Calculates and retrieves the total number of video identifiers.
        :return: The total count of videos this user has uploaded.
        """
        return len(self.videos_ids)
