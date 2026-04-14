import ast
import os
import hashlib
import queue
import re
import secrets
import smtplib
import string
import time
from email.message import EmailMessage

#from email_validator import validate_email, EmailNotValidError

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
        comm = serverComm.ServerComm(settings.PORT, self.recvQ)
        self.comm = comm
        self.commands = {
            '00': self.handle_registration,
            '01': self.handle_email_verification,
            '02': self.handle_sign_in,
            '03': self.handle_set_user_topics,
            '04': self.handle_filter_user_topics,
            '05': self.handle_creators_search,
            '06': self.handle_videos_search,
            '07': self.handle_video_comment,
            '08': self.handle_test_req,
            '09': self.handle_report,
            '10': self.handle_comments_req,
            '11': self.handle_video_del,
            '12': self.handle_del_comment,
            '13': self.handle_creator_videos_req,
            '14': self.handle_user_follow_list_req,
            '15': self.handle_video_req,
            '16': self.handle_video_upload,
            '17': self.handle_follow_user,
            "18": self.handle_like_video_confirmation,


            '97':self.handle_client_disconnected,

            '98': self.handle_comment_or_video_status,
            '99': self.handle_user_kick,
        }

        self.db = database.DataBase()
        self.current_video_port = settings.VIDEO_PORT
        self.clients = {} # [client_ip] = (username, video_comm, [topics_filter])

        self.clients_awaiting_email_verification = {} # [client_ip] = [username, password, email, email_verification_code, time]

        self.videos_to_send = {} # [client_ip] = [videos_ids]
        self.users_to_send = {} # [client_ip] = [users_names]
        self.comments_to_send = {} # [client_ip] = [comments_ids]
        self.pfps_sent = {} # [client_ip] = [users_names]

        self.handle_msgs()

    def handle_client_disconnected(self, client_ip, data):
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


    def handle_msgs(self):
        """Process incoming messages from clients"""
        while True:
            ip, msg = self.recvQ.get()

            if isinstance(msg, tuple) :
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
            self.clients_awaiting_email_verification[client_ip] = [username, password, email, verification_code, time_of_code_creation]
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
            if settings.EMAIL_VERIFICATION_CODE_EXPIRATION < time.time() - self.clients_awaiting_email_verification[client_ip][4]:
                status = settings.EMAIL_VERIFICATION_CODE_EXPIRED
                del self.clients_awaiting_email_verification[client_ip]

            elif email_verification_code == self.clients_awaiting_email_verification[client_ip][3]: # if not expired and is correct
                username, password, email = self.clients_awaiting_email_verification[client_ip][:3]
                # check if user credentials are still available
                status = self.validate_credentials_registration(username, password, email)

                if not any(status): # credentials are valid:
                    self.db.add_user(username, email, self.hash_password(password))
                    self.clients[client_ip] = [username,
                                               serverCommVideos.ServerCommVideos(self.current_video_port, self.recvQ),
                                               []]
                    self.pfps_sent[client_ip] = []
                    port = self.current_video_port
                    status = settings.EMAIL_VERIFICATION_SUCCESSFUL
                    self.current_video_port += 1
                    del self.clients_awaiting_email_verification[client_ip]

                else: # credentials are taken
                    status = settings.EMAIL_VERIFICATION_CREDENTIALS_TAKEN
        msg = serverProtocol.build_email_verification_confirmation(status, username, email, port)
        self.comm.send_msg(client_ip, msg)

    @staticmethod
    def create_email_verification_code(length = 6):
        """
        Generates a random numeric verification code of default 6 digits.

        :param length: Specifies the number of digits for the generated code.
            Defaults to 6 if not provided.
        :return: A randomly generated string consisting of numeric digits only.
        """
        return ''.join(secrets.choice('0123456789') for _ in range(length))

    def send_email_verification_code(self, email_address, verification_code, username):
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
            status[1] = settings.PASSWORD_TOO_LONG  # password too long (extreme long passwords hashing can slow down the server)
        elif not any(letter in password for letter in string.ascii_letters):
            status[1] = settings.PASSWORD_NO_LETTERS  # password must include letters


        if not self.is_email_valid(email):
            status[2] = settings.EMAIL_NOT_VALID # not a valid email

        elif self.db.email_exists(email) or self.db.user_exists(email):
            status[2] = settings.EMAIL_ALREADY_EXISTS # email already used as email or username
        return status

    @staticmethod
    def is_email_valid(email):
        EMAIL_REGEX_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(EMAIL_REGEX_PATTERN, email) is not None


    def handle_sign_in(self, client_ip, data):  # command 2
        username_or_email, password = data
        msg = serverProtocol.build_sign_in_status(0)
        status = 0
        username = self.db.get_username(username_or_email)
        print(f"trying to sign in user: {username} ")

        if self.db.log_in(username, self.hash_password(password)):
            status = 1

            followers_amount = self.db.get_followers_amount(username)
            followings_amount = self.db.get_following_amount(username)
            videos_amount = self.db.get_videos_amount(username)

            topics = self.db.get_user_topics(username)
            email = self.db.get_user_email(username)
            followings_names = self.db.get_followings(username)
            msg = serverProtocol.build_sign_in_status(1,self.current_video_port,username, followers_amount,
                                                      followings_amount, videos_amount, email, topics, followings_names)
            self.clients[client_ip] = [username, serverCommVideos.ServerCommVideos(self.current_video_port, self.recvQ), topics]
            self.pfps_sent[client_ip] = []
            self.current_video_port+=1

        self.comm.send_msg(client_ip, msg)
        if status:
            reports = self.db.get_not_notified_reports(username)
            for i, report in enumerate(reports):
                reports[i] = (*report, client_ip)
            self.send_reports_statuses(reports)

    def send_reports_statuses(self, reports):
        #reports = [(id, type, username, client_id),(...)]
        print("sending reports:",reports)
        for id, type, username, client_ip in reports:

            self.db.set_report_notified(username, id, type)

            status, created_at = self.db.get_report_status_and_created_at(username, id, type)
            date, time = created_at.split(" ")

            if type == settings.COMMENT_DIGIT_REPR:

                video_id, commenter, comment = self.db.get_specific_comment(id, False)[1:4]
                video_id = self.db.get_video_id_by_comment_id(id)
                creator, video_name = self.db.get_specific_video(video_id, False)[:2]

                content = (comment, video_name)
                content_publisher = (commenter, creator)
            else:
                content, content_publisher = self.db.get_specific_video(id, False)[:2]

            msg = serverProtocol.build_report_status(status, id, type, content, content_publisher, date, time)
            self.comm.send_msg(client_ip, msg)

    def handle_set_user_topics(self, client_ip, data):  # command 3
        topics = [int(t) for t in data]
        self.db.set_user_topics(self.clients[client_ip][0], topics)
        msg = serverProtocol.build_set_topics_confirmation(topics)
        self.comm.send_msg(client_ip, msg)

        self.db.print_tables()

    def handle_filter_user_topics(self, client_ip, data):  # command 4
        topic_filter = [int(t) for t in data]
        self.clients[client_ip][2] = topic_filter
        msg = serverProtocol.build_set_filter_confirmation(1, topic_filter)
        self.comm.send_msg(client_ip, msg)

        print("set filter:", topic_filter)

    def handle_creators_search(self, client_ip, data):  # command 5
        username, is_next_send = data[0]

        is_next_send = int(is_next_send)

        if is_next_send:
            usernames = self.users_to_send[client_ip]
        else:
            usernames = self.db.get_similar_usernames(username)

        #send username details and pfps
        users = usernames[:settings.AMOUNT_OF_USERS_TO_SEND]
        self.users_to_send[client_ip] = usernames[settings.AMOUNT_OF_USERS_TO_SEND:]

        if users:
            self.send_users_details(client_ip, users)
        else: # no more users to send
            msg_to_send = serverProtocol.build_user_details("",0,0,0)
            self.comm.send_msg(client_ip,msg_to_send)


    def send_users_details(self, client_ip, usernames): # Not a Command!
        for username in usernames:
            if self.db.user_exists(username):
                print("username in send_users_details:", username)
                followers_amount = self.db.get_followers_amount(username)
                followings_amount = self.db.get_following_amount(username)
                videos_amount = self.db.get_videos_amount(username)
                msg = serverProtocol.build_user_details(username, followers_amount, followings_amount, videos_amount)
                self.comm.send_msg(client_ip, msg)

                #sends the user's pfp if the client doesnt already have it

                if username not in self.pfps_sent[client_ip]:
                    user_pfp_image_path = f"media\\pfps\\{username}.png"
                    if os.path.isfile(user_pfp_image_path):
                        self.pfps_sent[client_ip].append(username)
                        self.clients[client_ip][1].send_file(user_pfp_image_path)

    def handle_videos_search(self, client_ip, data):  # command 6
        video_name_or_desc, topics, is_next_send = data

        is_next_send = int(is_next_send)
        if is_next_send:
            videos_ids = self.videos_to_send[client_ip]

        else:
            topics = ast.literal_eval(topics)

            video_ids_by_name = set(self.db.get_videos_with_similar_name(video_name_or_desc))
            video_ids_by_desc = set(self.db.get_videos_with_similar_desc(video_name_or_desc))
            videos_ids = video_ids_by_name | video_ids_by_desc

            if topics:
                video_ids_by_topics = set(self.db.get_videos_ids_by_topics(topics))
                videos_ids = list(set(video_ids_by_topics) & set(videos_ids))

            videos_ids = self.db.order_ids_by_views(videos_ids)

        videos_to_send = videos_ids[:settings.AMOUNT_OF_VIDEOS_TO_SEND]
        self.videos_to_send[client_ip] = videos_ids[settings.AMOUNT_OF_VIDEOS_TO_SEND:]

        print("videos_to_send in videos_search after last_id", videos_to_send)

        if videos_to_send:
            # send username details and pfps
            self.send_videos_details_and_thumbnail(client_ip, videos_to_send)
        else:
            msg_to_send = serverProtocol.build_video_details(0, "", "", "", "",0, 0, 0)
            self.clients[client_ip][1].send_msg(client_ip, msg_to_send)

    def send_videos_details_and_thumbnail(self, client_ip, video_ids): # Helper function
        for video_id in video_ids:
            if self.db.video_exists(video_id):
                video_id, creator, video_name, video_desc, created_at, likes_amount, comments_amount, liked = self.get_video_details(client_ip, video_id)
                self.clients[client_ip][1].send_file(client_ip, f"media\\videos\\{video_id}.png", video_id, creator,
                                                   video_name, video_desc, created_at, likes_amount, comments_amount, liked)

    def handle_video_comment(self, client_ip, data):  # command 7
        video_id, comment = data
        commenter_name = self.clients[client_ip][0]

        if self.db.video_exists(video_id):
            comment_id, created_at = self.db.add_comment(video_id, commenter_name, comment)
            print("id, created:",comment_id, created_at)
            msg = serverProtocol.build_comment_status(comment_id,video_id, commenter_name, comment, created_at)
            self.comm.send_msg(client_ip, msg)

    def handle_test_req(self, client_ip, data):  # command 8
        video_id = data[0]
        video_link = self.db.get_video_test_link(video_id)

        if video_link:
            video_link = ""

        msg = serverProtocol.build_send_test(video_id, video_link)
        self.comm.send_msg(client_ip, msg)

    def handle_report(self, client_ip, data):  # command 9
        id, type = data # 0 - comment, 1 - video

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
        print("comments req arrived at handle")
        video_id, is_next_send = data

        is_next_send = int(is_next_send)

        if is_next_send and client_ip in self.comments_to_send:
            comments = self.comments_to_send[client_ip]
            #clears non existent comments (incase they were deleted)
            comments = [i for i in comments if self.db.comment_exists(i[0])]
        else:
            comments = self.db.get_comments(video_id, self.clients[client_ip][0])

        comments_to_send = comments[:settings.AMOUNT_OF_COMMENTS_TO_SEND]
        self.comments_to_send[client_ip] = comments[settings.AMOUNT_OF_COMMENTS_TO_SEND:]

        print("comments_to_send:",comments_to_send)


        msg = serverProtocol.build_send_comments(comments_to_send)
        print("msg of comments:",msg)
        self.clients[client_ip][1].send_msg(client_ip, msg)

        commenters = {i[2] for i in comments_to_send}
        # send pfps
        for commenter_name in commenters:
            if not commenter_name in self.pfps_sent[client_ip]:
                pfp_path = f"media\\pfps\\{commenter_name}.png"
                if os.path.isfile(pfp_path):
                    self.pfps_sent[client_ip].append(commenter_name)
                    self.clients[client_ip][1].send_file(client_ip,pfp_path)
                    print("sending pfp of user:",commenter_name)

    def handle_video_del(self, client_ip, data):  # command 11
        video_id = data[0]
        print("trying to deleting video:",video_id)

        msg = serverProtocol.build_del_video_confirmation(0)
        if client_ip in self.clients and self.db.is_the_video_creator(video_id, self.clients[client_ip][0]):
            self.db.delete_video(video_id)
            msg = serverProtocol.build_del_video_confirmation(video_id)

        self.comm.send_msg(client_ip, msg)

    def handle_del_comment(self, client_ip, data):  # command 12
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
        username, last_id = data

        last_id = int(last_id)
        if last_id and last_id in self.videos_to_send[client_ip]:
            videos_ids = self.videos_to_send[client_ip]
            starting_index = videos_ids.index(last_id)+1
        else:
            videos_ids = self.db.get_videos_by_creator(username)
            starting_index = 0
        
        videos_to_send = videos_ids[starting_index:starting_index+settings.AMOUNT_OF_VIDEOS_TO_SEND]

        print(f"videos_to_send in creator video req: {videos_to_send}")
        
        if videos_to_send:
            self.send_videos_details_and_thumbnail(client_ip, videos_to_send)
        else: # indicates there are no more videos to send
            msg_to_send = serverProtocol.build_video_details(0, "", "", "", "", 0, 0, 0)
            self.clients[client_ip][1].send_msg(client_ip, msg_to_send)

    def handle_user_follow_list_req(self, client_ip, data):  # command 14
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
            users_to_send = users_to_send[starting_index:starting_index+settings.AMOUNT_OF_USERS_TO_SEND]
            self.send_users_details(client_ip, users_to_send)
        else:
            msg_to_send = serverProtocol.build_user_details("", 0, 0, 0)
            self.comm.send_msg(client_ip, msg_to_send)

    def handle_video_req(self, client_ip, data):  # command 15
        video_id = int(data[0])
        username = self.clients[client_ip][0]
        if not video_id:
            video_id = self.db.get_video_for_user(username, self.clients[client_ip][2])

        if video_id:
            self.send_video_and_details(client_ip, video_id)
            self.handle_comments_req(client_ip, [video_id, 0])
            self.db.add_watched_video(username, video_id)
        else:
            self.db.remove_watched_videos_for_user(username)
            msg_to_send = serverProtocol.build_video_details(0, "", "", "", "", 0, 0, 0)
            self.clients[client_ip][1].send_msg(client_ip, msg_to_send)

    def send_video_and_details(self, client_ip, video_id):
        video_id, creator, video_name, video_desc, created_at, likes_amount, comments_amount, liked = self.get_video_details(
            client_ip, video_id)
        file_path = f"media\\videos\\{video_id}.{settings.VIDEO_EXTENSION}"
        self.clients[client_ip][1].send_file(client_ip, file_path, video_id, creator, video_name, video_desc,
                                             created_at, likes_amount, comments_amount, liked)

        print(
            f"sending video {video_id} to {client_ip} with creator {creator}, name {video_name}, desc {video_desc}, likes {likes_amount}, comments {comments_amount}, liked {liked}"
        )


    def get_video_details(self,client_ip, video_id): # helper function
        creator, video_name, video_desc, created_at, likes_amount, comments_amount = self.db.get_specific_video(video_id)
        liked = self.db.is_liked_by_user(video_id, self.clients[client_ip][0])
        liked = int(liked)
        return video_id, creator, video_name, video_desc, created_at, likes_amount, comments_amount, liked

    def handle_follow_user(self, client_ip, data):  # command 17
        followed = data[0]
        follower = self.clients[client_ip][0]

        if self.db.user_exists(followed):
            if self.db.is_following(follower, followed):
                self.db.remove_following(follower, followed)
            else:
                self.db.add_following(follower, followed)
        else:
            followed = "" # indicates user doesnt exist
        msg = serverProtocol.build_follow_user_status(followed)
        self.comm.send_msg(client_ip, msg)

    def handle_like_video_confirmation(self, client_ip, data):
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

    #called by video comm

    def handle_video_upload(self, client_ip, data):  # command 00
        file_content, extension, video_details = data
        video_name, video_desc, test_link = video_details
        print("Test link in video upload:",test_link, type(test_link))

        video_hash = self.hash_video(file_content)
        if not self.db.hash_exists(video_hash):
            video_id = self.db.add_video(self.clients[client_ip][0], video_name, video_desc, test_link)
            with open(f"media\\videos\\{video_id}.{extension}", 'wb') as f:
                f.write(file_content)
            self.db.add_video_hash(video_id, video_hash)
            # puts the id for the thumbnail filename
            self.clients[client_ip][1].idsQ.put(video_id)
            print("video uploaded")
        else:
            # 0 indicates that the video already exists, so to not save the thumbnail
            self.clients[client_ip][1].idsQ.put(0)
            print("video already exists")


    # Called by System Manager

    def handle_comment_or_video_status(self, client_ip, data):  # command 98
        id, type, status = data # type = 0 - comment, 1 - video, status = 0 - dont remove, 1 - remove
        id, type = int(id), int(type)
        if self.db.is_system_manager(self.clients[client_ip][0]):

            if (type == settings.COMMENT_DIGIT_REPR and self.db.comment_exists(id)) or (type == settings.VIDEO_DIGIT_REPR and self.db.video_exists(id)):

                if status == settings.REPORT_ACCEPTED:
                    if type == settings.COMMENT_DIGIT_REPR:
                        comment_id, video_id, commenter, comment, created_at = self.db.get_specific_comment(id)
                        creator, video_name = self.db.get_specific_video(video_id)[:2]
                        self.db.delete_comment(id)
                        self.send_email(comment_id, self.EMAIL_COMMENT_REMOVE_MSG.format(comment, commenter, video_name, creator, created_at), self.EMAIL_COMMENT_REMOVE_SUBJECT)

                    else: # video
                        creator, video_name, desc, created_at = self.db.get_specific_video(id)[:4]
                        self.db.delete_video(id)
                        self.send_email(creator, self.EMAIL_VIDEO_REMOVE_MSG.format(video_name, desc, created_at, creator), self.EMAIL_VIDEO_REMOVE_SUBJECT)

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

    def handle_user_kick(self, client_ip, data):  # command 99
        username = data[0]
        if self.db.is_system_manager(self.clients[client_ip][0]):
            self.db.remove_user(username)
            email_address = self.db.get_user_email(username)
            self.send_email(email_address, self.EMAIL_USER_KICK_MSG.format(username), self.EMAIL_USER_KICK_SUBJECT)

    @staticmethod
    def send_email(email_address, email_msg, email_subject):
        sender = "ucademy.team@gmail.com"
        password = "ehfl pina bfmw ojte"  # app password
        receiver = email_address
        msg = EmailMessage()

        msg["Subject"] = email_subject
        msg["From"] = sender
        msg["To"] = receiver
        msg.set_content(email_msg)

        #todo put inside a try and except, crushes when i dont have wifi
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)


    @staticmethod
    def hash_video(path_or_content, chunk_size: int = 1024 * 1024) -> str:
        h = hashlib.sha256()
        # if os.path.isfile(path_or_content):
        #     with open(path_or_content, "rb") as f:
        #         for chunk in iter(lambda: f.read(chunk_size), b""):
        #             h.update(chunk)
        # else:
        chunks_hashed = 0
        for chunk in iter(lambda: path_or_content[chunks_hashed*chunk_size:chunk_size*(chunks_hashed+1)], b""):
            h.update(chunk)
            chunks_hashed +=1
        return h.hexdigest()

    @staticmethod
    def hash_password(password):
        return hashlib.md5(password.encode()).hexdigest()


if __name__ == "__main__":
    msgsQ = queue.Queue()
    ServerLogic()
