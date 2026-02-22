import os
import hashlib
import hmac
import queue

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
            '01': self.handle_sign_in,
            '02': self.handle_set_user_topics,
            '03': self.handle_filter_user_topics,
            '04': self.handle_creators_search,
            '05': self.handle_videos_search,
            '06': self.handle_video_comment,
            '07': self.handle_test_req,
            '08': self.handle_report,
            '09': self.handle_comments_req,
            '10': self.handle_video_del,
            '11': self.handle_del_comment,
            '12': self.handle_creator_videos_req,
            '13': self.handle_user_follow_list_req,
            '14': self.handle_video_req,
            '15': self.handle_video_upload,
            '16': self.handle_follow_user,

            '98': self.handle_comment_or_video_remove,
            '99': self.handle_user_kick,
        }

        self.db = database.DataBase()
        self.current_video_port = settings.VIDEO_PORT
        self.clients = {} # [client_ip] = (username, video_comm, [topics_filter])

        self.handle_msgs()

    def handle_msgs(self):
        """Process incoming messages from clients.
        """
        while True:
            ip, msg = self.recvQ.get()

            if isinstance(msg, tuple) :
                movie_name = msg[1]
            else:

                opcode, data = serverProtocol.unpack(msg)

                if opcode in self.commands.keys():
                    self.commands[opcode](ip, data)

    def handle_registration(self, client_ip, data): # command 0
        username, password, email = data

        msg = serverProtocol.build_sign_up_status(0)
        if self.db.add_user(username, email, self.hash_password(password)):
            self.clients[client_ip] = [username, serverCommVideos.ServerCommVideos(self.current_video_port), []]

            msg = serverProtocol.build_sign_up_status(1, self.current_video_port)

        self.current_video_port+=1

        self.comm.send_msg(client_ip, msg)

    def handle_sign_in(self, client_ip, data): #command 1
        username_or_email, password = data
        msg = serverProtocol.build_sign_in_status(0)

        username = self.db.get_username(username_or_email)
        print(username)
        if self.db.log_in(username_or_email, self.hash_password(password)):
            topics = self.db.get_user_topics(username)
            email = self.db.get_user_email(username)
            followings_names = self.db.get_followings(username)
            msg = serverProtocol.build_sign_in_status(1,  username, email, topics, followings_names)

            self.clients[client_ip] = [username, serverCommVideos.ServerCommVideos(self.current_video_port), topics]

        self.comm.send_msg(client_ip, msg)

    def handle_set_user_topics(self, client_ip, data): # command 2
        topics = [int(t) for t in data]
        self.db.set_topics(self.clients[client_ip][0], topics)
        msg = serverProtocol.build_set_topics_confirmation(topics)
        self.comm.send_msg(client_ip, msg)

        self.db.print_tables()

    def handle_filter_user_topics(self, client_ip, data): # command 3
        topic_filter = [int(t) for t in data]
        self.clients[client_ip][2] = topic_filter
        msg = serverProtocol.build_set_filter_confirmation(1, topic_filter)
        self.comm.send_msg(client_ip, msg)

        print("set filter:", topic_filter)

    def handle_creators_search(self, client_ip, data): # command 4
        username = data[0]
        usernames = self.db.get_similar_usernames(username)

        #send username details and pfps
        for username in usernames[:settings.AMOUNT_OF_USERS_TO_SEND]:
            self.send_user_details(client_ip, username)
            print("sending video details")

    def send_user_details(self, client_ip, username): # Not a Command!
        #/get_creator_details
        followers = self.db.get_followers(username)
        followings = self.db.get_followings(username)
        video_count = self.db.get_video_amount(username)

        msg = serverProtocol.build_creator_details(username, followers,followings, video_count)
        self.comm.send_msg(client_ip, msg)

        #sends the user's pfp
        user_pfp_image_path = f"{username}.png"
        if os.path.isfile(user_pfp_image_path):
            self.clients[client_ip][1].send_file(user_pfp_image_path)



    def handle_videos_search(self, client_ip, data):  # command 5
        video_name_or_desc, topics = data

        video_ids_by_topics = set(self.db.get_videos_ids_by_topics(topics))

        video_ids_by_string = set(self.db.get_videos_with_similar_name(video_name_or_desc))

        video_ids_by_string += set(self.db.get_videos_with_similar_desc(video_name_or_desc))

        both_lists_together = list(set(video_ids_by_topics) & set(video_ids_by_string))

        ordered_by_views = self.db.order_ids_by_views(both_lists_together)

        # send username details and pfps
        for video_id in ordered_by_views[:settings.AMOUNT_OF_VIDEOS_TO_SEND]:
            self.send_video_details(client_ip, video_id)



    def send_video_details(self, client_ip, video_id): # Not a Command!
        video_id, creator_name, video_name, video_desc = self.db.get_specific_video(video_id)
        likes_amount = self.db.get_video_likes_amount(video_id)
        comments_amount = self.db.get_comments_amount(video_id)
        liked = self.db.is_liked_by_user(video_id, self.clients[client_ip][0])

        msg = serverProtocol.build_video_details(video_id, creator_name, video_name, video_desc, likes_amount,
                                                 comments_amount, liked)

        self.comm.send_msg(client_ip, msg)





    def handle_video_comment(self, client_ip, data):  # command 6
        video_id, comment = data
        pass

    def handle_test_req(self, client_ip, data):  # command 7
        video_id = data
        pass

    def handle_report(self, client_ip, data):  # command 8
        id = data
        pass

    def handle_comments_req(self, client_ip, data):  # command 9
        video_id, comment_id = data
        pass

    def handle_video_del(self, client_ip, data):  # command 10
        video_id = data
        pass

    def handle_del_comment(self, client_ip, data):  # command 11
        comment_id = data
        pass

    def handle_creator_videos_req(self, client_ip, data):  # command 12
        username = data
        pass

    def handle_user_follow_list_req(self, client_ip, data):  # command 13
        username, follow_type = data
        pass

    def handle_video_req(self, client_ip, data):  # command 14
        video_id = data[0]

        if video_id:
            self.clients[client_ip][1].send_file(client_ip, video_id)


    def handle_video_upload(self, client_ip, data):  # command 15
        video_name, video_desc, test_link = data

        video_id = self.db.add_video(self.clients[client_ip[0]], video_name, video_desc, test_link)
        # puts the id twice, once for the video and once for the thumbnail
        self.clients[client_ip[1]].idsQ.put(video_id)
        self.clients[client_ip[1]].idsQ.put(video_id)


    def handle_follow_user(self, client_ip, data):  # command 16
        username = data
        pass


    # Called by System Manager

    def handle_comment_or_video_remove(self, client_ip, data): # command 9
        id, type = data # type - 0 - comment, 1 - video
        pass

    def handle_user_kick(self, client_ip, data):
        username = data
        pass

    @staticmethod
    def hash_video(path: str, chunk_size: int = 1024 * 1024) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def hash_password(password: str, *, iterations: int = 200_000) -> str:
        salt = os.urandom(16)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return f"pbkdf2_sha256${iterations}${salt.hex()}${dk.hex()}"

if __name__ == "__main__":
    msgsQ = queue.Queue()
    ServerLogic()
