import time


import clientCommVideos
import clientProtocol
import clientComm
import queue
import settings
import threading
import ast
import user
import video
import comment


class ClientLogic:
    """Manages client-side logic for the UCademy project.
    Processes server messages
    """

    def __init__(self):
        """Initialize the ClientLogic object.

        """
        self.recvQ = queue.Queue()
        self.recvVQ = queue.Queue() # currently not in use
        self.comm = clientComm.ClientComm(self, settings.SERVER_IP, settings.PORT, self.recvQ)
        self.comm.connect()
        self.video_comm = None
        self.user = None
        self.filter = []
        
        self.videos = {} # [video_id] = video_object
        self.users = {} # [username] - user_object
        self.current_video = None
        
        self.commands = {
            "00": self.handle_reg_confirmation,
            "01": self.handle_email_verification_confirmation,
            "02": self.handle_sign_in_confirmation,
            "03": self.handle_topics_confirmation,
            "04": self.handle_filter_confirmation,
            "05": self.handle_user_details,
            "06": self.handle_video_details,
            "07": self.handle_video_comment_confirmation,
            "08": self.handle_test,
            "09": self.handle_report_status,
            "10": self.handle_comments,
            "11": self.handle_vid_del_confirmation,
            "12": self.handle_comment_del_confirmation,
            "16": self.handle_video_upload_confirmation,
            "17": self.handle_follow_status
        }
        self.video_commands = {
            "00": self.handle_video_details,
            "01": self.handle_confirm_file_upload
        }

        threading.Thread(target=self.handle_msgs, daemon=True).start()

    def quit(self):
        """Quit the game.

        """
        self.comm.close_client()

    def handle_msgs(self):
        """Process incoming messages from the server.

        Continuously retrieves messages from the receive queue and handles them based on opcode.
        """
        while True:
            msg = self.recvQ.get()

            if isinstance(msg, list):
                self.handle_video_details(msg)
            else:
                opcode, data = clientProtocol.unpack(msg)
                if opcode in self.commands:
                    self.commands[opcode](data)

    def handle_reg_confirmation(self, data):  # command 1
        status = data[0]
        status = [int(i) for i in status]
        if not any(status):
            print("an email verification code has been sent to the user's email account")
        else:
            username_status, password_status, email_status = status
            print("error signing up:")
            if username_status:
                print("username error: ",settings.USERNAME_ERRORS[username_status])
            if password_status:
                print("password error: ", settings.PASSWORD_ERRORS[password_status])
            if email_status:
                print("email error: ", settings.EMAIL_ERRORS[email_status])

    def handle_email_verification_confirmation(self, data):  # command 2
        status = data[0]
        status = int(status)
        if status:
            username, email, video_port= data[1:]
            video_port = int(video_port)
            self.video_comm = clientCommVideos.ClientCommVideos(self, settings.SERVER_IP, video_port, self.recvQ)
            self.video_comm.connect()
            self.user = user.User(username, 0, 0, 0, email)
        else:
            print("email verification failed, not a valid code")
            verification_code = input("Enter verification code: ")
            msg_to_send = clientProtocol.build_email_verification_code(verification_code)
            client.comm.send_msg(msg_to_send)

    def handle_sign_in_confirmation(self, data):  # command 2
        status = int(data[0])

        print("sign in status:",status)
        if status:
            video_port, username, followers_amount, followings_amount, videos_amount, email, topics, followings_names = data[1:]

            self.video_comm = clientCommVideos.ClientCommVideos(self, settings.SERVER_IP, int(video_port), self.recvQ)
            self.video_comm.connect()

            followers_amount = int(followings_amount)
            followings_amount = int(followings_amount)
            videos_amount = int(videos_amount)

            self.user = user.User(username, followers_amount, followings_amount, videos_amount,email, topics, followings_names)

    def handle_topics_confirmation(self, data):  # command 3
        topics = data[0]
        self.user.topics = topics

    def handle_filter_confirmation(self, data):  # command 4
        filter = data[0]
        self.filter = filter
        print("setting filter:", filter)

    def handle_user_details(self, data):  # command 5
        username, followers_amount, followings_amount, videos_amount = data

        if username:
            followers_amount = int(followers_amount)
            followings_amount = int(followings_amount)
            videos_amount = int(videos_amount)
            self.users[username] = user.User(username, followers_amount, followings_amount, videos_amount)
            print(f"added user: username: {username}, followers_amount: {followers_amount}, followings_amount: {followings_amount}, videos_amount: {videos_amount}")
        else:
            print("NO MORE USERS TO SEND")

    def handle_video_details(self, data):  # command 6
        video_id, creator, video_name, video_desc, created_at, likes_amount, comments_amount, liked, arrived_with_video = data

        video_id = int(video_id)
        if video_id: # video_id = 0 means that there are no more videos to send
            liked = bool(int(liked))
            self.videos[video_id] = video.Video(video_id, creator, video_name, video_desc, created_at,likes_amount, comments_amount, liked)
            print(
                f"added video: video_id={video_id}, creator={creator}, video_name={video_name}, video_desc={video_desc}, created_at = {created_at}, likes_amount={likes_amount}, comments_amount={comments_amount}, liked={liked}")
            if arrived_with_video:
                self.current_video = video_id
        else:
            print("NO MORE VIDEOS TO SEND")

    def handle_video_comment_confirmation(self, data):  # command 7
        comment_id, video_id, added_comment = data
        self.videos[video_id].comments.append(comment.Comment(comment_id, added_comment, self.user.username))

    def handle_test(self, data):  # command 8
        video_id, test_link = data

        if test_link:
            print(f"video {video_id} has test: {test_link}")

        if video_id in self.videos:
            self.videos[video_id].test_link = test_link # if no test link, test_link = ""

    def handle_report_status(self, data):  # command 9
        id, type, content, content_publisher, status = data[:5]
        type = int(type)
        id = int(id)

        msg2 = f"has been examined and it has been decided that the"

        msg1 = f"report of video {content} by {content_publisher}"
        type_str = "video"

        if type == settings.COMMENT_DIGIT_REPR:
            type_str = "comment"

            if content and content_publisher:
                comment, video_name = content
                commenter, video_creator = content_publisher
                msg1 = f"report of comment {comment} by {commenter} on video {video_name} by {video_creator}"

        if id:
            if status:
                date, time = data[5:]

                status = int(status)
                if status:
                    result = "will be removed"
                else:
                    result = "will not be removed"
                print(f"{msg1} you issued on {date} at {time} {msg2} {type_str} {result}")
            else:
                msg2 = "has been received at the server and will be examined"
                print(f"{msg1} {msg2}")

        else:
            if content and content_publisher:
                print(f"{msg1} has already been issued!")
            else:
                print(f"{type_str} reported does not exist!")

    def handle_comments(self, data):  # command 10
        # data = [[comment_info], [comment_info]]
        if data:
            for comment_info in data:
                comment_id, video_id, commenter, comment_content, created_at = comment_info
                video_id = int(video_id)
                comment_id = int(comment_id)
                self.videos[video_id].add_comment(comment.Comment(comment_id, comment_content, commenter, created_at))
                print(f"comment added: comment_id: {comment_id} content: {comment_content} by {commenter} created at {created_at}")
        else:
            print("no more comments")

    def handle_vid_del_confirmation(self, data):  # command 11
        video_id = int(data[0])
        if video_id:
            print(f"video {video_id} is deleted")
            self.videos.pop(video_id, None)
        else:
            print("video deletion failed")

    def handle_comment_del_confirmation(self, data):  # command 12
        video_id, comment_id = data
        video_id = int(video_id)
        comment_id = int(comment_id)
        if video_id:
            print(f"comment {comment_id} deleted from video {video_id}")
            video = self.videos.get(video_id)
            if video:
                video.comments.pop(comment_id, None)
        else:
            print("comment deletion failed")

    def handle_video_upload_confirmation(self, data):  # command 13
        status = data[0]
        print("video upload status:",status)

    def handle_follow_status(self, data):  # command 14
        status = data[0]
        pass
    #todo implement this, add to self.user i think

    # called by the video_comm
    def handle_confirm_file_upload(self, data):  # command 01
        status = data[0]
        print(status)


