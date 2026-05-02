import wx
from pubsub import pub
import clientProtocol
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

        # video_details only contains videos with a video file
        self.videos_details = {}  # [video_id] = video_object

        self.users = {}  # [username] = user_object

        self.video_requests_by_feeds = []  # [feed_panel]
        self.comments_requests_by_feeds = []  # [feed_panel]
        self.comment_requests_by_feeds = []  # [feed_panel]
        self.like_requests_by_feeds = []  # [feed_panel]

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

        # self.login_panel.Show()
        # self.signup_panel.Show()
        # self.email_verification_panel.Show()
        # self.pick_topics_panel.Show()

        msg = clientProtocol.build_sign_in("barakbm9@gmail.com", "password")
        self.comm.send_msg(msg)
        # # time.sleep(1)
        # self.feed_panel.Show()

        # time.sleep(5)
        # msg = clientProtocol.build_req_video()
        # demo_video = video.Video(4, "", "", "", "", 5, 10, False)
        # self.feed_panel.load_video(demo_video)
        # self.comm.send_msg(msg)

        pub.subscribe(self.load_new_video, "load_new_video")

        pub.subscribe(self.load_new_comments, "load_new_comments")

        pub.subscribe(self.on_like_video_ans, "video_like_ans")

        pub.subscribe(self.on_add_comment_ans, "added_comment")

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

    def on_like_video_ans(self, status, video_id):
        """
        Routes a like response from the server to the feed panel that sent the like request.
        :param status: The success or failure status of the like action.
        :param video_id: The ID of the video that was liked.
        """
        correct_feed_panel = self.like_requests_by_feeds.pop(0)
        correct_feed_panel.on_like_video_ans(status, video_id)

    def on_add_comment_ans(self, video_id, comment):
        """
        Routes an add-comment response from the server to the feed panel that sent the request.
        :param video_id: The ID of the video the comment was added to.
        :param comment: The comment object returned by the server.
        """
        correct_feed_panel = self.comment_requests_by_feeds.pop(0)
        correct_feed_panel.on_add_comment_ans(video_id, comment)

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


# ----------------------------
# App Entry Point
# ----------------------------
if __name__ == "__main__":
    app = wx.App()
    frame = MainFrame(None)
    frame.Show()
    app.MainLoop()
