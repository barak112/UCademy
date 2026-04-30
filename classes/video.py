from typing import Any

import comment


class Video:
    def __init__(self, video_id, creator, video_name, video_desc, created_at, amount_of_likes, amount_of_comments, liked, test_link = None):
        """
        Initializes the Video object with the given attributes.

        :param video_id: The unique identifier of the video.
        :param creator: The creator of the video.
        :param video_name: The title of the video.
        :param video_desc: The description of the video content.
        :param created_at: The timestamp indicating when the video was created. formatted hh:mm
        :param amount_of_likes: The number of likes the video has received.
        :param amount_of_comments: The number of comments associated with the video.
        :param liked: Indicates whether the current user has liked the video.
        :param test_link: Optional. The URL link to access the video's test.
        """
        self.video_id = video_id
        self.creator = creator
        self.comments = {}
        self.video_name = video_name
        self.video_desc = video_desc
        self.created_at = created_at
        self.amount_of_likes = amount_of_likes
        self.amount_of_comments = amount_of_comments
        self.liked = liked
        self.test_link = test_link

    def add_comment_at_start(self, comment : comment.Comment):
        """adds a comment to this video's comments list"""
        self.comments = {
            comment.comment_id: comment,
            **self.comments
        }
        self.amount_of_comments+=1

    def add_comments(self, comments : list[comment.Comment]):
        """adds multiple comments to this video's comments list"""
        self.comments.update({comment.comment_id : comment for comment in comments})

    # def get_comments(self) -> dict[int, comment.Comment]:
    #     """returns a list of comments associated with this video"""
    #     return self.comments

    def get_comments(self) -> list[comment.Comment]:
        """returns a list of comments associated with this video"""
        return list(self.comments.values())

