import settings


class ClientLogic:
    """Manages client-side logic for the UCademy project.
    Processes server messages
    """

    def __init__(self):
        """
        Initialize the ClientLogic object and set up communication, queues, and state containers.
        """
        self.recvQ = queue.Queue()
        self.recvVQ = queue.Queue()
        self.comm = clientComm.ClientComm(self, settings.SERVER_IP, settings.PORT, self.recvQ)
        self.comm.connect()
        self.video_comm = None
        self.user = None
        self.filter = []

        self.videos = {}
        self.users = {}
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
        """
        Close the client connection and terminate communication with the server.
        """
        self.comm.close_client()

    def handle_msgs(self):
        """
        Continuously process incoming messages and route them to the correct handler.
        """
        while True:
            msg = self.recvQ.get()

            if isinstance(msg, list):
                self.handle_video_details(msg)
            else:
                opcode, data = clientProtocol.unpack(msg)
                if opcode in self.commands:
                    self.commands[opcode](data)

    def handle_reg_confirmation(self, data):
        """
        Process registration confirmation and display success or error messages.
        :param data: List of status codes for username, password, and email validation.
        """
        status = [int(i) for i in data[0]]
        if not any(status):
            print("an email verification code has been sent to the user's email account")
        else:
            print("error signing up:")
            if [status[0]]:
                print(settings.USERNAME_ERRORS[status[0]])
            if [status[1]]:
                print(settings.PASSWORD_ERRORS[status[1]])
            if [status[2]]:
                print(settings.EMAIL_ERRORS[status[2]])

    def handle_email_verification_confirmation(self, data):
        """
        Handle email verification result and initialize user/video communication if successful.
        :param data: List containing verification status and connection details.
        """
        status = int(data[0])
        if status:
            username, email, video_port = data[1:]
            self.video_comm = clientCommVideos.ClientCommVideos(self, settings.SERVER_IP, int(video_port), self.recvQ)
            self.video_comm.connect()
            self.user = user.User(username, 0, 0, 0, email)

    def handle_sign_in_confirmation(self, data):
        """
        Handle sign-in response and initialize user state and video communication.
        :param data: List containing sign-in status and user information.
        """
        status = int(data[0])
        if status:
            video_port, username, followers, followings, videos, email, topics, followings_names = data[1:]
            self.video_comm = clientCommVideos.ClientCommVideos(self, settings.SERVER_IP, int(video_port), self.recvQ)
            self.video_comm.connect()
            self.user = user.User(username, int(followers), int(followings), int(videos), email, topics,
                                  followings_names)

    def handle_topics_confirmation(self, data):
        """
        Update user's topics preferences.
        :param data: List of topic identifiers.
        """
        self.user.topics = data[0]

    def handle_filter_confirmation(self, data):
        """
        Update current video filter settings.
        :param data: List of filter identifiers.
        """
        self.filter = data[0]

    def handle_user_details(self, data):
        """
        Store received user details in the local cache.
        :param data: Tuple of username, followers count, followings count, and videos count.
        """
        username, followers, followings, videos = data
        if username:
            self.users[username] = user.User(username, int(followers), int(followings), int(videos))

    def handle_video_details(self, data):
        """
        Store video metadata and update current video if needed.
        :param data: Tuple containing video details such as id, creator, name, description, stats, etc.
        """
        video_id, creator, name, desc, created_at, likes, comments, liked, arrived = data
        video_id = int(video_id)

        if video_id:
            self.videos[video_id] = video.Video(video_id, creator, name, desc, created_at, likes, comments,
                                                bool(int(liked)))
            if arrived:
                self.current_video = video_id

    def handle_video_comment_confirmation(self, data):
        """
        Add a new comment to a video.
        :param data: Tuple containing comment ID, video ID, and comment text.
        """
        comment_id, video_id, content = data
        self.videos[video_id].comments.append(comment.Comment(comment_id, content, self.user.username))

    def handle_test(self, data):
        """
        Attach a test link to a video.
        :param data: Tuple containing video ID and test link.
        """
        video_id, link = data
        if video_id in self.videos:
            self.videos[video_id].test_link = link

    def handle_report_status(self, data):
        """
        Process report result and display status message.
        :param data: Tuple containing report result and metadata.
        """
        print(data)

    def handle_comments(self, data):
        """
        Add multiple comments to their corresponding videos.
        :param data: List of comment tuples.
        """
        if data:
            for comment_info in data:
                comment_id, video_id, commenter, content, created_at = comment_info
                self.videos[int(video_id)].add_comment(comment.Comment(int(comment_id), content, commenter, created_at))

    def handle_vid_del_confirmation(self, data):
        """
        Remove a video after deletion confirmation.
        :param data: List containing video ID.
        """
        video_id = int(data[0])
        if video_id:
            self.videos.pop(video_id, None)

    def handle_comment_del_confirmation(self, data):
        """
        Remove a comment after deletion confirmation.
        :param data: Tuple containing video ID and comment ID.
        """
        video_id, comment_id = map(int, data)
        video = self.videos.get(video_id)
        if video:
            video.comments.pop(comment_id, None)

    def handle_video_upload_confirmation(self, data):
        """
        Display video upload result.
        :param data: List containing upload status.
        """
        print("video upload status:", data[0])

    def handle_follow_status(self, data):
        """
        Update followings list after follow action.
        :param data: List containing followed username or None.
        """
        if data[0]:
            self.user.followings.append(data[0])

    def handle_confirm_file_upload(self, data):
        """
        Confirm file upload result from video communication.
        :param data: List containing upload status.
        """
        print(data[0])
