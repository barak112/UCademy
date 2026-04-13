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
    return build_command(0, [status])

def build_email_verification_confirmation(status, username = None, email = None, port=None):
    return build_command(1, [status, username, email, port])

def build_sign_in_status(status, port = None, username = None, followers_amount = None,
                         followings_amount = None, videos_amount = None, email = None, topics = None, followings_names = None):
    return build_command(2, [status, port, username, followers_amount, followings_amount, videos_amount, email, topics,
                             followings_names])


def build_set_topics_confirmation(topics):
    return build_command(3, [topics])


def build_set_filter_confirmation(status, filter):
    return build_command(4, [status, filter])


def build_user_details(username, followers_amount, followings_amount, videos_amount):
    return build_command(
        5,
        [username, followers_amount, followings_amount, videos_amount]
    )


def build_video_details(video_id, creator_name, video_name, video_desc, created_at, likes_amount,
                        comments_amount, liked):
    return build_command(
        6,
        [video_id, creator_name, video_name, video_desc, created_at, likes_amount,
         comments_amount, liked]
    )


def build_comment_status(comment_id, video_id, commenter, comment, created_at):
    return build_command(7, [comment_id, video_id, commenter, comment, created_at])


def build_send_test(video_id, link):
    if not link:
        link = ""
    return build_command(8, [video_id, link])


def build_report_status(status, id, type, content, content_publisher, date = "", time = ""):
    return build_command(9, [status, id, type, content, content_publisher, date, time])


def build_send_comments(comments):
    # comments = [[comment_id, video_id, commenter_name, comment], ...]
    return build_command(10, comments)


def build_del_video_confirmation(video_id):
    return build_command(11, [video_id])


def build_del_comment_confirmation(video_id = 0, comment_id = 0):
    return build_command(12, [video_id, comment_id])


#12-14 are client requests that are handles using other commands


def build_video_upload_confirmation(status):
    return build_command(16, [status])


def build_follow_user_status(status):
    return build_command(17, [status])

def build_like_video_confirmation(status):
    return build_command(18, [status])

# ----- Video transfer protocol -----


def build_file_details(file_name, file_size, video_id = None, creator_name = None, video_name=None, video_desc=None,
                       created_at = None, likes_amount=None,
                       comments_amount=None, liked=None):
    return build_command(0, [file_name, file_size, video_id, creator_name, video_name, video_desc,
                             created_at, likes_amount, comments_amount, liked])


def build_confirm_file(status):
    return build_command(1, [status])


def unpack(data):
    """Unpack a command string into opcode and parameters.

    Extracts the opcode and splits parameters by '@#' delimiter if present.

    :param data: Command string to unpack.
    :return: Tuple of (opcode, parameters list).
    """
    opcode = data[:2]
    params = [""]
    if len(data) > 2:
        params = data[2:].split("@#")

    for i, v in enumerate(params):
        if "#@" in v:
            params[i] = v.split("#@")

    return opcode, params
