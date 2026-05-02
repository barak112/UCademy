def build_command(command, params):
    """Build a command string using an opcode and parameters.

    Joins parameters with '@#' delimiter and prepends the command opcode.

    :param command: The opcode for the command.
    :param params: List of parameters for the command.
    :return: Formatted command string.
    """
    while params and params[-1] is None:  # remove None at the end of params
        params.pop()

    for index, value in enumerate(params):
        if isinstance(value, (list, tuple)):
            value = [str(i) for i in value]
            params[index] = "#@".join(value)

    params = [str(i) for i in params]
    return str(command).zfill(2) + "@#".join(params)


def build_sign_up_status(status):
    """
        Builds a response command indicating the result of a sign-up attempt.
    :param status: A list of status codes for username, password, and email validation.
    :return: Formatted sign-up status command string.
    """
    return build_command(0, [status])


def build_email_verification_confirmation(status, username=None, email=None, port=None):
    """
        Builds a response command confirming the result of an email verification attempt.
    :param status: The status code of the verification result.
    :param username: The username of the verified user, if successful.
    :param email: The email address of the verified user, if successful.
    :param port: The video communication port assigned to the client, if successful.
    :return: Formatted email verification confirmation command string.
    """
    return build_command(1, [status, username, email, port])


def build_sign_in_status(status, port=None, username=None, followers_amount=None,
                         followings_amount=None, videos_ids=None, email=None, topics=None, followings_names=None):
    """
        Builds a response command indicating the result of a sign-in attempt.
    :param status: The status code of the sign-in result (0 for failure, 1 for success).
    :param port: The video communication port assigned to the client, if successful.
    :param username: The username of the signed-in user, if successful.
    :param followers_amount: The number of followers the user has.
    :param followings_amount: The number of users the client is following.
    :param videos_ids: List of video IDs uploaded by the user.
    :param email: The email address of the signed-in user.
    :param topics: List of topic preferences associated with the user.
    :param followings_names: List of usernames the user is following.
    :return: Formatted sign-in status command string.
    """
    return build_command(2, [status, port, username, followers_amount, followings_amount, videos_ids, email, topics,
                             followings_names])


def build_set_topics_confirmation(topics):
    """
        Builds a response command confirming that a user's topics have been updated.
    :param topics: The updated list of topics assigned to the user.
    :return: Formatted set-topics confirmation command string.
    """
    return build_command(3, [topics])


def build_set_filter_confirmation(filter):
    """
        Builds a response command confirming that a user's topic filter has been updated.
    :param filter: The updated list of topics used as the active filter.
    :return: Formatted set-filter confirmation command string.
    """
    return build_command(4, [filter])


def build_user_details_in_search(username, followers_amount, followings_amount, videos_ids):
    """
        Builds a response command containing a user's details for display in search results.
    :param username: The username of the user.
    :param followers_amount: The number of followers the user has.
    :param followings_amount: The number of users the user is following.
    :param videos_ids: List of video IDs uploaded by the user.
    :return: Formatted user-details-in-search command string.
    """
    return build_command(
        5,
        [username, followers_amount, followings_amount, videos_ids]
    )


def build_video_details_in_search(video_id, creator_name, video_name, video_desc, created_at, likes_amount,
                                  comments_amount, liked):
    """
        Builds a response command containing a video's details for display in search results.
    :param video_id: The unique ID of the video.
    :param creator_name: The username of the video's creator.
    :param video_name: The title of the video.
    :param video_desc: The description of the video.
    :param created_at: The formatted creation timestamp of the video.
    :param likes_amount: The number of likes the video has received.
    :param comments_amount: The number of comments on the video.
    :param liked: Integer indicating whether the requesting user has liked the video (1 or 0).
    :return: Formatted video-details-in-search command string.
    """
    return build_command(
        6,
        [video_id, creator_name, video_name, video_desc, created_at, likes_amount,
         comments_amount, liked]
    )


def build_comment_status(comment_id, video_id, commenter, comment, created_at):
    """
        Builds a response command confirming that a comment was successfully posted.
    :param comment_id: The unique ID of the newly created comment.
    :param video_id: The ID of the video the comment was posted on.
    :param commenter: The username of the user who posted the comment.
    :param comment: The text content of the comment.
    :param created_at: The formatted timestamp of when the comment was created.
    :return: Formatted comment-status command string.
    """
    return build_command(7, [comment_id, video_id, commenter, comment, created_at])


def build_user_details_in_profile(username, followers_amount, followings_amount, videos_ids):
    """
        Builds a response command containing a user's details for display on their profile page.
    :param username: The username of the user.
    :param followers_amount: The number of followers the user has.
    :param followings_amount: The number of users the user is following.
    :param videos_ids: List of video IDs uploaded by the user.
    :return: Formatted user-details-in-profile command string.
    """
    return build_command(8, [username, followers_amount, followings_amount, videos_ids])


def build_report_status(status, id, type, content, content_publisher, created_at=""):
    """
        Builds a response command containing the status of a report.
    :param status: The status code of the report.
    :param id: The ID of the reported target.
    :param type: The type of the reported target (0 for comment, 1 for video).
    :param content: The content of the reported item.
    :param content_publisher: The username(s) associated with the reported content.
    :param created_at: The formatted timestamp of when the report was created.
    :return: Formatted report-status command string.
    """
    return build_command(9, [status, id, type, content, content_publisher, created_at])


