def build_command(command, params):
    """Build a command string using an opcode and parameters.

    Joins parameters with '@#' delimiter and prepends the command opcode.

    :param command: The opcode for the command.
    :param params: List of parameters for the command.
    :return: Formatted command string.
    """
    return str(command) + "@#".join(params)


def build_sign_up(username, password, email):
    return build_command(0, [username, password, email])


def build_sign_in(username_or_email, password):
    return build_command(1, [username_or_email, password])


def build_set_topics(topics):
    return build_command(2, topics)


def build_set_filter(topics):
    return build_command(3, topics)


def build_search_creators(creator_name):
    return build_command(4, [creator_name])


def build_search_videos(video_name_or_desc, topics):
    return build_command(5, [video_name_or_desc, topics])


def build_comment(video_id, comment):
    return build_command(6, [video_id, comment])


def build_ask_test(video_id):
    return build_command(7, [video_id])


def build_report(video_or_comment_id):
    return build_command(8, [video_or_comment_id])


def build_req_comments(video_id, comment_id):
    return build_command(9, [video_id, comment_id])


def build_del_video(video_id):
    return build_command(10, [video_id])


def build_del_comment(comment_id):
    return build_command(11, [comment_id])


def build_req_creator_videos(username):
    return build_command(12, [username])


def build_req_creator_follow(username, follow_type):
    return build_command(13, [username, follow_type])


def build_req_video(video_id):
    return build_command(14, [video_id])


def build_video_detail(video_name, video_desc, test_link):
    return build_command(15, [video_name, video_desc, test_link])


def build_follow_req(username):
    return build_command(16, [username])


# ----- Video transfer protocol -----

def build_file_details(file_name, file_size):
    return build_command(00, [file_name, file_size])


def unpack(data):
    """Unpack a command string into opcode and parameters.

    Splits the command string by '@#' to extract parameters.

    :param data: Command string to unpack.
    :return: Tuple of (opcode, parameters list).
    """
    opcode = data[0]
    params = data[1:].split("@#")
    return opcode, params
