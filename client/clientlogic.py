import time
import clientCommVideos
import clientProtocol
import clientComm
import queue
import settings
import threading
import user
import video
import comment
from pubsub import pub
import wx
from main_frame import MainFrame

class ClientLogic:
    """Manages client-side logic for the UCademy project.
    Processes server messages
    """

    def __init__(self):
        """Initialize the ClientLogic object.

        """
        self.recvQ = queue.Queue()
        self.comm = clientComm.ClientComm(self, settings.SERVER_IP, settings.PORT, self.recvQ)
        self.comm.connect()

        self.commands = {
            "00": self.handle_reg_confirmation,
            "01": self.handle_email_verification_confirmation,
            "02": self.handle_sign_in_confirmation,
            "03": self.handle_topics_confirmation,
            "04": self.handle_filter_confirmation,
            "05": self.handle_user_details_in_search,
            "06": self.handle_video_details_in_search,
            "07": self.handle_video_comment_confirmation,
            "08": self.handle_user_details_in_profile,
            "09": self.handle_report_status,
            "10": self.handle_comments,
            "11": self.handle_vid_del_confirmation,
            "12": self.handle_comment_del_confirmation,
            "13": self.handle_video_details_in_profile,
            "14":self.handle_user_details_in_follow_list,
            "15": self.handle_load_new_video,
            "16": self.handle_video_upload_confirmation,
            "17": self.handle_follow_status,
            "18": self.handle_like_video,
            "19": self.update_pfp
        }
        self.video_commands = {
            # "00": self.handle_video_details,
            "01": self.handle_confirm_file_upload
        }

        threading.Thread(target=self.handle_msgs, daemon=True).start()

    def getComm(self):
        return self.comm

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

            opcode, data = clientProtocol.unpack(msg)
            if opcode in self.commands:
                self.commands[opcode](data)

    def handle_reg_confirmation(self, data):  # command 0
        status = data[0]
        status = [int(i) for i in status]
        wx.CallAfter(pub.sendMessage, "signup_ans", status=status)

    def handle_email_verification_confirmation(self, data):  # command 1
        status = data[0]
        status = int(status)
        if status == settings.EMAIL_VERIFICATION_SUCCESSFUL:
            username, email, video_port = data[1:]
            video_port = int(video_port)
            video_comm = clientCommVideos.ClientCommVideos(self, settings.SERVER_IP, video_port, self.recvQ)
            video_comm.connect()
            self.user = user.User(username, 0, 0, 0, email)

        wx.CallAfter(pub.sendMessage,"email_verification_ans", status = status, video_comm = video_comm, user = self.user)

    def handle_sign_in_confirmation(self, data):  # command 2
        status = int(data[0])

        print("sign in status:", status)
        if status:
            video_port, username, followers_amount, followings_amount, videos_ids, email, topics, followings_names = data[
                1:]


            video_comm = clientCommVideos.ClientCommVideos(self, settings.SERVER_IP, int(video_port), self.recvQ)
            video_comm.connect()

            followers_amount = int(followings_amount)
            followings_amount = int(followings_amount)

            user_obj = user.User(username, followers_amount, followings_amount, videos_ids, email, topics,
                                  followings_names)

            print(f"signed in as {username}")
            wx.CallAfter(pub.sendMessage, "login_ans", status=status, video_comm=video_comm, user=user_obj)
        else:
            wx.CallAfter(pub.sendMessage, "login_ans", status=status)
            print("one of the credentials inputted is incorrect")

    def handle_topics_confirmation(self, data):  # command 3
        topics = data[0]
        topics = [int(topic) for topic in topics]
        wx.CallAfter(pub.sendMessage, "set_topics_ans", topics = topics)

    def handle_filter_confirmation(self, data):  # command 4
        filter = data[0]
        print("setting filter:", filter)
        wx.CallAfter(pub.sendMessage, "set_filter_ans", filter=filter)

    def handle_user_details_in_search(self, data):  # command 5
        user_obj = self.get_user_obj(data)
        wx.CallAfter(pub.sendMessage, "user_details_ans", user=user_obj)

    @staticmethod
    def get_user_obj(data): # helper function
        username, followers_amount, followings_amount, videos_ids = data
        followers_amount = int(followers_amount)
        followings_amount = int(followings_amount)
        videos_ids = [int(i) for i in videos_ids]
        user_details = user.User(username, followers_amount, followings_amount, videos_ids)
        return user_details

    def handle_video_details_in_search(self, data):  # command 6
        video_obj = self.get_video_obj(data)
        wx.CallAfter(pub.sendMessage, "load_video", video =video_obj)

    @staticmethod
    def get_video_obj(data): # helper function
        video_id, creator, video_name, video_desc, created_at, likes_amount, comments_amount, liked = data
        print("video_id:",video_id,"comments amount:", comments_amount)
        video_id = int(video_id)
        comments_amount = int(comments_amount)
        likes_amount = int(likes_amount)
        liked = bool(int(liked))
        video_details = video.Video(video_id, creator, video_name, video_desc, created_at, likes_amount,
                                    comments_amount, liked)
        return video_details

    def handle_video_comment_confirmation(self, data):  # command 7
        print('data:', data)
        comment_id, video_id, commenter, added_comment, created_at = data
        comment_id = int(comment_id)
        video_id = int(video_id)
        comment_obj = comment.Comment(comment_id, added_comment, commenter, created_at)

        print("calling after")
        wx.CallAfter(pub.sendMessage, "added_comment", video_id = video_id, comment = comment_obj)


    def handle_user_details_in_profile(self, data):  # command 8
        user_obj = self.get_user_obj(data)

        wx.CallAfter(pub.sendMessage, "user_details_in_profile_ans", user = user_obj)


    def handle_report_status(self, data):  # command 9
        print(data, "1")
        status, id, type, content, content_publisher, created_at = data
        status = int(status)
        type = int(type)
        # id will be future used to view the reported content if it is decided to not be removed

        msg2 = f"has been examined and it has been decided that the"

        msg1 = f"report of video {content} by {content_publisher}"

        type_str = "video" if status == settings.VIDEO_DIGIT_REPR else "comment"

        if type == settings.COMMENT_DIGIT_REPR and content and content_publisher:
            comment, video_name = content
            commenter, video_creator = content_publisher
            msg1 = f"report of comment {comment} by {commenter} on video {video_name} by {video_creator}"

        # Determine the message based on status
        status_messages = {
            settings.REPORT_DENIED: f"{msg1} you issued on {created_at} {msg2} {type_str} will not be removed",
            settings.REPORT_ACCEPTED: f"{msg1} you issued on {created_at} {msg2} {type_str} will be removed",
            settings.REPORT_CONTENT_DOESNT_EXISTS: f"{type_str} reported does not exist!",
            settings.REPORT_ALREADY_ISSUED: f"{msg1} has already been issued by you!",
            settings.REPORT_RECEIVED: f"{msg1} has been received at the server and will be examined",
            settings.REPORT_CONCLUDED: f"{msg1} has already been concluded"
        }

        print(status_messages[status])

    def handle_comments(self, data):  # command 10
        # data = [[comment_info], [comment_info]]
        comments = []
        video_id = 0
        for comment_info in data:
            comment_id, video_id, commenter, comment_content, created_at = comment_info
            video_id = int(video_id)
            comment_id = int(comment_id)
            comments.append(comment.Comment(comment_id, comment_content, commenter, created_at))
            print(
                f"comment added: comment_id: {comment_id} content: {comment_content} by {commenter} created at {created_at}")

        print("video id in handle comments:", video_id)
        wx.CallAfter(pub.sendMessage, "load_new_comments", video_id = video_id, comments = comments)
            #todo maybe change so that comments are sent as video_id@#[...]@#[...]@#[...] so the video id wouldnt be sent with each comment

    def handle_vid_del_confirmation(self, data):  # command 11
        video_id = int(data[0])
        if video_id:
            print(f"video {video_id} is deleted")
        else:
            print("video deletion failed")

        wx.CallAfter(pub.sendMessage, "video_del_ans", video_id = video_id)

    def handle_comment_del_confirmation(self, data):  # command 12
        video_id, comment_id = data
        video_id = int(video_id)
        comment_id = int(comment_id)
        if video_id:
            print(f"comment {comment_id} deleted from video {video_id}")
        else:
            print("comment deletion failed")

        wx.CallAfter(pub.sendMessage, "video_del_ans", video_id=video_id)

    def handle_video_details_in_profile(self, data): # command 13
        video_obj = self.get_video_obj(data)
        wx.CallAfter(pub.sendMessage, "video_details_in_profile_ans", video=video_obj)

    def handle_user_details_in_follow_list(self, data):
        user_obj = self.get_user_obj(data)
        wx.CallAfter(pub.sendMessage, "user_details_in_follow_list_ans", user=user_obj)

    def handle_load_new_video(self, data): # command 15
        video_obj = self.get_video_obj(data)
        wx.CallAfter(pub.sendMessage, "load_new_video", video=video_obj)

    def handle_video_upload_confirmation(self, data):  # command 16
        video_id = data[0]
        video_id = int(video_id)
        wx.CallAfter(pub.sendMessage, "video_upload_ans", video_id=video_id)

    def handle_follow_status(self, data):  # command 17
        status, following = data

        if following:
            # self.user.followings.append(following)
            pass
        else:
            print("user trying to follow doesnt exists")

        wx.CallAfter(pub.sendMessage, "follow_ans", status=status, following = following)

    def handle_like_video(self, data): # command 18
        status, video_id = data
        status = int(status)
        video_id = int(video_id)

        wx.CallAfter(pub.sendMessage, "video_like_ans", status = status, video_id = video_id)

    def update_pfp(self, data): # command 19
        wx.CallAfter(pub.sendMessage, "update_pfp_ans")

    # called by the video_comm

    # command 0 is command 6 in the regular commands

    def handle_confirm_file_upload(self, data):  # command 01
        status = data[0]
        print(status)


