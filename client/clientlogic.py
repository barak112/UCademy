import time

import clientCommVideos
import clientProtocol
import clientComm
import queue
import settings
import threading
import ast
import user


class ClientLogic:
    """Manages client-side logic for the UCademy project.
    Processes server messages
    """

    def __init__(self):
        """Initialize the ClientLogic object.

        """
        self.recvQ = queue.Queue()
        self.recvVQ = queue.Queue()
        self.comm = clientComm.ClientComm(self, settings.SERVER_IP, settings.PORT, self.recvQ)
        self.comm.connect()
        self.video_comm = None
        self.user = None
        self.filter = []
        self.commands = {
            "00": self.handle_reg_confirmation,
            "01": self.handle_sign_in_confirmation,
            "02": self.handle_topics_confirmation,
            "03": self.handle_filter_confirmation,
            "04": self.handle_user_details,
            "05": self.handle_video_details,
            "06": self.handle_video_comment_confirmation,
            "07": self.handle_test,
            "08": self.handle_report_status,
            "09": self.handle_comments,
            "10": self.handle_vid_del_confirmation,
            "11": self.handle_comment_del_confirmation,
            "15": self.handle_video_upload_confirmation,
            "16": self.handle_follow_status
        }
        self.video_commands = {
            "01": self.handle_confirm_file_upload
        }

        threading.Thread(target=self.handle_msgs, daemon=True).start()
        threading.Thread(target=self.handle_video_msgs, daemon=True).start()

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

    def handle_video_msgs(self):
        """Process incoming messages from the server.

        Continuously retrieves messages from the receive queue and handles them based on opcode.
        """
        while True:
            msg = self.recvVQ.get()
            opcode, data = clientProtocol.unpack(msg)
            if opcode in self.video_commands:
                self.video_commands[opcode](data)

    def handle_reg_confirmation(self, data):
        status = int(data[0])
        if status:
            video_port = int(data[1])
            self.video_comm = clientCommVideos.ClientCommVideos(self, settings.SERVER_IP, video_port, self.recvVQ)
            self.video_comm.connect()

        print("sign up status:",status)

    def handle_sign_in_confirmation(self, data):
        status = int(data[0])

        print("sign in status:",status)
        print(data)
        if status:
            username, email, topics, followings_names = data[1:]
            topics = ast.literal_eval(topics)

            self.user = user.User(username, email, topics, followings_names)


    def handle_topics_confirmation(self, data):
        topics = data[0]
        self.user.topics = topics

    def handle_filter_confirmation(self, data):
        filter = ast.literal_eval(data[0])
        self.filter = filter
        print("setting filter:", filter)

    def handle_user_details(self, data):
        username, followers_amount, videos_amount = data

        print("receiving video details")

    def handle_video_details(self, data):
        video_id, creator, name, desc, likes_amount, comments_amount, liked = data
        pass

    def handle_video_comment_confirmation(self, data):
        status = data[0]
        pass

    def handle_test(self, data):
        test_link = data[0]
        pass

    def handle_report_status(self, data):
        id, type, status = data
        pass

    def handle_comments(self, data):
        comment_id, comment, creator = data
        pass

    def handle_vid_del_confirmation(self, data):
        status = data[0]
        pass

    def handle_comment_del_confirmation(self, data):
        status = data[0]
        pass

    def handle_video_upload_confirmation(self, data):
        status = data[0]
        print(status)

    def handle_follow_status(self, data):
        status = data[0]
        pass

    # called by the video_comm
    def handle_confirm_file_upload(self, data):
        status = data[0]
        pass


if __name__ == "__main__":
    """Main entry point to run the client."""
    client = ClientLogic()
    time.sleep(0.1)

    msg_to_send = clientProtocol.build_sign_up("Alon", "password123", "Alon@")
    client.comm.send_msg(msg_to_send)

    msg_to_send = clientProtocol.build_sign_in("Alon", "password123")
    client.comm.send_msg(msg_to_send)

    msg_to_send = clientProtocol.build_set_topics([2, 3, 4])
    client.comm.send_msg(msg_to_send)

    msg_to_send = clientProtocol.build_set_filter([5, 6, 7])
    client.comm.send_msg(msg_to_send)

    #command 15


    time.sleep(0.5)
    print(client.user)

    while True:
        pass

