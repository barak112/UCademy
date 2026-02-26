def build_command(command, params):
    """Build a command string using an opcode and parameters.

    Joins parameters with '@#' delimiter and prepends the command opcode.

    :param command: The opcode for the command.
    :param params: List of parameters for the command.
    :return: Formatted command string.
    """
    while params and params[-1] is None:  # remove None at the end of params
        params.pop()
    params = [str(i) for i in params]
    return str(command).zfill(2) + "@#".join(params)


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


def build_search_videos(video_name_or_desc, topics = None):
    if not topics:
        topics = []
    return build_command(5, [video_name_or_desc, topics])


def build_comment(video_id, comment):
    return build_command(6, [video_id, comment])


def build_req_test(video_id):
    return build_command(7, [video_id])


def build_report(video_or_comment_id):
    return build_command(8, [video_or_comment_id])


def build_req_comments(video_id, last_comment_id):
    return build_command(9, [video_id, last_comment_id])


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


def build_video_details(video_name, video_desc, test_link):
    return build_command(15, [video_name, video_desc, test_link])


def build_follow_req(username):
    return build_command(16, [username])


# ----- Video transfer protocol -----

def build_file_details(file_name, file_size, video_name=None, video_description=None, test_link=None):
    return build_command(0, [file_name, file_size, video_name, video_description, test_link])


def is_video(msg):
    return msg[:2] == build_file_details("", "")[:2]


# ----- System Manager protocol -----

def build_remove_command_or_video(id, type):
    return build_command(98, [id, type]) # type - 0 - comment, 1 - video

def build_kick_user(username):
    return build_command(99, [username])


def unpack(data):
    """Unpack a command string into opcode and parameters.

    Splits the command string by '@#' to extract parameters.

    :param data: Command string to unpack.
    :return: Tuple of (opcode, parameters list).
    """
    opcode = data[:2]
    params = [None]
    if len(data) > 2:
        params = data[2:].split("@#")
    return opcode, params

