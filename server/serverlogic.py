import ast
import os
import hashlib
import hmac
import queue
import re
import secrets
import smtplib
import string
from email.message import EmailMessage
from string import punctuation

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
        """Initialize the server object.

        :param comm: ServerComm object for client communication.
        :param recvQ: Queue for receiving messages from clients.
        """

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

            '98': self.handle_comment_or_video_remove,
            '99': self.handle_user_kick,
        }

        self.db = database.DataBase()
        self.current_video_port = settings.VIDEO_PORT
        self.clients = {} # [client_ip] = (username, video_comm, [topics_filter])

        self.clients_awaiting_email_verification = {} # [client_ip] = [username, password, email, email_verification_code]

        self.videos_to_send = {} # [client_ip] = [videos_ids]
        self.users_to_send = {} # [client_ip] = [users_names]
        self.comments_to_send = {} # [client_ip] = [comments_ids]
        self.pfps_sent = {} # [client_ip] = [users_names]

        self.handle_msgs()

    def handle_msgs(self):
        """Process incoming messages from clients.
        """
        while True:
            ip, msg = self.recvQ.get()

            if isinstance(msg, tuple) :
                self.handle_video_upload(ip, msg)
            else:
                opcode, data = serverProtocol.unpack(msg)

                if opcode in self.commands.keys():
                    self.commands[opcode](ip, data)

    def handle_registration(self, client_ip, data):  # command 0
        username, password, email = data

        status = self.validate_credentials_registration(username, password, email)

        if not any(status):
            verification_code = self.create_email_verification_code()
            self.clients_awaiting_email_verification[client_ip] = [username, password, email, verification_code]
            self.send_email_verification_code(email, verification_code, username)

        msg = serverProtocol.build_sign_up_status(status)
        self.comm.send_msg(client_ip, msg)

    def handle_email_verification(self, client_ip, data):  # command 1
        email_verification_code = data[0]

        msg = serverProtocol.build_email_verification_confirmation(0)

        if email_verification_code == self.clients_awaiting_email_verification[client_ip][3]:
            username, password, email = self.clients_awaiting_email_verification[client_ip][:3]

            self.db.add_user(username, email, self.hash_password(password))
            self.clients[client_ip] = [username, serverCommVideos.ServerCommVideos(self.current_video_port, self.recvQ),[]]
            self.pfps_sent[client_ip] = []
            msg = serverProtocol.build_email_verification_confirmation(1, username, email, self.current_video_port)

            self.current_video_port+=1

        self.comm.send_msg(client_ip, msg)

    def create_email_verification_code(self , length = 6):
        return ''.join(secrets.choice('0123456789') for _ in range(length))

    def send_email_verification_code(self, email_address, verification_code, username):
        self.send_email(email_address, self.EMAIL_VERIFICATION_CODE_MSG.format(verification_code, username),
                        self.EMAIL_VERIFICATION_CODE_SUBJECT)


    def validate_credentials_registration(self, username, password, email):
        status = [0,0,0] # username, password, email statuses - everything is ok
        if len(username)<settings.MIN_NAME_LENGTH:
            status[0] = 1 # username too short
        elif len(username)>settings.MAX_NAME_LENGTH:
            status[0] = 2 # username too long
        elif self.db.user_exists(username):
            status[0] = 3 # username already exists
        elif not all(char in string.ascii_letters + string.digits + "_-." for char in username):
            status[0] = 4 # invalid username characters
        elif not username[0] in string.ascii_letters:
            status[0] = 5 # username must start with a letter

        if len(password)<settings.MIN_PASSWORD_LENGTH:
            status[1] = 1 # password too short (not secure)
        elif len(password)>settings.MAX_PASSWORD_LENGTH:
            status[1] = 2 # password too long (extreme long passwords hashing can slow down the server)
        elif not any(letter in username for letter in string.ascii_letters):
            status[1] = 3 # password must include letters

        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if re.match(pattern, email) is None:
            status[2] = 1 # not a valid email

        return status

    def handle_sign_in(self, client_ip, data):  # command 2
        username_or_email, password = data
        msg = serverProtocol.build_sign_in_status(0)
        status = 0
        username = self.db.get_username(username_or_email)
        print(f"trying to sign in user: {username} ")
        if self.db.log_in(username_or_email, password):
            followers_amount = self.db.get_followers_amount(username)
            followings_amount = self.db.get_following_amount(username)
            videos_amount = self.db.get_videos_amount(username)

            topics = self.db.get_user_topics(username)
            email = self.db.get_user_email(username)
            followings_names = self.db.get_followings(username)
            msg = serverProtocol.build_sign_in_status(1,self.current_video_port,username, followers_amount,
                                                      followings_amount, videos_amount, email, topics, followings_names)
            status = 1
            self.clients[client_ip] = [username, serverCommVideos.ServerCommVideos(self.current_video_port, self.recvQ), topics]
            self.pfps_sent[client_ip] = []
            self.current_video_port+=1

        self.comm.send_msg(client_ip, msg)
        print(f"sign in status for {username} is {status}")

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
            #todo check that the empty video works

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
            comment_id = self.db.add_comment(video_id, commenter_name, comment)
            msg = serverProtocol.build_comment_status(comment_id,video_id, comment)
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

        if type == settings.COMMENT_DIGIT_REPR and self.db.comment_exists(id):
            video_id, content_publisher, content = self.db.get_specific_comment(id)[1:4]
            # comments also share the video's name and creator
            video_creator, video_name = self.db.get_specific_video(video_id)[:2]
            content = [content, video_name]
            content_publisher = [content_publisher, video_creator]

        elif type == settings.VIDEO_DIGIT_REPR and self.db.video_exists(id):
            content, content_publisher = self.db.get_specific_video(id)[:2]

        else:
            id = 0

        if self.db.has_user_reported(username, id, type):
            id = 0

        if id:
            self.db.add_report(username, id, type)

        msg = serverProtocol.build_report_status(id, type, content, content_publisher)

        self.comm.send_msg(client_ip, msg)

    def handle_comments_req(self, client_ip, data):  # command 10
        """
            :param data: video_id,, last_comment_id
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
        video_id = data[0]
        if video_id:
            video_id, creator, video_name, video_desc, created_at, likes_amount, comments_amount, liked = self.get_video_details(client_ip, video_id)
            file_path = f"media\\videos\\{video_id}.{settings.VIDEO_EXTENSION}"
            self.clients[client_ip][1].send_file(client_ip, file_path, video_id, creator, video_name, video_desc,
                                                 created_at, likes_amount, comments_amount, liked)
            print(
                f"sending video {video_id} to {client_ip} with creator {creator}, name {video_name}, desc {video_desc}, likes {likes_amount}, comments {comments_amount}, liked {liked}"
            )
        else:
            #todo: algorithm to choose video
            pass

    def get_video_details(self,client_ip, video_id): # helper function
        creator, video_name, video_desc, created_at, likes_amount, comments_amount = self.db.get_specific_video(video_id)
        liked = self.db.is_liked_by_user(video_id, self.clients[client_ip][0])
        liked = int(liked)
        return video_id, creator, video_name, video_desc, created_at, likes_amount, comments_amount, liked

    def handle_follow_user(self, client_ip, data):  # command 17
        username = data
        pass


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

    def handle_comment_or_video_remove(self, client_ip, data):  # command 98
        id, type = data # type = 0 - comment, 1 - video
        if self.db.is_system_manager(self.clients[client_ip][0]):
            if type == settings.COMMENT_DIGIT_REPR:
                comment_id, video_id, commenter, comment, created_at = self.db.get_specific_comment(id)
                creator, video_name = self.db.get_specific_video(video_id)[:2]

                self.db.delete_comment(id)
                self.send_email(comment_id, self.EMAIL_COMMENT_REMOVE_MSG.format(comment, commenter, video_name, creator, created_at), self.EMAIL_COMMENT_REMOVE_SUBJECT)

            elif type == settings.VIDEO_DIGIT_REPR:
                creator, video_name, desc, created_at = self.db.get_specific_video(id)[:4]

                self.db.delete_video(id)
                self.send_email(creator, self.EMAIL_VIDEO_REMOVE_MSG.format(video_name, desc, created_at, creator), self.EMAIL_VIDEO_REMOVE_SUBJECT)

            else:
                print("Invalid type value")
        else:
            print("not a system manager")

    def handle_user_kick(self, client_ip, data):  # command 99
        username = data[0]
        if self.db.is_system_manager(self.clients[client_ip][0]):
            self.db.remove_user(username)
            email_address = self.db.get_user_email(username)
            self.send_email(email_address, self.EMAIL_USER_KICK_MSG.format(username), self.EMAIL_USER_KICK_SUBJECT)

    def send_email(self, email_address, email_msg, email_subject):
        sender = "ucademy.team@gmail.com"
        password = "ehfl pina bfmw ojte"  # app password
        receiver = email_address
        msg = EmailMessage()

        msg["Subject"] = email_subject
        msg["From"] = sender
        msg["To"] = receiver
        msg.set_content(email_msg)

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
    def hash_password(password: str, *, iterations: int = 200_000) -> str:
        salt = os.urandom(16)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return f"pbkdf2_sha256${iterations}${salt.hex()}${dk.hex()}"

if __name__ == "__main__":
    msgsQ = queue.Queue()
    ServerLogic()
