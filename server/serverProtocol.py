def build_command(command, params):
    """Build a command string using an opcode and parameters.

    Joins parameters with '@#' delimiter and prepends the command opcode.

    :param command: The opcode for the command.
    :param params: List of parameters for the command.
    :return: Formatted command string.
    """
    params = [str(i) for i in params]
    return str(command).zfill(2) + "@#".join(params)


def build_sign_up_status(status, port = None):
    msg = build_command(0, [status])
    if status:
        msg = build_command(0, [status, port])
    return msg


def build_sign_in_status(status, username = None, email = None, topics = None,followings_names = None):
    msg = build_command(1, [status])
    if status:
        msg = build_command(1, [status, username, email, topics, followings_names])
    return msg


def build_set_topics_confirmation(topics):
    return build_command(2, [topics])


def build_set_filter_confirmation(status, filter):
    return build_command(3, [status, filter])


def build_creator_details(username, followers_amount, following_amount, videos_amount):
    return build_command(
        4,
        [username, followers_amount, following_amount, videos_amount]
    )


def build_video_details(video_id, creator_name, video_name, video_desc, likes_amount,
                        comments_amount, liked):
    return build_command(
        5,
        [video_id, creator_name, video_name, video_desc, likes_amount,
         comments_amount, liked]
    )


def build_comment_status(status):
    return build_command(6, [status])


def build_send_test(link):
    return build_command(7, [link])


def build_report_status(status):
    return build_command(8, [status])


def Build_send_comments(comments):
    # comments = [[comment_id, commenter_name, comment], ...]
    return build_command(9, comments)


def build_del_video_confirmation(status):
    return build_command(10, [status])


def build_del_comment_confirmation(status):
    return build_command(11, [status])


#12-14 are client requests that are handles using other commands


def build_video_upload_confirmation(status):
    return build_command(15, [status])

def build_follow_user_status(status):
    return build_command(16, [status])



# ----- Video transfer protocol -----


def build_file_details(file_name, file_size):
    return build_command(0, [file_name, file_size])


def build_confirm_file(status):
    return build_command(1, [status])


def unpack(data):
    """Unpack a command string into opcode and parameters.

    Extracts the opcode and splits parameters by '@#' delimiter if present.

    :param data: Command string to unpack.
    :return: Tuple of (opcode, parameters list).
    """
    opcode = data[:2]
    params = ""
    if len(data) > 2:
        params = data[2:].split("@#")
    return opcode, params