def build_send_comments(comments):
    """
        Builds a response command containing a batch of comments for a video.
    :param comments: A list of comment entries, each containing comment_id, video_id,
                     commenter_name, comment text, and created_at timestamp.
    :return: Formatted send-comments command string.
    """
    # comments = [[comment_id, video_id, commenter_name, comment, created_at], ...]
    return build_command(10, comments)


def build_del_video_confirmation(video_id):
    """
        Builds a response command confirming the deletion of a video.
    :param video_id: The ID of the deleted video, or 0 if deletion failed.
    :return: Formatted delete-video confirmation command string.
    """
    return build_command(11, [video_id])


def build_del_comment_confirmation(video_id=0, comment_id=0):
    """
        Builds a response command confirming the deletion of a comment.
    :param video_id: The ID of the video the comment belonged to, or 0 if deletion failed.
    :param comment_id: The ID of the deleted comment, or 0 if deletion failed.
    :return: Formatted delete-comment confirmation command string.
    """
    return build_command(12, [video_id, comment_id])


def build_video_details_in_profile(video_id, creator_name, video_name, video_desc, created_at, likes_amount,
                                   comments_amount, liked):
    """
        Builds a response command containing a video's details for display on a creator's profile.
    :param video_id: The unique ID of the video.
    :param creator_name: The username of the video's creator.
    :param video_name: The title of the video.
    :param video_desc: The description of the video.
    :param created_at: The formatted creation timestamp of the video.
    :param likes_amount: The number of likes the video has received.
    :param comments_amount: The number of comments on the video.
    :param liked: Integer indicating whether the requesting user has liked the video (1 or 0).
    :return: Formatted video-details-in-profile command string.
    """
    return build_command(
        13,
        [video_id, creator_name, video_name, video_desc, created_at, likes_amount,
         comments_amount, liked]
    )


def build_user_details_follow_list(username, followers_amount, followings_amount, videos_ids):
    """
        Builds a response command containing a user's details for display in a follow list.
    :param username: The username of the user.
    :param followers_amount: The number of followers the user has.
    :param followings_amount: The number of users the user is following.
    :param videos_ids: List of video IDs uploaded by the user.
    :return: Formatted user-details-follow-list command string.
    """
    return build_command(
        14,
        [username, followers_amount, followings_amount, videos_ids]
    )


def build_video_details(video_id, creator_name, video_name, video_desc, created_at, likes_amount,
                        comments_amount, liked):
    """
        Builds a response command containing a video's full details for playback.
    :param video_id: The unique ID of the video.
    :param creator_name: The username of the video's creator.
    :param video_name: The title of the video.
    :param video_desc: The description of the video.
    :param created_at: The formatted creation timestamp of the video.
    :param likes_amount: The number of likes the video has received.
    :param comments_amount: The number of comments on the video.
    :param liked: Integer indicating whether the requesting user has liked the video (1 or 0).
    :return: Formatted video-details command string.
    """
    return build_command(
        15,
        [video_id, creator_name, video_name, video_desc, created_at, likes_amount,
         comments_amount, liked]
    )


def build_video_upload_confirmation(video_id):
    """
        Builds a response command confirming the result of a video upload.
    :param video_id: The ID of the newly uploaded video, or 0 if the video already exists.
    :return: Formatted video-upload confirmation command string.
    """
    return build_command(16, [video_id])


def build_follow_user_status(status, followed):
    """
        Builds a response command indicating the result of a follow or unfollow action.
    :param status: 1 if the user was followed, 0 if they were unfollowed.
    :param followed: The username of the user that was followed or unfollowed.
    :return: Formatted follow-user status command string.
    """
    return build_command(17, [status, followed])


def build_like_video_confirmation(status, video_id):
    """
        Builds a response command confirming the result of a like or unlike action.
    :param status: 1 if the video was liked, 0 if the like was removed.
    :param video_id: The ID of the video that was liked or unliked.
    :return: Formatted like-video confirmation command string.
    """
    return build_command(18, [status, video_id])


def build_update_pfp():
    """
        Builds a response command notifying the client that their profile picture has been updated.
    :return: Formatted update-pfp command string.
    """
    return build_command(19, [])


# ----- Video transfer protocol -----

def build_file_details(file_name, file_size):
    """
        Builds a command containing file metadata for the video transfer protocol.
    :param file_name: The name of the file being transferred.
    :param file_size: The size of the file in bytes.
    :return: Formatted file-details command string.
    """
    return build_command(0, [file_name, file_size])


def is_file(msg):
    """
        Checks whether a message corresponds to a file transfer command.
    :param msg: The message string to check.
    :return: True if the message is a file transfer command, False otherwise.
    """
    return msg[:2] == build_file_details("", "")[:2]


def unpack(data):
    """Unpack a command string into opcode and parameters.

    Extracts the opcode and splits parameters by '@#' delimiter if present.

    :param data: Command string to unpack.
    :return: Tuple of (opcode, parameters list).
    """
    opcode = data[:2]
    params = []
    if len(data) > 2:
        params = data[2:].split("@#")

    for i, v in enumerate(params):
        if "#@" in v:
            params[i] = v.split("#@")

    return opcode, params
