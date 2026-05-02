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


def build_sign_up(username, password, email):
    """
        Builds a sign-up command with user credentials.
    :param username: The desired username for the new account.
    :param password: The desired password for the new account.
    :param email: The email address for the new account.
    :return: Formatted sign-up command string.
    """
    return build_command(0, [username, password, email])


def build_email_verification_code(email_verification_code):
    """
        Builds an email verification command with the provided code.
    :param email_verification_code: The verification code sent to the user's email.
    :return: Formatted email verification command string.
    """
    return build_command(1, [email_verification_code])


def build_sign_in(username_or_email, password):
    """
        Builds a sign-in command with user credentials.
    :param username_or_email: The username or email address of the user.
    :param password: The password of the user.
    :return: Formatted sign-in command string.
    """
    return build_command(2, [username_or_email, password])


def build_set_topics(topics):
    """
        Builds a command to set the topics associated with a user.
    :param topics: List of topics to assign to the user.
    :return: Formatted set-topics command string.
    """
    return build_command(3, topics)


def build_set_filter(topics):
    """
        Builds a command to set the content filter topics for a user.
    :param topics: List of topics to use as filters.
    :return: Formatted set-filter command string.
    """
    return build_command(4, topics)


def build_search_creators(creator_name, send_next: bool = False):
    """
        Builds a command to search for creators by name.
    :param creator_name: The name or partial name of the creator to search for.
    :param send_next: Whether to fetch the next page of results.
    :return: Formatted search-creators command string.
    """
    return build_command(5, [creator_name, int(send_next)])


def build_search_videos(video_name_or_desc, topics=None, send_next: bool = False):
    """
        Builds a command to search for videos by name or description.
    :param video_name_or_desc: The name or description to search for.
    :param topics: Optional list of topics to filter results by.
    :param send_next: Whether to fetch the next page of results.
    :return: Formatted search-videos command string.
    """
    if not topics:
        topics = []
    return build_command(6, [video_name_or_desc, topics, int(send_next)])


def build_comment(video_id, comment):
    """
        Builds a command to post a comment on a video.
    :param video_id: The ID of the video to comment on.
    :param comment: The comment text to post.
    :return: Formatted comment command string.
    """
    return build_command(7, [video_id, comment])


def build_req_user_info(username):
    """
        Builds a command to request information about a user.
    :param username: The username of the user to retrieve info for.
    :return: Formatted request-user-info command string.
    """
    return build_command(8, [username])


def build_report(id, type):
    """
        Builds a command to report a user or piece of content.
    :param id: The ID of the item being reported.
    :param type: The type of the item being reported.
    :return: Formatted report command string.
    """
    return build_command(9, [id, type])


def build_req_comments(video_id, last_id=0):
    """
        Builds a command to request comments for a video.
    :param video_id: The ID of the video to fetch comments for.
    :param last_id: The ID of the last received comment, used for pagination.
    :return: Formatted request-comments command string.
    """
    return build_command(10, [video_id, last_id])


def build_del_video(video_id):
    """
        Builds a command to delete a video.
    :param video_id: The ID of the video to delete.
    :return: Formatted delete-video command string.
    """
    return build_command(11, [video_id])


def build_del_comment(comment_id):
    """
        Builds a command to delete a comment.
    :param comment_id: The ID of the comment to delete.
    :return: Formatted delete-comment command string.
    """
    return build_command(12, [comment_id])


def build_req_creator_videos(username, last_id=0):
    """
        Builds a command to request videos uploaded by a specific creator.
    :param username: The username of the creator.
    :param last_id: The ID of the last received video, used for pagination.
    :return: Formatted request-creator-videos command string.
    """
    return build_command(13, [username, last_id])


def build_req_user_follow_list(username, follow_type,
                               send_next: bool = False):  # follow_type: 0 - followings, 1 - followers
    """
        Builds a command to request a user's following or followers list.
    :param username: The username of the user whose follow list to retrieve.
    :param follow_type: The type of list to fetch — 0 for followings, 1 for followers.
    :param send_next: Whether to fetch the next page of results.
    :return: Formatted request-follow-list command string.
    """
    return build_command(14, [username, follow_type, int(send_next)])


def build_req_video(video_id=0):
    """
        Builds a command to request a specific video.
    :param video_id: The ID of the video to retrieve.
    :return: Formatted request-video command string.
    """
    return build_command(15, [video_id])


def build_video_details(video_name, video_desc, test_link, topics):
    """
        Builds a command to submit details for a video.
    :param video_name: The name/title of the video.
    :param video_desc: The description of the video.
    :param test_link: A test link associated with the video.
    :param topics: List of topics associated with the video.
    :return: Formatted video-details command string.
    """
    return build_command(16, [video_name, video_desc, test_link, topics])


def build_follow_req(username):
    """
        Builds a command to follow or unfollow a user.
    :param username: The username of the user to follow/unfollow.
    :return: Formatted follow-request command string.
    """
    return build_command(17, [username])


def build_like_video(video_id):
    """
        Builds a command to like or unlike a video.
    :param video_id: The ID of the video to like/unlike.
    :return: Formatted like-video command string.
    """
    return build_command(18, [video_id])


# ----- Video transfer protocol -----

def build_file_details(file_name, file_size, video_name=None, video_description=None, test_link=None, topics=None):
    """
        Builds a command containing file and optional video metadata for transfer.
    :param file_name: The name of the file being transferred.
    :param file_size: The size of the file in bytes.
    :param video_name: Optional name/title of the associated video.
    :param video_description: Optional description of the associated video.
    :param test_link: Optional test link associated with the video.
    :param topics: Optional list of topics associated with the video.
    :return: Formatted file-details command string.
    """
    return build_command(0, [file_name, file_size, video_name, video_description, test_link, topics])


def is_file(msg):
    """
        Checks whether a message corresponds to a file transfer command.
    :param msg: The message string to check.
    :return: True if the message is a file transfer command, False otherwise.
    """
    return msg[:2] == build_file_details("", "")[:2]


# ----- System Manager protocol -----

def build_comment_or_video_status(id, type, status):
    """
        Builds a command to update the status of a comment or video.
    :param id: The ID of the comment or video.
    :param type: The type of the item — 0 for comment, 1 for video.
    :param status: The new status to assign to the item.
    :return: Formatted status-update command string.
    """
    return build_command(98, [id, type, status])  # type - 0 - comment, 1 - video


def build_kick_user(username):
    """
        Builds a command to kick a user from the system.
    :param username: The username of the user to kick.
    :return: Formatted kick-user command string.
    """
    return build_command(99, [username])


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
