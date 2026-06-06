import wx
from pubsub import pub
import clientProtocol
import settings
from email_verification import EmailVerificationPanel
from feed import FeedPanel
from log_in import LoginPanel
from pick_topics import PickTopicsPanel
from sign_up import SignupPanel
from upload_video import UploadVideoPanel
from user_profile import UserProfilePanel


# ----------------------------
# Main Frame (Controller)
# ----------------------------
class MainFrame(wx.Frame):

    def __init__(self, comm):
        """
        Initializes the main application frame, sets up all panels, sizers, and pubsub subscriptions.
        :param comm: The communication object used to send and receive messages with the server.
        """
        super().__init__(None, title="Ucademy", size=(1366, 768))
        super().Maximize()

        icon_path = "assets\\ucademy_logo.ico"
        icon = wx.Icon(icon_path, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        self.comm = comm
        self.video_comm = None
        self.user = None

        # video_details only contains videos with a video file, only relevant for feed panels
        self.videos_details = {}  # [video_id] = video_object

        self.users = {}  # [username] = user_object

        self.video_requests_by_feeds = []  # [feed_panel]
        self.comments_requests_by_feeds = []  # [feed_panel]

        self.status_labels = [] # list of all status labels
        self.animated_dot_labels = ["waiting for video from server", "Loading video", "Sending verification code",
                                    "Waiting for comments from server", "Loading Video From Server", "Loading Content",
                                    "Uploading", "Resending code", "sending credentials to the server",
                                    "Loading Content From Server", "waiting for videos from server",
                                    "Disconnected from server, Closing application in 5 seconds", "Creator uploaded a new video, loading it now from server",
                                    "The video you were watching has been deleted, waiting for video from the server"]


        self.dots_animation_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.status_label_dots_animation, self.dots_animation_timer)
        self.dots_animation_timer.Start(500)  # every half a minute

        self.CreateStatusBar()

        self.container = wx.Panel(self)

        self.login_panel = LoginPanel(self, self.container)
        self.signup_panel = SignupPanel(self, self.container)
        self.email_verification_panel = EmailVerificationPanel(self, self.container)
        self.pick_topics_panel = PickTopicsPanel(self, self.container)
        self.feed_panel = FeedPanel(self, self.container)
        self.pick_filter_panel = PickTopicsPanel(self, self.container, self.feed_panel)
        self.user_profile_panel = UserProfilePanel(self, self.container)
        self.user_profile_feed_panel = FeedPanel(self, self.container, self.user_profile_panel)
        self.upload_video_panel = UploadVideoPanel(self, self.container)
        self.pick_video_topics_panel = PickTopicsPanel(self, self.container, self.upload_video_panel)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.sizer.Add(self.login_panel, 1, wx.EXPAND)
        self.sizer.Add(self.signup_panel, 1, wx.EXPAND)
        self.sizer.Add(self.email_verification_panel, 1, wx.EXPAND)
        self.sizer.Add(self.pick_topics_panel, 1, wx.EXPAND)
        self.sizer.Add(self.feed_panel, 1, wx.EXPAND)
        self.sizer.Add(self.pick_filter_panel, 1, wx.EXPAND)
        self.sizer.Add(self.user_profile_panel, 1, wx.EXPAND)
        self.sizer.Add(self.upload_video_panel, 1, wx.EXPAND)
        self.sizer.Add(self.pick_video_topics_panel, 1, wx.EXPAND)
        self.sizer.Add(self.user_profile_feed_panel, 1, wx.EXPAND)

        self.container.SetSizer(self.sizer)

        # self.signup_panel.Show()
        # self.email_verification_panel.Show()
        # self.pick_topics_panel.Show()
        # self.user_profile_panel.Show()

        # self.login_panel.Show()

        import __main__

        if __main__.__file__ == "D:\\UCademy\client\clientlogic.py":
            msg = clientProtocol.build_sign_in("bbmalt9@gmail.com", "password")
            self.comm.send_msg(msg)
        else:
            msg = clientProtocol.build_sign_in("barakbm9@gmail.com", "password")
            self.comm.send_msg(msg)



        # self.upload_video_panel.Show()
        # self.feed_panel.Hide()
        # time.sleep(1)
        # self.feed_panel.Show()

        # time.sleep(5)
        # msg = clientProtocol.build_req_video()
        # demo_video = video.Video(4, "", "", "", "", 5, 10, False)
        # self.feed_panel.load_video(demo_video)
        # self.comm.send_msg(msg)

        pub.subscribe(self.on_a_user_deleted_comment, "comment_deleted_ans")

        pub.subscribe(self.on_a_user_deleted_video, "video_deleted_ans")

        pub.subscribe(self.load_new_video, "load_new_video")

        pub.subscribe(self.load_new_comments, "load_new_comments")

        pub.subscribe(self.on_like_video_ans, "video_like_ans")

        pub.subscribe(self.on_a_user_added_comment, "added_comment")

        pub.subscribe(self.comm_disconnected, "comm_disconnected")

        pub.subscribe(self.on_a_user_upload_video, "video_upload_ans")

        pub.subscribe(self.on_report_ans, "report_ans")

    def on_report_ans(self, status, id, type, content, content_publisher, created_at):
        msg2 = f"has been examined and it has been decided that the"

        msg1 = f'report of video "{content}" by "{content_publisher}"'

        type_str = "video" if type == settings.VIDEO_DIGIT_REPR else "comment"

        if type == settings.COMMENT_DIGIT_REPR and content and content_publisher:
            comment, video_name = content
            commenter, video_creator = content_publisher
            msg1 = f'report of comment "{comment}" by "{commenter}" on video "{video_name}" by "{video_creator}"'

        # Determine the message based on status
        status_messages = {
            settings.REPORT_DENIED: f"{msg1} you issued on {created_at} {msg2} {type_str} will not be removed",
            settings.REPORT_ACCEPTED: f"{msg1} you issued on {created_at} {msg2} {type_str} will be removed",
            settings.REPORT_CONTENT_DOESNT_EXISTS: f"{type_str} reported does not exist!",
            settings.REPORT_ALREADY_ISSUED: f"{msg1} has already been issued by you!",
            settings.REPORT_RECEIVED: f"{msg1} has been received at the server and will be examined",
            settings.REPORT_CONCLUDED: f"{msg1} has already been concluded"
        }

        wx.MessageBox(
            status_messages[status],
            f"{type_str.capitalize()} Report Status",
            wx.OK | wx.ICON_INFORMATION
        )

        self.Layout()

    def on_a_user_deleted_comment(self, video_id, comment_id):
        if video_id in self.videos_details:  # if the client has the video's file (if it has appeared in the feed)
            self.videos_details[video_id].delete_comment(comment_id)  # delete comment from video details
            self.user_profile_feed_panel.on_a_user_deleted_comment(video_id, comment_id)  # visually delete comment in the user panel feed
            self.feed_panel.on_a_user_deleted_comment(video_id, comment_id) # visually delete comment in the feed

        # update comments amount in the user profile panel
        self.user_profile_panel.on_a_user_deleted_comment(video_id)


    def on_a_user_deleted_video(self, video_id):

        if video_id in self.videos_details:  # if the client has the video's file (if it has appeared in the feed)
            del self.videos_details[video_id]  # delete video from video details
            self.user_profile_feed_panel.on_a_user_deleted_video(video_id)
            self.feed_panel.on_a_user_deleted_video(video_id)

        # remove the video from the user profile panel
        self.user_profile_panel.on_a_user_deleted_video(video_id)

        if video_id in self.user.videos_ids:
            self.user.videos_ids.remove(video_id)


    def load_new_video(self, video):
        """
        Routes an incoming video to the feed panel that originally requested it.
        :param video: The video object to load into the appropriate feed panel.
        """
        correct_feed_panel = self.video_requests_by_feeds.pop(0)
        correct_feed_panel.load_new_video(video)

    def load_new_comments(self, video_id, comments):
        """
        Routes an incoming list of comments to the feed panel that originally requested them.
        :param video_id: The ID of the video whose comments are being loaded.
        :param comments: The list of comment objects to load.
        """
        correct_feed_panel = self.comments_requests_by_feeds.pop(0)
        correct_feed_panel.load_new_comments(video_id, comments)

    def on_like_video_ans(self, status, video_id, username):
        """
        Routes a like response from the server to the feed panel that sent the like request.
        :param status: The success or failure status of the like action.
        :param video_id: The ID of the video that was liked.
        :param username: The username of the user that has liked or unliked the video
        """

        if video_id in self.videos_details:  # if the client has the video's file (if it has appeared in the feed)
            self.videos_details[video_id].amount_of_likes += 1 if status else -1  # either adds or removes a like from the video
            self.user_profile_feed_panel.on_a_user_liked_video(status, video_id, username)
            self.feed_panel.on_a_user_liked_video(status, video_id, username)

        # update the video's comments amount in the user profile panel
        self.user_profile_panel.on_a_user_liked_video(status, video_id)
    def on_a_user_added_comment(self, video_id, comment):
        """
        Routes an add-comment response from the server to the feed panel that sent the request.
        :param video_id: The ID of the video the comment was added to.
        :param comment: The comment object returned by the server.
        """
        index = 0
        if not comment.commenter == self.user.username: # if the comment is not from the current user, add it after the last comment by the user
            index = self.get_last_comment_index_by_user(self.videos_details[video_id], self.user.username) + 1

        if video_id in self.videos_details: # if the client has the video's file (if it has appeared in the feed)
            self.videos_details[video_id].add_comment_at_index(comment, index)
            self.user_profile_feed_panel.on_a_user_added_comment(video_id, comment, index)
            self.feed_panel.on_a_user_added_comment(video_id, comment, index)

        # update the video's comments amount in the user profile panel
        self.user_profile_panel.on_a_user_added_comment(video_id)

    @staticmethod
    def get_last_comment_index_by_user(video, username):
        comments = video.get_comments()
        commenter_names = [c.commenter for c in comments]
        if username in commenter_names:
            index = len(commenter_names) - 1 - commenter_names[::-1].index(username)
        else:
            index = -1
        print("index:", index, "commenter_names:", commenter_names)
        return index

    def on_a_user_upload_video(self, video_id, username):
        if username in self.users:
            self.users[username].videos_ids.insert(0, video_id)

        if username == self.user.username:
            self.upload_video_panel.on_video_upload_ans(video_id)
            self.user.videos_ids.insert(0, video_id)

        self.user_profile_panel.on_a_user_upload_video(username, video_id)


    def switch_panel(self, new_panel, old_panel):
        """
        Hides the current panel and shows the new one, then refreshes the layout.
        :param new_panel: The panel to switch to and display.
        :param old_panel: The panel to hide.
        """
        old_panel.Hide()
        new_panel.Show()
        new_panel.SetFocus()
        self.Layout()
        self.Refresh()
        self.sizer.Layout()
        new_panel.Refresh()

    def change_text_status(self, text):
        """Event handler to update the status bar text."""
        self.SetStatusText(text, 0)

    def comm_disconnected(self):
        wx.MessageBox(
            "Disconnected from server, Closing application in 5 seconds.",
            "Closing app in 5 seconds.",
            wx.OK | wx.ICON_INFORMATION
        )

        self.change_text_status("Disconnected from server, Closing application in 5 seconds.")

        for status_label in self.status_labels:
            status_label.SetLabel("Disconnected from server, Closing application in 5 seconds.")

        self.Layout()
        wx.CallLater(5000, self.Close)

    def status_label_dots_animation(self, event):
        for status_label in self.status_labels:
            if status_label.GetLabel().strip(".") in self.animated_dot_labels:
                if status_label.GetLabel()[-3:] == "...":
                    status_label.SetLabel(status_label.GetLabel()[:-3])
                else:
                    status_label.SetLabel(status_label.GetLabel() + ".")

# ----------------------------
# App Entry Point
# ----------------------------
if __name__ == "__main__":
    app = wx.App()
    frame = MainFrame(None)
    frame.Show()
    app.MainLoop()
