


class Video:

    def __init__(self, video_id, comments, video_name, video_desc, amount_of_likes, amount_of_comments, liked):
        self.video_id = video_id
        self.comments = comments
        self.video_name = video_name
        self.video_desc = video_desc
        self.amount_of_likes = amount_of_likes
        self.amount_of_comments = amount_of_comments
        self.liked = liked


    def add_comment(self, comment):
        self.comments.append(comment)
