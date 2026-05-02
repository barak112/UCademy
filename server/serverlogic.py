import os
import hashlib
import queue
import re
import secrets
import smtplib
import string
import time
from email.message import EmailMessage

import database
import serverComm
import serverCommVideos
import serverProtocol
import settings


class ServerLogic:
    """Manages the server-side logic for the UCademy project.

    Processes incoming messages
    from clients via a queue and communicates updates using the server communication module.
    """

    EMAIL_USER_KICK_MSG = """
    Your user {} has been kicked from the Ucademy platform for uploading inappropriate content multiple times.
    If you believe this is a mistake, please contact us at ucademy.team@gmail.com.

    Sincerely,
    The Ucademy System Managers Team
    """

    EMAIL_USER_KICK_SUBJECT = "Ucademy User Kick Notification"

    EMAIL_VIDEO_REMOVE_MSG = """
    Your video "{}" with description "{}" that was uploaded on {} by user {} has been removed from the Ucademy platform for violating our community guidelines.
    If you believe this is a mistake, please contact us at ucademy.team@gmail.com.

    Sincerely,
    The Ucademy System Managers Team
    """

    EMAIL_VIDEO_REMOVE_SUBJECT = "Ucademy Video Removal Notification"

    EMAIL_COMMENT_REMOVE_MSG = """
    Your comment "{}" that has been commented by user {} on the video "{}" by {} on {} has been removed from the Ucademy platform for violating our community guidelines.
    If you believe this is a mistake, please contact us at ucademy.team@gmail.com.

    Sincerely,
    The Ucademy System Managers Team
    """

    EMAIL_COMMENT_REMOVE_SUBJECT = "Ucademy Comment Removal Notification"

    EMAIL_VERIFICATION_CODE_MSG = """
    Your verification code for Ucademy email verification is: {}
    Do not share this code with anyone.

    A user "{}" has recently signed up to Ucademy's platform with this email address.
    We would like to ensure that the email used at the registration was used by its rightfully owner.

    If you did not recently signed up to the Ucademy platform, please ignore this email.
    For any questions, please contact us at ucademy.team@gmail.com.
    """

    EMAIL_VERIFICATION_CODE_SUBJECT = "Ucademy Email Verification Code"

    def __init__(self):
        """Initialize the server object and starts handle msgs"""

        self.recvQ = queue.Queue()
        self.comm = serverComm.ServerComm(settings.PORT, self.recvQ)
        self.commands = {
            '00': self.handle_registration,
            '01': self.handle_email_verification,
            '02': self.handle_sign_in,
            '03': self.handle_set_user_topics,
            '04': self.handle_filter_user_topics,
            '05': self.handle_creators_search,
            '06': self.handle_videos_search,
            '07': self.handle_video_comment,
            '08': self.handle_user_details_req,
            '09': self.handle_report,
            '10': self.handle_comments_req,
            '11': self.handle_video_del,
            '12': self.handle_del_comment,
            '13': self.handle_creator_videos_req,
            '14': self.handle_user_follow_list_req,
            '15': self.handle_video_req,
            '16': self.handle_video_upload,
            '17': self.handle_follow_user,
            '18': self.handle_like_video,
            '19': self.send_user_his_pfp,

            '97': self.handle_client_disconnected,
            '98': self.handle_comment_or_video_status,
            '99': self.handle_user_kick,
        }

        self.db = database.DataBase()
        self.current_video_port = settings.VIDEO_PORT
        self.clients = {}  # [client_ip] = (username, video_comm, [topics_filter])

        self.clients_awaiting_email_verification = {}  # [client_ip] = [username, password, email, email_verification_code, time]

        # todo delete this and fix all the searches to use lastid
        self.videos_to_send = {}  # [client_ip] = [videos_ids]
        self.users_to_send = {}  # [client_ip] = [users_names]
        self.comments_to_send = {}  # [client_ip] = [comments_ids]

        self.pfps_sent = {}  # [client_ip] = [users_names]
        self.videos_sent = {}  # [client_ip] = [videos_ids]
        self.thumbnails_sent = {}  # [client_ip] = [videos_ids]

        self.handle_msgs()

    def handle_client_disconnected(self, client_ip, data):  # command 96
        """
            deletes client from all dictionaries in the logic
        :param client_ip: client_ip to delete from dictionaries
        :param data: not used
        """
        self.clients.pop(client_ip, None)
        self.clients_awaiting_email_verification.pop(client_ip, None)
        self.videos_to_send.pop(client_ip, None)
        self.users_to_send.pop(client_ip, None)
        self.comments_to_send.pop(client_ip, None)

        self.pfps_sent.pop(client_ip, None)
        self.videos_sent.pop(client_ip, None)
        self.thumbnails_sent.pop(client_ip, None)

    def handle_msgs(self):
        """Process incoming messages from clients"""
        while True:
            ip, msg = self.recvQ.get()

            if isinstance(msg, tuple):
                self.handle_video_upload(ip, msg)
            else:
                opcode, data = serverProtocol.unpack(msg)

                if opcode in self.commands.keys():
                    self.commands[opcode](ip, data)

    def handle_registration(self, client_ip, data):  # command 0
        """
        Handles the registration process for a client during sign-up. Ensures that the
        provided credentials are valid. if valid, a verification code is
        generated and sent to the client's email. Tracks users awaiting verification.
        if the credentials are not valid, sends to the user the problems with the credentials

        :param client_ip: The IP address of the client initiating the registration.
        :param data: A tuple containing the username, password, and email provided
                     by the client for registration.
        """
        username, password, email = data

        status = self.validate_credentials_registration(username, password, email)

        if not any(status):
            verification_code = self.create_email_verification_code()
            time_of_code_creation = time.time()
            self.clients_awaiting_email_verification[client_ip] = [username, password, email, verification_code,
                                                                   time_of_code_creation]
            self.send_email_verification_code(email, verification_code, username)

        msg = serverProtocol.build_sign_up_status(status)
        self.comm.send_msg(client_ip, msg)

    def handle_email_verification(self, client_ip, data):  # command 1
        """
        Handles the process of verifying an email verification code sent to clients. This function validates
        the code provided by the client, checks if the code has expired, and processes the client
        information accordingly. Once the verification is successful, the client is registered, and a
        confirmation message is sent back to the client.

        :param client_ip: The IP address of the client attempting email verification.
        :param data: a list containing the verification code the user entered
        """
        email_verification_code = data[0]

        status = settings.EMAIL_VERIFICATION_CODE_INVALID
        username = None
        email = None
        port = None

        # check if user is awaiting verification code
        if client_ip in self.clients_awaiting_email_verification:
            # check if code is expired
            if settings.EMAIL_VERIFICATION_CODE_EXPIRATION < time.time() - \
                    self.clients_awaiting_email_verification[client_ip][4]:
                status = settings.EMAIL_VERIFICATION_CODE_EXPIRED
                del self.clients_awaiting_email_verification[client_ip]

            elif email_verification_code == self.clients_awaiting_email_verification[client_ip][
                3]:  # if not expired and is correct
                username, password, email = self.clients_awaiting_email_verification[client_ip][:3]
                # check if user credentials are still available
                status = self.validate_credentials_registration(username, password, email)

                if not any(status):  # credentials are valid:
                    self.db.add_user(username, email, self.hash_password(password))
                    self.clients[client_ip] = [username,
                                               serverCommVideos.ServerCommVideos(self.current_video_port, self.recvQ, client_ip),
                                               []]
                    self.pfps_sent[client_ip] = []
                    self.videos_sent[client_ip] = []
                    self.thumbnails_sent[client_ip] = []

                    port = self.current_video_port
                    status = settings.EMAIL_VERIFICATION_SUCCESSFUL
                    self.current_video_port += 1
                    del self.clients_awaiting_email_verification[client_ip]

                else:  # credentials are taken
                    status = settings.EMAIL_VERIFICATION_CREDENTIALS_TAKEN
        msg = serverProtocol.build_email_verification_confirmation(status, username, email, port)
        self.comm.send_msg(client_ip, msg)

    @staticmethod
    def create_email_verification_code():
        """
        Generates a random numeric verification code of default 6 digits.

        :param length: Specifies the number of digits for the generated code.
            Defaults to 6 if not provided.
        :return: A randomly generated string consisting of numeric digits only.
        """
        return ''.join(secrets.choice('0123456789') for _ in range(settings.VERIFICATION_CODE_LENGTH))

    def send_email_verification_code(self, email_address, verification_code, username):
        """
            Sends an email verification code to the user's email address.
        :param email_address: The email address to send the verification code to.
        :param verification_code: The verification code to include in the email.
        :param username: The username of the user being verified.
        """
        self.send_email(email_address, self.EMAIL_VERIFICATION_CODE_MSG.format(verification_code, username),
                        self.EMAIL_VERIFICATION_CODE_SUBJECT)

    def validate_credentials_registration(self, username, password, email):
        """
        Validates the credentials for user registration, including username, password,
        and email address. Performs checks based on predefined settings such as minimum
        and maximum lengths, format validations, and uniqueness constraints within the
        system's database. Returns a status list indicating the validity of each credential.

        :param username: The username to validate.
        :param password: The password to validate.
        :param email: The email address to validate.
        :return: A list of integers indicating the validation status for username,
            password, and email, respectively. Each index of the list represents:
                - Index 0: Status for username validation
                - Index 1: Status for password validation
                - Index 2: Status for email validation
        """
        status = [0, 0, 0]  # username, password, email statuses - everything is ok

        if len(username) < settings.MIN_NAME_LENGTH:
            status[0] = settings.USERNAME_TOO_SHORT  # username too short
        elif len(username) > settings.MAX_NAME_LENGTH:
            status[0] = settings.USERNAME_TOO_LONG  # username too long
        elif self.db.user_exists(username) or self.db.email_exists(username):
            status[0] = settings.USERNAME_ALREADY_EXISTS  # username already used as username or email
        elif not all(char in string.ascii_letters + string.digits + "_-." for char in username):
            status[0] = settings.USERNAME_INVALID_CHARACTERS  # invalid username characters
        elif not username[0] in string.ascii_letters:
            status[0] = settings.USERNAME_NOT_START_LETTER  # username must start with a letter

        if len(password) < settings.MIN_PASSWORD_LENGTH:
            status[1] = settings.PASSWORD_TOO_SHORT  # password too short (not secure)
        elif len(password) > settings.MAX_PASSWORD_LENGTH:
            status[
                1] = settings.PASSWORD_TOO_LONG  # password too long (extreme long passwords hashing can slow down the server)
        elif not any(letter in password for letter in string.ascii_letters):
            status[1] = settings.PASSWORD_NO_LETTERS  # password must include letters

        if not self.is_email_valid(email):
            status[2] = settings.EMAIL_NOT_VALID  # not a valid email

        elif self.db.email_exists(email) or self.db.user_exists(email):
            status[2] = settings.EMAIL_ALREADY_EXISTS  # email already used as email or username
        return status

    @staticmethod
    def is_email_valid(email):
        """
            Checks whether the given email address matches a valid email format.
        :param email: The email address string to validate.
        :return: True if the email matches the valid format pattern, False otherwise.
        """
        EMAIL_REGEX_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(EMAIL_REGEX_PATTERN, email) is not None

    def handle_sign_in(self, client_ip, data):  # command 2
        """
            Handles the sign-in process for a client. Validates credentials and, if correct,
            retrieves the user's data and registers them as an active client.
        :param client_ip: The IP address of the client attempting to sign in.
        :param data: A list containing the username or email and the password.
        """
        username_or_email, password = data
        msg = serverProtocol.build_sign_in_status(0)
        status = 0
        username = self.db.get_username(username_or_email)
        print(f"trying to sign in user: {username} ")

        if self.db.is_correct_username_and_password_hash(username, self.hash_password(password)):
            status = 1

            followers_amount = self.db.get_followers_amount(username)
            followings_amount = self.db.get_following_amount(username)
            videos_ids = self.db.get_videos_by_creator(username)

            topics = self.db.get_user_topics(username)
            email = self.db.get_user_email(username)
            followings_names = self.db.get_followings(username)
            msg = serverProtocol.build_sign_in_status(1, self.current_video_port, username, followers_amount,
                                                      followings_amount, videos_ids, email, topics, followings_names)
            self.clients[client_ip] = [username, serverCommVideos.ServerCommVideos(self.current_video_port, self.recvQ,
                                                                                   client_ip), []]
            self.pfps_sent[client_ip] = []
            self.videos_sent[client_ip] = []
            self.thumbnails_sent[client_ip] = []
            self.current_video_port += 1

        self.comm.send_msg(client_ip, msg)
        if status:
            reports = self.db.get_not_notified_reports(username)
            for i, report in enumerate(reports):
                reports[i] = (*report, client_ip)
            self.send_reports_statuses(reports)

    def send_reports_statuses(self, reports):
        """
            Sends report status notifications to the relevant clients, including
            any associated content details and media such as thumbnails or profile pictures.
        :param reports: A list of tuples in the format (target_id, target_type, reporter_username, client_ip).
        """
        # reports = [(id, type, username, client_id),(...)]
        print("sending reports:", reports)
        for id, type, username, client_ip in reports:

            self.db.set_report_notified(username, id, type)

            status, created_at = self.db.get_report_status_and_created_at(username, id, type)

            if type == settings.COMMENT_DIGIT_REPR:

                video_id, commenter, comment = self.db.get_specific_comment(id, False)[1:4]
                video_id = self.db.get_video_id_by_comment_id(id)
                creator, video_name = self.db.get_specific_video(video_id, False)[:2]

                content = (comment, video_name)
                content_publisher = (commenter, creator)
                self.send_pfp(client_ip, commenter)  # sends the commenter's pfp if the client doesnt already have it
            else:  # type == settings.VIDEO_DIGIT_REPR
                content, content_publisher = self.db.get_specific_video(id, False)[:2]
                thumbnail_path = (f"media\\videos\\{id}.png")
                if os.path.isfile(thumbnail_path) and thumbnail_path not in self.thumbnails_sent[client_ip]:
                    self.clients[client_ip][1].send_file(
                        thumbnail_path)  # sends the video's thumbnail if the client doesnt already have it'
                    self.thumbnails_sent[client_ip].append(thumbnail_path)

            msg = serverProtocol.build_report_status(status, id, type, content, content_publisher, created_at)
            self.clients[client_ip][1].send_msg(client_ip, msg)

    def handle_set_user_topics(self, client_ip, data):  # command 3
        """
            Handles updating the topic preferences for a user.
        :param client_ip: The IP address of the client sending the request.
        :param data: A list of topic integers to set as the user's preferences.
        """
        topics = [int(t) for t in data]
        self.db.set_user_topics(self.clients[client_ip][0], topics)
        msg = serverProtocol.build_set_topics_confirmation(topics)
        self.comm.send_msg(client_ip, msg)

        self.db.print_tables()

    def handle_filter_user_topics(self, client_ip, data):  # command 4
        """
            Handles setting a topic filter for a client's video feed.
        :param client_ip: The IP address of the client sending the request.
        :param data: A list of topic integers to use as the active filter.
        """
        topic_filter = [int(t) for t in data]
        self.clients[client_ip][2] = topic_filter
        msg = serverProtocol.build_set_filter_confirmation(topic_filter)
        self.comm.send_msg(client_ip, msg)

        print("set filter:", topic_filter)

    def handle_creators_search(self, client_ip, data):  # command 5
        """
        Handles the search for creators based on the provided username

        :param client_ip: The ip of the client making the request.
        :param data: A tuple containing the search username and a flag indicating if the
                     next batch of usernames should be sent.
        """
        username, is_next_send = data[0]

        is_next_send = int(is_next_send)

        if is_next_send:
            usernames = self.users_to_send[client_ip]
        else:
            usernames = self.db.get_similar_usernames(username)

        # send username details and pfps
        users = usernames[:settings.AMOUNT_OF_USERS_TO_SEND]
        self.users_to_send[client_ip] = usernames[settings.AMOUNT_OF_USERS_TO_SEND:]

        if users:
            self.send_users_details(client_ip, users)
        else:  # no more users to send
            msg_to_send = serverProtocol.build_user_details_in_search("", 0, 0, 0)
            self.comm.send_msg(client_ip, msg_to_send)

    def send_users_details(self, client_ip, usernames):  # helper func
        """
        Send the user details of the users in usernames to the client.

        :param client_ip: The ip of the client to which the data will be sent.
        :param usernames: A list of usernames of the users to send their details.
        """
        for username in usernames:
            if self.db.user_exists(username):
                followers_amount = self.db.get_followers_amount(username)
                followings_amount = self.db.get_following_amount(username)
                videos_ids = self.db.get_videos_by_creator(username)
                msg = serverProtocol.build_user_details_in_search(username, followers_amount, followings_amount,
                                                                  videos_ids)
                self.comm.send_msg(client_ip, msg)

                # sends the user's pfp if the client doesnt already have it
                self.send_pfp(client_ip, username)

    def send_pfp(self, client_ip, username):
        """
            sends the profile picture of a user to a client if it hasn't already been sent to him.

        :param client_ip: The ip of the client requesting the profile picture.
        :param username: The username associated with the profile picture to be sent.
        """
        if username not in self.pfps_sent[client_ip]:
            user_pfp_image_path = f"media\\pfps\\{username}.png"
            if os.path.isfile(user_pfp_image_path):
                self.pfps_sent[client_ip].append(username)
                self.clients[client_ip][1].send_file(user_pfp_image_path)
                print("sending pfp of user:", username)

    def handle_videos_search(self, client_ip, data):  # command 6
        """
        Handles the search of videos based on name and desc similarity.
        sends videos details and thumbnails to the client.

        :param client_ip: The IP address of the client initiating the request.
        :param data: A tuple containing the search parameters:
                     - video_name_or_desc: The name or description of the video to search for.
                     - topics: A list of topics to filter the search.
                     - is_next_send: Indicates if the next set of results should be sent.
        """
        video_name_or_desc, topics, is_next_send = data

        print("topics in videos_search: ", topics)

        is_next_send = int(is_next_send)
        if is_next_send:
            videos_ids = self.videos_to_send[client_ip]

        else:
            videos_ids = self.db.search_videos(video_name_or_desc, topics)

        videos_to_send = videos_ids[:settings.AMOUNT_OF_VIDEOS_TO_SEND]
        self.videos_to_send[client_ip] = videos_ids[settings.AMOUNT_OF_VIDEOS_TO_SEND:]

        print("videos_to_send in videos_search after last_id", videos_to_send)

        if videos_to_send:
            # send username details and pfps
            self.send_videos_details_and_thumbnail(client_ip, videos_to_send)
        else:
            msg_to_send = serverProtocol.build_video_details_in_search(0, "", "", "", "", 0, 0, 0)
            self.clients[client_ip][1].send_msg(client_ip, msg_to_send)

    def send_videos_details_and_thumbnail(self, client_ip, video_ids):  # Helper function
        """
        sends video details and thumbnail to the client.

        :param client_ip: The ip of the client.
        :param video_ids: A list of video ids of videos to send details and thumbnails.
        """
        for video_id in video_ids:
            if self.db.video_exists(video_id):
                video_id, creator, video_name, video_desc, created_at, likes_amount, comments_amount, liked = self.get_video_details(
                    client_ip, video_id)

                if video_id not in self.thumbnails_sent[client_ip]:
                    self.thumbnails_sent[client_ip].append(video_id)
                    thumbnail_path = f"media\\videos\\{video_id}.png"
                    self.clients[client_ip][1].send_file(thumbnail_path)

                msg = serverProtocol.build_video_details_in_profile(video_id, creator, video_name, video_desc,
                                                                    created_at,
                                                                    likes_amount, comments_amount, liked)

                self.clients[client_ip][1].send_msg(client_ip, msg)

        # to indicate end of videos sending
        msg = serverProtocol.build_video_details_in_profile(settings.END_OF_BATCH_SEND_ID, "", "", "", "", 0, 0, 0)
        self.clients[client_ip][1].send_msg(client_ip, msg)

    def handle_video_comment(self, client_ip, data):  # command 7
        """
            Handles a request from a client to post a comment on a video.
        :param client_ip: The IP address of the client posting the comment.
        :param data: A list containing the video ID and the comment text.
        """
        video_id, comment = data
        commenter_name = self.clients[client_ip][0]

        if self.db.video_exists(video_id):
            comment_id, created_at = self.db.add_comment(video_id, commenter_name, comment)
            print("id, created:", comment_id, created_at)
            msg = serverProtocol.build_comment_status(comment_id, video_id, commenter_name, comment, created_at)
            self.comm.send_msg(client_ip, msg)

    def handle_user_details_req(self, client_ip, data):  # command 8
        """
            Handles a request for a user's profile details, sending back their
            info and profile picture if not already sent.
        :param client_ip: The IP address of the client making the request.
        :param data: A list containing the username to look up.
        """
        username = data[0]

        user_details = self.get_user_details(username)

        # sends the user's pfp if the client doesnt already have it
        self.send_pfp(client_ip, username)

        # sends the user's details
        msg = serverProtocol.build_user_details_in_profile(*user_details)
        self.clients[client_ip][1].send_msg(client_ip, msg)

    def get_user_details(self, username):
        """
            Retrieves follower count, following count, and video IDs for a given user.
        :param username: The username of the user to retrieve details for.
        :return: A tuple of (username, followers_amount, followings_amount, videos_ids).
        """
        followers_amount = 0
        followings_amount = 0
        videos_ids = 0

        if self.db.user_exists(username):
            followers_amount = self.db.get_followers_amount(username)
            followings_amount = self.db.get_following_amount(username)
            videos_ids = self.db.get_videos_by_creator(username)

        return username, followers_amount, followings_amount, videos_ids

    def handle_report(self, client_ip, data):  # command 9
        """
            Handles a report submitted by a client against a video or comment.
            Validates the target exists, checks for duplicate or concluded reports,
            and records the report if valid.
        :param client_ip: The IP address of the client submitting the report.
        :param data: A list containing the target ID and target type (0 for comment, 1 for video).
        """
        id, type = data  # 0 - comment, 1 - video

        type = int(type)
        id = int(id)
        username = self.clients[client_ip][0]
        content, content_publisher = "", ""

        status = settings.REPORT_RECEIVED

        if type == settings.COMMENT_DIGIT_REPR and self.db.comment_exists(id):
            video_id, content_publisher, content = self.db.get_specific_comment(id)[1:4]
            # comments also share the video's name and creator
            video_creator, video_name = self.db.get_specific_video(video_id)[:2]
            content = [content, video_name]
            content_publisher = [content_publisher, video_creator]

        elif type == settings.VIDEO_DIGIT_REPR and self.db.video_exists(id):
            content, content_publisher = self.db.get_specific_video(id)[:2]

        else:
            status = settings.REPORT_CONTENT_DOESNT_EXISTS

        if self.db.is_report_concluded(id, type):
            status = settings.REPORT_CONCLUDED

        elif self.db.has_user_reported(username, id, type):
            status = settings.REPORT_ALREADY_ISSUED

        elif status == settings.REPORT_RECEIVED:
            self.db.add_report(username, id, type)

        msg = serverProtocol.build_report_status(status, id, type, content, content_publisher)
        self.comm.send_msg(client_ip, msg)

    def handle_comments_req(self, client_ip, data):  # command 10
        """
            :param data: video_id, last_comment_id
            last_comment_id -> used to determine which comments should be next to be sent to the client.
            last_comment_id is the last comment's id the client has received.
            if last_comment_id = 0. it means that its the first time the client has requested comments.
        """
        video_id, last_id = data
        print("comments req arrived at handle", video_id)

        last_id = int(last_id)

        comments = self.db.get_comments(video_id, self.clients[client_ip][0])
        comments_ids = [i[0] for i in comments]

        start_index = 0
        if last_id:
            start_index = comments_ids.index(last_id) + 1

        comments = comments[start_index:]  # make the comments start from the start_index

        deleted_comments_ids = self.db.get_deleted_command_ids(video_id)
        print("deleted comments ids:", deleted_comments_ids)

        # recreate comments without any deleted comments
        comments = [i for i in comments if i[0] not in deleted_comments_ids]

        print("comments:", repr(comments), "commentslen", len(comments))
        comments_to_send = comments[:settings.AMOUNT_OF_COMMENTS_TO_SEND]
        print(f"comments_to_send for video {video_id}:", comments_to_send)

        commenters = {i[2] for i in comments_to_send}
        # send pfps
        for commenter_name in commenters:
            self.send_pfp(client_ip, commenter_name)
            print("sending pfp of user in comments:", commenter_name)

        msg = serverProtocol.build_send_comments(comments_to_send)
        print("msg of comments:", msg)
        self.clients[client_ip][1].send_msg(client_ip, msg)

    def handle_video_del(self, client_ip, data):  # command 11
        """
            Handles a request to delete a video, verifying the requester is the creator.
        :param client_ip: The IP address of the client requesting deletion.
        :param data: A list containing the video ID to delete.
        """
        video_id = data[0]
        print("trying to deleting video:", video_id)

        msg = serverProtocol.build_del_video_confirmation(0)
        if client_ip in self.clients and self.db.is_the_video_creator(video_id, self.clients[client_ip][0]):
            self.db.delete_video(video_id)
            self.delete_video_file(video_id)
            msg = serverProtocol.build_del_video_confirmation(video_id)

        self.comm.send_msg(client_ip, msg)

    def handle_del_comment(self, client_ip, data):  # command 12
        """
            Handles a request to delete a comment.
        :param client_ip: The IP address of the client requesting deletion.
        :param data: A list containing the comment ID to delete.
        """
        comment_id = data[0]
        msg = serverProtocol.build_del_comment_confirmation(0)
        comment = self.db.get_specific_comment(comment_id)
        if comment:
            self.db.delete_comment(comment_id)
            video_id = comment[1]
            msg = serverProtocol.build_del_comment_confirmation(video_id, comment_id)
            print("deleting comment")
        self.comm.send_msg(client_ip, msg)

    def handle_creator_videos_req(self, client_ip, data):  # command 13
        """
            Handles a request for a paginated list of videos uploaded by a specific creator.
        :param client_ip: The IP address of the client making the request.
        :param data: A list containing the creator's username and the last received video ID for pagination.
        """
        username, last_id = data
        last_id = int(last_id)

        videos_ids = self.db.get_videos_by_creator(username, False)
        start_index = 0
        if last_id:
            start_index = videos_ids.index(last_id) + 1

        videos_ids = videos_ids[start_index:]
        deleted_videos_ids = self.db.get_deleted_videos_ids()

        videos_ids = [i for i in videos_ids if i not in deleted_videos_ids]

        videos_to_send = videos_ids[:settings.AMOUNT_OF_VIDEOS_TO_SEND]

        print(f"videos_to_send in creator video req: {videos_to_send}")

        if videos_to_send:
            self.send_videos_details_and_thumbnail(client_ip, videos_to_send)
        else:  # indicates there are no more videos to send
            msg_to_send = serverProtocol.build_video_details_in_profile(0, "", "", "", "", 0, 0, 0)
            self.clients[client_ip][1].send_msg(client_ip, msg_to_send)

    def handle_user_follow_list_req(self, client_ip, data):  # command 14
        """
            Handles a request for a user's followers or followings list, sending
            back user details in paginated batches.
        :param client_ip: The IP address of the client making the request.
        :param data: A list containing the username, follow type (0 for followings, 1 for followers),
                     and the last received username for pagination.
        """
        username, follow_type, last_follow_name = data

        if last_follow_name and last_follow_name in self.users_to_send[client_ip]:
            starting_index = self.users_to_send[client_ip].index(last_follow_name) + 1
            users_to_send = self.users_to_send[client_ip]
        else:
            follow_type = int(follow_type)
            starting_index = 0
            if follow_type:  # follow_type: 0 - followings, 1 - followers
                users_to_send = self.db.get_followers(username)
            else:
                users_to_send = self.db.get_followings(username)
            self.users_to_send[client_ip] = users_to_send

        print("users to send in follow list req", users_to_send)

        if users_to_send:
            users_to_send = users_to_send[starting_index:starting_index + settings.AMOUNT_OF_USERS_TO_SEND]
            self.send_users_details(client_ip, users_to_send)
        else:
            msg_to_send = serverProtocol.build_user_details_follow_list("", 0, 0, 0)
            self.comm.send_msg(client_ip, msg_to_send)

    def handle_video_req(self, client_ip, data):  # command 15
        """
            Handles a request for a specific or recommended video, sending the video
            file, its details, and its comments to the client.
        :param client_ip: The IP address of the client making the request.
        :param data: A list containing the video ID (0 to request a recommended video).
        """
        video_id = int(data[0])
        username = self.clients[client_ip][0]
        if not video_id:
            video_id = self.db.get_video_for_user(username, self.clients[client_ip][2])

        if video_id:
            if self.db.video_exists(video_id):
                self.send_video_and_details(client_ip, video_id)
                self.handle_comments_req(client_ip, [video_id, 0])
                if not self.db.has_watched_video(username, video_id):
                    self.db.add_watched_video(username, video_id)
            else:
                # if video requested has been deleted
                msg_to_send = serverProtocol.build_video_details(settings.DELETED_ID, "", "", "", "", 0, 0, 0)
                self.clients[client_ip][1].send_msg(client_ip, msg_to_send)
        else:
            video_id = settings.END_OF_LIST_ID
            if not self.db.are_there_videos():
                video_id = settings.NO_VIDEOS_ID

            self.db.remove_watched_videos_for_user(username)
            msg_to_send = serverProtocol.build_video_details(video_id, "", "", "", "", 0, 0, 0)
            self.clients[client_ip][1].send_msg(client_ip, msg_to_send)

    def send_video_and_details(self, client_ip, video_id):  # helper function
        """
        sends a video and its details to the client, including the creator's pfp.

        :param client_ip: The ip of the client requesting the video.
        :param video_id: The unique identifier of the video to be sent to the client.
        """
        video_id, creator, video_name, video_desc, created_at, likes_amount, comments_amount, liked = self.get_video_details(
            client_ip, video_id)

        self.send_pfp(client_ip, creator)  # sends creator's pfp if the clients doesnt already have it

        if not video_id in self.videos_sent[client_ip]:
            self.videos_sent[client_ip].append(video_id)
            file_path = f"media\\videos\\{video_id}.{settings.VIDEO_EXTENSION}"
            self.clients[client_ip][1].send_file(file_path)

        msg = serverProtocol.build_video_details(video_id, creator, video_name, video_desc, created_at, likes_amount,
                                                 comments_amount, liked)
        self.clients[client_ip][1].send_msg(client_ip, msg)

    def handle_video_upload(self, client_ip, data):  # command 16
        """
            Handles a video upload from a client, checking for duplicates by hash
            before saving the file and recording it in the database.
        :param client_ip: The IP address of the client uploading the video.
        :param data: A tuple of (file_content, extension, video_details), where video_details
                     contains the video name, description, test link, and topics.
        """
        file_content, extension, video_details = data
        video_name, video_desc, test_link, topics = video_details
        print("video_name", video_name, "video_desc", video_desc, "test_link", test_link, "topics", topics)

        video_hash = self.hash_video(file_content)
        if not self.db.hash_exists(video_hash):
            video_id = self.db.add_video(self.clients[client_ip][0], video_name, video_desc, test_link)
            self.db.add_video_topics(video_id, topics)

            with open(f"media\\videos\\{video_id}.{extension}", 'wb') as f:
                f.write(file_content)
            self.db.add_video_hash(video_id, video_hash)
            # puts the id for the thumbnail filename
            self.clients[client_ip][1].idsQ.put(video_id)
            print("video uploaded")
            msg = serverProtocol.build_video_upload_confirmation(video_id)
            self.comm.send_msg(client_ip, msg)
        else:
            # 0 indicates that the video already exists, so to not save the thumbnail
            self.clients[client_ip][1].idsQ.put(0)
            msg = serverProtocol.build_video_upload_confirmation(0)
            self.comm.send_msg(client_ip, msg)
            print("video already exists")

    def get_video_details(self, client_ip, video_id):  # helper function
        """
            Retrieves full details for a video, including whether the requesting user has liked it.
        :param client_ip: The IP address of the client requesting the details.
        :param video_id: The ID of the video to retrieve details for.
        :return: A tuple of (video_id, creator, video_name, video_desc, created_at, likes_amount, comments_amount, liked).
        """
        creator, video_name, video_desc, created_at, likes_amount, comments_amount = self.db.get_specific_video(
            video_id)
        liked = self.db.is_liked_by_user(video_id, self.clients[client_ip][0])
        liked = int(liked)
        return video_id, creator, video_name, video_desc, created_at, likes_amount, comments_amount, liked

    def handle_follow_user(self, client_ip, data):  # command 17
        """
            Handles a follow or unfollow request from a client.
        :param client_ip: The IP address of the client making the request.
        :param data: A list containing the username of the user to follow or unfollow.
        """
        followed = data[0]
        follower = self.clients[client_ip][0]
        status = 0
        if self.db.user_exists(followed):
            if self.db.is_following(follower, followed):
                self.db.remove_following(follower, followed)
            else:
                self.db.add_following(follower, followed)
                status = 1
        else:
            followed = ""  # indicates user doesnt exist
        msg = serverProtocol.build_follow_user_status(status, followed)
        self.comm.send_msg(client_ip, msg)

    def handle_like_video(self, client_ip, data):  # command 18
        """
            Handles a like or unlike request for a video from a client.
        :param client_ip: The IP address of the client making the request.
        :param data: A list containing the video ID to like or unlike.
        """
        video_id = data[0]
        username = self.clients[client_ip][0]
        status = 0
        if self.db.is_liked_by_user(video_id, username):
            self.db.remove_video_like(video_id, username)
        else:
            status = 1
            self.db.add_video_like(video_id, username)
        msg = serverProtocol.build_like_video_confirmation(status, video_id)
        self.comm.send_msg(client_ip, msg)

    def send_user_his_pfp(self, client_ip, data):  # command 19
        """
            Sends the logged-in user their own profile picture, refreshing it if already sent.
        :param client_ip: The IP address of the client requesting their profile picture.
        :param data: Not used.
        """
        if self.clients[client_ip][0] in self.pfps_sent[client_ip]:
            self.pfps_sent[client_ip].remove(self.clients[client_ip][0])
        print(self.pfps_sent)
        self.send_pfp(client_ip, self.clients[client_ip][0])
        msg = serverProtocol.build_update_pfp()
        self.clients[client_ip][1].send_msg(client_ip, msg)
        print("sending user pfp")

    # Called by System Manager

    def handle_comment_or_video_status(self, client_ip, data):  # command 98
        """
            Handles a system manager's decision on a reported comment or video,
            optionally removing the content and notifying affected reporters.
        :param client_ip: The IP address of the system manager client.
        :param data: A list containing the target ID, target type (0 for comment, 1 for video),
                     and the status decision (0 for keep, 1 for remove).
        """
        id, type, status = data  # type = 0 - comment, 1 - video, status = 0 - dont remove, 1 - remove
        id, type = int(id), int(type)
        if self.db.is_system_manager(self.clients[client_ip][0]):

            if (type == settings.COMMENT_DIGIT_REPR and self.db.comment_exists(id)) or (
                    type == settings.VIDEO_DIGIT_REPR and self.db.video_exists(id)):

                if status == settings.REPORT_ACCEPTED:
                    if type == settings.COMMENT_DIGIT_REPR:
                        comment_id, video_id, commenter, comment, created_at = self.db.get_specific_comment(id)
                        creator, video_name = self.db.get_specific_video(video_id)[:2]
                        self.db.delete_comment(id)
                        self.send_email(comment_id,
                                        self.EMAIL_COMMENT_REMOVE_MSG.format(comment, commenter, video_name, creator,
                                                                             created_at),
                                        self.EMAIL_COMMENT_REMOVE_SUBJECT)

                    else:  # video
                        creator, video_name, desc, created_at = self.db.get_specific_video(id)[:4]
                        self.db.delete_video(id)
                        self.db.remove_video_hash(id)
                        self.delete_video_file(id)
                        self.send_email(creator,
                                        self.EMAIL_VIDEO_REMOVE_MSG.format(video_name, desc, created_at, creator),
                                        self.EMAIL_VIDEO_REMOVE_SUBJECT)

                self.db.set_report_status(id, type, status)

                usernames = set(self.db.get_reporters(id, type))

                client_names = {i[0] for i in self.clients.values()}

                active_reporters = usernames & client_names

                reports = [[id, type, username, client_ip] for username in active_reporters]

                self.send_reports_statuses(reports)
            else:
                print("content does not exist")
        else:
            print("not a system manager")

    def delete_video_file(self, video_id):
        """
            Deletes a video's file from disk and removes its hash from the database.
        :param video_id: The ID of the video whose file should be deleted.
        """
        file_path = f"media\\videos\\{video_id}.{settings.VIDEO_EXTENSION}"
        if os.path.isfile(file_path):
            os.remove(file_path)
        self.db.remove_video_hash(video_id)

    def handle_user_kick(self, client_ip, data):  # command 99
        """
            Handles a system manager's request to kick a user, removing them from
            the database and sending them a notification email.
        :param client_ip: The IP address of the system manager client.
        :param data: A list containing the username of the user to kick.
        """
        username = data[0]
        if self.db.is_system_manager(self.clients[client_ip][0]):
            self.db.remove_user(username)
            email_address = self.db.get_user_email(username)
            self.send_email(email_address, self.EMAIL_USER_KICK_MSG.format(username), self.EMAIL_USER_KICK_SUBJECT)

    @staticmethod
    def send_email(email_address, email_msg, email_subject):
        """
            Sends an email using the Ucademy team Gmail account via SMTP SSL.
        :param email_address: The recipient's email address.
        :param email_msg: The body text of the email.
        :param email_subject: The subject line of the email.
        """
        sender = "ucademy.team@gmail.com"
        password = "ehfl pina bfmw ojte"  # app password
        receiver = email_address
        msg = EmailMessage()

        msg["Subject"] = email_subject
        msg["From"] = sender
        msg["To"] = receiver
        msg.set_content(email_msg)

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender, password)
                server.send_message(msg)
        except Exception as e:
            print("error when trying to send email:", e)

    @staticmethod
    def hash_video(path_or_content, chunk_size: int = 1024 * 1024) -> str:
        """
            Computes a SHA-256 hash of a video's binary content.
        :param path_or_content: The raw bytes of the video to hash.
        :param chunk_size: The size of each chunk to process at a time in bytes.
        :return: The hexadecimal SHA-256 digest of the video content.
        """
        h = hashlib.sha256()
        chunks_hashed = 0
        for chunk in iter(lambda: path_or_content[chunks_hashed * chunk_size:chunk_size * (chunks_hashed + 1)], b""):
            h.update(chunk)
            chunks_hashed += 1
        return h.hexdigest()

    @staticmethod
    def hash_password(password):
        """
            Hashes a plaintext password using MD5.
        :param password: The plaintext password string to hash.
        :return: The MD5 hexadecimal digest of the password.
        """
        return hashlib.md5(password.encode()).hexdigest()


if __name__ == "__main__":
    msgsQ = queue.Queue()
    ServerLogic()
