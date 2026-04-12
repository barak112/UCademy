


class Comment:

    def __init__(self, comment_id, comment, commenter, created_at):
        """
        Initializes a new instance of the class with the provided comment information.
        :param comment_id: Unique identifier for the comment.
        :param comment: Text content of the comment.
        :param commenter: Name of the individual who made the comment.
        :param created_at: Timestamp representing when the comment was created. formatted hh:mm
        """
        self.comment_id = comment_id
        self.comment = comment
        self.commenter = commenter
        self.created_at = created_at

        #todo add liked by user attribute
