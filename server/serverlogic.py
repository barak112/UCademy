import hashlib
import os.path
import queue
import threading

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
        self.commands = {'00':self.handle_registration
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
            print("ip, msg",ip, msg)
            opcode, data = serverProtocol.unpack(msg)

            if opcode in self.commands.keys():
                self.commands[opcode](ip, data)

    def handle_registration(self, client_ip, data):
        username, password, email = data
        print("register user")


        msg = serverProtocol.build_sign_up_status(0)
        if self.db.add_user(username, email, self.hash_password(password)):
            self.clients[client_ip] = [username, serverCommVideos.ServerCommVideos(self.current_video_port), []]

            msg = serverProtocol.build_sign_up_status(1, self.current_video_port)

        self.current_video_port+=1

        self.comm.send_msg(client_ip, msg)


    def handle_sign_in(self, client_ip, data):
        username_or_email, password = data
        msg = serverProtocol.build_sign_in_status(0)

        if self.db.log_in(username_or_email, self.hash_password(password)):
            username = self.clients[client_ip][0]
            topics = self.db.get_user_topics(username)
            email = self.db.get_user_email(username)
            followings_names = self.db.get_followings(username)
            topic_filter = self.clients[client_ip][2]
            msg = serverProtocol.build_sign_in_status(topics, username, email, topic_filter, followings_names)


        self.comm.send_msg(client_ip, msg)

    def handle_set_user_topics(self, client_ip, data):
        topics = data
        self.db.set_topics(self.clients[client_ip][0], topics)
        msg = serverProtocol.build_set_topics_confirmation(1)
        self.comm.send_msg(client_ip, msg)

    def handle_filter_user_topics(self, client_ip, data):
        topics = data
        self.clients[client_ip][2] = topics
        msg = serverProtocol.build_set_filter_confirmation(1)
        self.comm.send_msg(client_ip, msg)

    def handle_creators_search(self, client_ip, data):
        username = data[0]
        usernames = self.db.get_similar_usernames(username)

        #send username details and pfps
        for username in usernames[:settings.AMOUNT_OF_USERS_TO_SEND]:
            self.send_user_details(client_ip, username)


    def send_user_details(self, client_ip, username): # command 4
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



    def handle_videos_search(self, client_ip, data):
        video_name_or_desc, topics = data

        video_ids_by_topics = set(self.db.get_videos_ids_by_topics(topics))

        video_ids_by_string = set(self.db.get_videos_with_similar_name(video_name_or_desc))

        video_ids_by_string += set(self.db.get_videos_with_similar_desc(video_name_or_desc))

        both_lists_together = list(set(video_ids_by_topics) & set(video_ids_by_string))

        ordered_by_views = self.db.order_ids_by_views(both_lists_together)

        # send username details and pfps
        for video_id in ordered_by_views[:settings.AMOUNT_OF_VIDEOS_TO_SEND]:
            self.send_video_details(client_ip, video_id)



    def send_video_details(self, client_ip, video_id):
        video_id, creator_name, video_name, video_desc = self.db.get_specific_video(video_id)
        likes_amount = self.db.get_video_likes_amount(video_id)
        comments_amount = self.db.get_comments_amount(video_id)
        liked = self.db.is_liked_by_user(video_id, self.clients[client_ip][0])

        msg = serverProtocol.build_video_details(video_id, creator_name, video_name, video_desc, likes_amount,
                                                 comments_amount, liked)

        self.comm.send_msg(client_ip, msg)





    def handle_video_comment(self, client_ip, data):
        video_id, comment = data
        pass

    def handle_test_req(self, client_ip, data):
        video_id = data
        pass

    def handle_report(self, client_ip, data):
        id = data
        pass

    def handle_comments_req(self, client_ip, data):
        video_id, comment_id = data
        pass

    def handle_video_del(self, client_ip, data):
        video_id = data
        pass

    def handle_del_comment(self, client_ip, data):
        comment_id = data
        pass

    def handle_creator_videos_req(self, client_ip, data):
        username = data
        pass

    def handle_user_follow_list_req(self, client_ip, data):
        username, follow_type = data
        pass

    def handle_video_req(self, client_ip, data):
        video_id = data[0]

        if video_id:
            self.clients[client_ip][1].send_file(client_ip, video_id)


    def handle_video_upload(self, client_ip, data):
        video_name, video_desc, test_link = data
        pass

    def handle_follow_user(self, client_ip, data):
        username = data
        pass

    # Called by System Manager
    def handle_comment_or_video_remove(self, client_ip, data):
        id = data
        pass

    def handle_user_kick(self, client_ip, data):
        username = data
        pass

    def hash_password(self, password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

if __name__ == "__main__":
    msgsQ = queue.Queue()
    ServerLogic()
