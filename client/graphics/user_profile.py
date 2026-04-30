import math
import os.path

import wx
import wx.media
from pubsub import pub

import clientProtocol
import profile_widget
import rounded_button
import settings
import comments
import video_widget


class UserProfilePanel(wx.ScrolledWindow):
    BG_COLOR = (232, 239, 255)
    COLUMN_WIDTH = 280

    RATIO = 4 / 3

    def __init__(self, frame, parent):
        super().__init__(parent)

        self.frame = frame
        self.parent = parent
        self.SetScrollRate(0, 12)

        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(main_sizer)
        self.SetBackgroundColour(self.BG_COLOR)

        self.current_user = None  # current user object
        self.video_ids = []

        #padded vertical sizer
        padding_sizer = wx.BoxSizer(wx.VERTICAL)

        # profile info
        self.profile_info = profile_widget.ProfileWidget(self.frame, self)
        # profile_info.SetMinSize((400, 100))
        # profile_info.SetBackgroundColour(wx.BLACK)

        # videos grid
        videos_label_and_add_video_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        videos_label = wx.StaticText(self, label="Videos")
        videos_label.SetFont(videos_label.GetFont().Scale(1.3).Bold())

        self.add_video_btn = rounded_button.RoundedButton(self, "assets\\add_video.png", (180, 200, 255), self.BG_COLOR, circle=True, use_image=True)
        self.add_video_btn.SetMinSize((25, 25))

        # add to videos_label_and_add_video_btn_sizer
        videos_label_and_add_video_btn_sizer.Add(videos_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        videos_label_and_add_video_btn_sizer.Add(self.add_video_btn, 0, wx.ALIGN_CENTER_VERTICAL)

        self.grid_columns = 4
        self.grid_rows = 1

        self.videos_grid = wx.GridSizer(self.grid_rows, self.grid_columns, 20, 20)

        videos_sizer = wx.BoxSizer(wx.VERTICAL)
        videos_sizer.Add(videos_label_and_add_video_btn_sizer, 0, wx.BOTTOM, 10)
        videos_sizer.Add(self.videos_grid, 0)


        # add to padding_sizer
        padding_sizer.Add(self.profile_info, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 20)
        padding_sizer.Add(videos_sizer, 1, wx.ALIGN_CENTER_HORIZONTAL)


        # back arrow
        back_arrow = rounded_button.RoundedButton(self, "assets\\back_arrow.png", wx.WHITE, self.BG_COLOR, circle=True, use_image=True, text_color=wx.WHITE)
        back_arrow.SetMinSize((50, 50))

        # add to main_sizer
        main_sizer.Add(back_arrow, 0, wx.ALL, 20)
        main_sizer.AddStretchSpacer()
        main_sizer.Add(padding_sizer, 0, wx.EXPAND)
        main_sizer.AddStretchSpacer()


        self.Bind(wx.EVT_SIZE, self.on_resize)
        self.add_video_btn.Bind(wx.EVT_LEFT_UP, self.on_move_to_upload_video)
        back_arrow.Bind(wx.EVT_LEFT_DOWN, self.on_back_arrow)

        self.FitInside()  # calculates virtual size
        pub.subscribe(self.user_info_ans, "user_details_in_profile_ans")
        pub.subscribe(self.video_details_ans, "video_details_in_profile_ans")

        self.Hide()
        #todo when clicking pfp, opens explorer to choose new photo.
        # when hovering the pfp shows a tooltip with the option to click the image to change it
        # also be able to change topics

    def video_selected(self, video):
        # req video
        self.frame.user_profile_feed_panel.waiting_for_video = True
        msg = clientProtocol.build_req_video(video.video_id)
        self.frame.comm.send_msg(msg)

        # set video ids to scroll through in user_profile_feed_panel
        self.frame.user_profile_feed_panel.videos_ids = self.video_ids
        # switch to feed associated with user profile
        self.frame.switch_panel(self.frame.user_profile_feed_panel, self)
        # todo make sure so when scrolling through the videos, when finishing them, either req more or stop scrolling
        # do that you get all of the user's videos ids when getting its info

    def on_back_arrow(self, event):
        self.frame.switch_panel(self.frame.feed_panel, self)
        event.Skip()

    def on_move_to_upload_video(self, event):
        self.frame.switch_panel(self.frame.upload_video_panel, self)
        event.Skip()

    def video_details_ans(self, video):
        print("got new video in profile:", video)
        self.frame.videos_details[video.video_id] = video
        self.video_ids.append(video.video_id)
        #todo make sure the videos are sorted by date, the new ones sent first

        thumbnail = video_widget.VideoWidget(self, video, self.COLUMN_WIDTH, self.RATIO)
        self.videos_grid.Add(thumbnail, 0, wx.EXPAND)

        self.FitInside()
        self.Layout()
        self.Refresh()

    def user_info_ans(self, user):
        self.frame.users[user.username] = user
        self.current_user = user
        self.profile_info.set_user(user)
        self.grid_rows = math.ceil(user.video_amount / self.grid_columns)
        print("grid rows:", self.grid_rows)
        self.videos_grid.SetRows(self.grid_rows)
        print("user ans:",user)

    def req_user_info(self, username):
        msg = clientProtocol.build_req_user_info(username)
        self.frame.comm.send_msg(msg)
        msg = clientProtocol.build_req_creator_videos(username)
        self.frame.comm.send_msg(msg)

    def set_user(self, username):
        self.videos_grid.Clear(True)
        self.current_user = username
        self.req_user_info(username)

        self.Layout()
        self.Refresh()

    def Show(self, show=True):
        super().Show()

    def on_resize(self, event):
        self.Layout()
        self.Refresh()
        event.Skip()


if __name__ == "__main__":
    app = wx.App()
    frame = wx.Frame(None)
    frame.SetSize((800, 600))
    panel = UserProfilePanel(frame, frame)
    frame.Show()
    app.MainLoop()