if __name__ == "__main__":
    """Main entry point to run the client."""
    client = ClientLogic()
    time.sleep(0.1)

    app = wx.App()
    frame = MainFrame(client.getComm())
    frame.Show()
    app.MainLoop()



    # test command 0
    # msg_to_send = clientProtocol.build_sign_up("Barak", "password123", "bbmalt9@gmail.com")
    # client.comm.send_msg(msg_to_send)
    # #
    # #test command 1
    # verification_code = input("Enter verification code: ")
    # msg_to_send = clientProtocol.build_email_verification_code(verification_code)
    # client.comm.send_msg(msg_to_send)

    # test command 2
    # msg_to_send = clientProtocol.build_sign_in("Barak", "password123")
    # client.comm.send_msg(msg_to_send)
    #
    # time.sleep(1)

    # test command 3
    # msg_to_send = clientProtocol.build_set_topics([2, 3, 4])
    # client.comm.send_msg(msg_to_send)

    # test command 4
    # msg_to_send = clientProtocol.build_set_filter([5, 6, 7])
    # client.comm.send_msg(msg_to_send)

    # test command 5
    # msg_to_send = clientProtocol.build_search_videos("video", None, 0)
    # client.comm.send_msg(msg_to_send)

    # test command 6
    # msg_to_send = clientProtocol.build_comment(1, "hello man")
    # client.comm.send_msg(msg_to_send)

    # test command 7

    # msg_to_send = clientProtocol.build_req_test(1)
    # client.comm.send_msg(msg_to_send)

    # test command 8

    # msg_to_send = clientProtocol.build_report(2, 1)
    # client.comm.send_msg(msg_to_send)

    # test command 9 (requires command 14 first)
    # msg_to_send = clientProtocol.build_req_comments(1)
    # client.comm.send_msg(msg_to_send)

    # test command 10
    # msg_to_send = clientProtocol.build_del_video(1)
    # client.comm.send_msg(msg_to_send)

    # test command 11
    # msg_to_send = clientProtocol.build_del_comment(5)
    # client.comm.send_msg(msg_to_send)

    # test command 12
    # msg_to_send = clientProtocol.build_req_creator_videos("Alon")
    # client.comm.send_msg(msg_to_send)

    # test command 13
    # msg_to_send = clientProtocol.build_req_user_follow_list("Barak", 0)
    # client.comm.send_msg(msg_to_send)

    # test command 14
    # msg_to_send = clientProtocol.build_req_video(1)
    # client.comm.send_msg(msg_to_send)

    # video comm
    # test command 0
    # client.video_comm.send_file("15.txt", "video name", "video desc", "test link")
    # client.video_comm.send_file("35.abc")
    # client.video_comm.send_file("barak.txt")

    # test system manager

    # msg_to_send = clientProtocol.build_comment_or_video_status(2, 1, settings.REPORT_ACCEPTED)
    # client.comm.send_msg(msg_to_send)
    #
    # time.sleep(0.5)
    # # print(client.user)
    #
    # while True:
    #     pass