if __name__ == "__main__":
    """Main entry point to run the client."""
    client = ClientLogic()
    time.sleep(0.1)

    # test command 0
    # msg_to_send = clientProtocol.build_sign_up("Barak3", "password123", "bbmalt9@gmail.com")
    # client.comm.send_msg(msg_to_send)
    
    #test command 1
    # verification_code = input("Enter verification code: ")
    # msg_to_send = clientProtocol.build_email_verification_code(verification_code)
    # client.comm.send_msg(msg_to_send)
    
    
    # test command 2
    msg_to_send = clientProtocol.build_sign_in("Barak2", "password123")
    client.comm.send_msg(msg_to_send)

    time.sleep(1)

    # test command 3
    # msg_to_send = clientProtocol.build_set_topics([2, 3, 4])
    # client.comm.send_msg(msg_to_send)

    # test command 4
    # msg_to_send = clientProtocol.build_set_filter([5, 6, 7])
    # client.comm.send_msg(msg_to_send)

    #test command 5
    # msg_to_send = clientProtocol.build_search_videos("video", None, 0)
    # client.comm.send_msg(msg_to_send)


    #test command 6
    # msg_to_send = clientProtocol.build_comment(1, "hello man")
    # client.comm.send_msg(msg_to_send)

    #test command 7

    # msg_to_send = clientProtocol.build_req_test(1)
    # client.comm.send_msg(msg_to_send)

    # test command 8

    # msg_to_send = clientProtocol.build_report(1, 0)
    # client.comm.send_msg(msg_to_send)

    #test command 9 (requires command 14 first)
    # msg_to_send = clientProtocol.build_req_comments(1)
    # client.comm.send_msg(msg_to_send)


    #test command 10
    # msg_to_send = clientProtocol.build_del_video(1)
    # client.comm.send_msg(msg_to_send)

    #test command 11
    # msg_to_send = clientProtocol.build_del_comment(5)
    # client.comm.send_msg(msg_to_send)

    #test command 12
    # msg_to_send = clientProtocol.build_req_creator_videos("Alon")
    # client.comm.send_msg(msg_to_send)

    #test command 13
    # msg_to_send = clientProtocol.build_req_user_follow_list("Barak", 0)
    # client.comm.send_msg(msg_to_send)

    #test command 14
    msg_to_send = clientProtocol.build_req_video(1)
    client.comm.send_msg(msg_to_send)

    #video comm
    #test command 0
    # client.video_comm.send_file("15.txt", "video name", "video desc", "test link")
    # client.video_comm.send_file("35.abc")
    # client.video_comm.send_file("barak.txt")



    time.sleep(0.5)
    # print(client.user)

    while True:
        pass

