import time

import clientCommVideos
import graphics
import clientProtocol
import clientComm
import queue
import settings
import threading


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

        print("status:",status)

    def handle_sign_in_confirmation(self, data):
        status = data[0]

        if status:
            username, email, topics = data[1:]

    def handle_topics_confirmation(self, data):
        status = data[0]
        pass

    def handle_filter_confirmation(self, data):
        status = data[0]
        pass

    def handle_user_details(self, data):
        username, followers_amount, videos_amount = data
        pass

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
        pass

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

    msg_to_send = clientProtocol.build_sign_up("Barak", "passwword123", "barakbm9")
    time.sleep(0.1)
    client.comm.send_msg(msg_to_send)
    while True:
        pass

