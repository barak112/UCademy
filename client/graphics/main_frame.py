import time

import wx

import clientProtocol
import video
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
        super().__init__(None, title="Ucademy", size=(1366,768))
        super().Maximize()
        # super().ShowFullScreen(True)

        icon_path = "assets\\ucademy_logo.ico"
        icon = wx.Icon(icon_path, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        self.comm = comm
        self.video_comm = None
        self.user = None

        self.videos_details = {}  # [video_id] = video_object
        self.videos_ids_with_file = [] # video ids of videos with both details and actual video

        self.users = {}  # [username] = user_object

        # todo in feed, for each req add to this list. maybe make it a queue.
        self.video_requests_by_feeds = [] # [feed_associated_panel]

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

    def switch_panel(self, new_panel, old_panel):
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
