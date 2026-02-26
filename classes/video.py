class Video:
    def __init__(self, video_id, creator, video_name, video_desc, amount_of_likes, amount_of_comments, liked, video_link = None):
        self.video_id = video_id
        self.creator = creator
        self.comments = []
        self.video_name = video_name
        self.video_desc = video_desc
        self.amount_of_likes = amount_of_likes
        self.amount_of_comments = amount_of_comments
        self.liked = liked
        self.video_link = video_link

    def add_comment(self, comment):
        self.comments.append(comment)

    def set_comments(self, comments):
        self.comments = comments

    def get_comments(self):
        return self.comments
