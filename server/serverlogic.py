import ast
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
                self.handle_video_upload(ip, msg)
            else:
                opcode, data = serverProtocol.unpack(msg)

                if opcode in self.commands.keys():
                    self.commands[opcode](ip, data)

    def handle_registration(self, client_ip, data): # command 0
        username, password, email = data

        msg = serverProtocol.build_sign_up_status(0)
        if self.db.add_user(username, email, self.hash_password(password)):
            self.clients[client_ip] = [username, serverCommVideos.ServerCommVideos(self.current_video_port, self.recvQ), []]

            msg = serverProtocol.build_sign_up_status(1, self.current_video_port)

        self.current_video_port+=1

        self.comm.send_msg(client_ip, msg)

    def handle_sign_in(self, client_ip, data): #command 1
        username_or_email, password = data
        msg = serverProtocol.build_sign_in_status(0)
        status = 0
        username = self.db.get_username(username_or_email)
        print(f"trying to sign in user: {username} ")
        if self.db.log_in(username_or_email, password):
            topics = self.db.get_user_topics(username)
            email = self.db.get_user_email(username)
            followings_names = self.db.get_followings(username)
            msg = serverProtocol.build_sign_in_status(1,self.current_video_port,  username, email, topics, followings_names)
            status = 1
            self.clients[client_ip] = [username, serverCommVideos.ServerCommVideos(self.current_video_port, self.recvQ), topics]
            self.current_video_port+=1

        self.comm.send_msg(client_ip, msg)
        print(f"sign in status for {username} is {status}")

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
        topics = ast.literal_eval(topics)

        video_ids_by_string = set(self.db.get_videos_with_similar_name(video_name_or_desc))
        both_lists_together = video_ids_by_string | set(self.db.get_videos_with_similar_desc(video_name_or_desc))

        if topics:
            video_ids_by_topics = set(self.db.get_videos_ids_by_topics(topics))
            both_lists_together = list(set(video_ids_by_topics) & set(both_lists_together))

        ordered_by_views = self.db.order_ids_by_views(both_lists_together)

        # send username details and pfps
        for video_id in ordered_by_views[:settings.AMOUNT_OF_VIDEOS_TO_SEND]:
            video_id, creator, video_name, video_desc, likes_amount, comments_amount, liked = self.get_video_details(client_ip, video_id)
            self.clients[client_ip][1].send_file(client_ip, f"media\\videos\\{video_id}.png", video_id, creator,
                                                 video_name, video_desc, likes_amount, comments_amount, liked)


    def handle_video_comment(self, client_ip, data):  # command 6
        video_id, comment = data
        commenter_name = self.clients[client_ip][0]
        comment_id = self.db.add_comment(video_id, commenter_name, comment)
        msg = serverProtocol.build_comment_status(comment_id,video_id, comment)
        self.comm.send_msg(client_ip, msg)

    def handle_test_req(self, client_ip, data):  # command 7
        video_id = data[0]
        video_link = self.db.get_video_test_link(video_id)

        msg = serverProtocol.build_send_test(video_id, video_link)
        self.comm.send_msg(client_ip, msg)

    def handle_report(self, client_ip, data):  # command 8
        id = data
        pass

    def handle_comments_req(self, client_ip, data):  # command 9
        """
            :param data: video_id,, last_comment_id
            last_comment_id -> used to determine which comments should be next to be sent to the client.
            last_comment_id is the last comment's id the client has received.
            if last_comment_id = 0. it means that its the first time the client has requested comments.
        """
        print("comments req arriveed at handle")
        video_id, last_comment_id = data
        comments_ids, comments = self.db.get_comments(video_id, self.clients[client_ip][0])

        last_comment_id = int(last_comment_id)
        start_index = 0
        if last_comment_id:
            start_index = comments_ids.index(last_comment_id)


        comments_to_send = comments[start_index:start_index+settings.AMOUNT_OF_COMMENTS_TO_SEND]

        print("comments_to_send:",comments_to_send)

        msg = serverProtocol.build_send_comments(comments_to_send)
        print("msg of comments:",msg)
        self.clients[client_ip][1].send_msg(client_ip, msg)

        commenters = {i[2] for i in comments_to_send}
        # send pfps
        for commenter_name in commenters:
            pfp_path = f"media\\pfps\\{commenter_name}.png"
            self.clients[client_ip][1].send_file(client_ip,pfp_path)
            print("sending pfp of user:",commenter_name)



    def handle_video_del(self, client_ip, data):  # command 10
        video_id = data[0]
        print("trying to deleting video:",video_id)

        msg = serverProtocol.build_del_video_confirmation(0)
        if client_ip in self.clients and self.db.is_the_video_creator(video_id, self.clients[client_ip][0]):
            self.db.delete_video(video_id)
            msg = serverProtocol.build_del_video_confirmation(video_id)

        self.comm.send_msg(client_ip, msg)

    def handle_del_comment(self, client_ip, data):  # command 11
        comment_id = data[0]
        msg = serverProtocol.build_del_comment_confirmation(0)
        comment = self.db.get_comment(comment_id)
        if comment:
            self.db.delete_comment(comment_id)
            video_id = comment[1]
            msg = serverProtocol.build_del_comment_confirmation(video_id, comment_id)
            print("deleting comment")
        self.comm.send_msg(client_ip, msg)


    def handle_creator_videos_req(self, client_ip, data):  # command 12
        username = data
        #todo: implement
        pass

    def handle_user_follow_list_req(self, client_ip, data):  # command 13
        username, follow_type = data
        pass

    def handle_video_req(self, client_ip, data):  # command 14
        video_id = data[0]
        if video_id:
            video_id, creator, video_name, video_desc, likes_amount, comments_amount, liked = self.get_video_details(client_ip, video_id)
            file_path = f"media\\videos\\{video_id}.{settings.VIDEO_EXTENSION}"
            self.clients[client_ip][1].send_file(client_ip, file_path, video_id, creator, video_name, video_desc, likes_amount, comments_amount, liked)
            print(
                f"sending video {video_id} to {client_ip} with creator {creator}, name {video_name}, desc {video_desc}, likes {likes_amount}, comments {comments_amount}, liked {liked}"
            )
        else:
            # algorithm to choose video
            pass

    def get_video_details(self,client_ip, video_id):
        video_name, video_desc, creator, likes_amount, comments_amount = self.db.get_specific_video(video_id)
        liked = self.db.is_liked_by_user(video_id, self.clients[client_ip][0])
        liked = int(liked)
        return video_id, creator, video_name, video_desc, likes_amount, comments_amount, liked

    def handle_follow_user(self, client_ip, data):  # command 16
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

    def handle_comment_or_video_remove(self, client_ip, data): # command 9
        id, type = data # type - 0 - comment, 1 - video
        pass

    def handle_user_kick(self, client_ip, data):
        username = data
        pass

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
