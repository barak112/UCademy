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


class UserProfilePanel(wx.ScrolledWindow):
    BG_COLOR = (232, 239, 255)
    COLUMN_WIDTH = 200

    RATIO = 4 / 3

    def __init__(self, frame, parent):
        super().__init__(parent)

        self.frame = frame
        self.parent = parent
        self.SetScrollRate(0, 7)

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

        self.videos_grid = wx.GridSizer(self.grid_rows, self.grid_columns, 5, 5)

        videos_sizer = wx.BoxSizer(wx.VERTICAL)
        videos_sizer.Add(videos_label_and_add_video_btn_sizer, 0, wx.BOTTOM, 10)
        videos_sizer.Add(self.videos_grid, 0)


        # add to padding_sizer
        padding_sizer.Add(self.profile_info, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 20)
        padding_sizer.Add(videos_sizer, 1, wx.ALIGN_CENTER_HORIZONTAL)


        # add to main_sizer
        main_sizer.AddStretchSpacer()
        main_sizer.Add(padding_sizer, 0, wx.EXPAND)
        main_sizer.AddStretchSpacer()


        self.Bind(wx.EVT_SIZE, self.on_resize)
        self.add_video_btn.Bind(wx.EVT_LEFT_UP, self.on_move_to_upload_video)

        self.Layout()
        self.FitInside()  # calculates virtual size

        pub.subscribe(self.user_info_ans, "user_details_in_profile_ans")
        pub.subscribe(self.video_details_ans, "video_details_in_profile_ans")

        self.Hide()
        #todo when clicking pfp, opens explorer to choose new photo.
        # when hovering the pfp shows a tooltip with the option to click the image to change it

    def on_move_to_upload_video(self, event):
        self.frame.switch_panel(self.frame.upload_video_panel, self)
        event.Skip()

    def scale_thumbnail(self, thumbnail_image):
        w, h = thumbnail_image.GetSize()
        print("thumbnail size:", w, h)
        column_height = self.COLUMN_WIDTH * self.RATIO


        scale_w = self.COLUMN_WIDTH/w
        scale_h = column_height/h
        # if w>self.COLUMN_WIDTH and h >column_height:
        scale = max(scale_h, scale_w)

        new_w = int(w * scale)
        new_h = int(h * scale)
        print("new thumbnail size:", new_w, new_h)
        return thumbnail_image.Scale(new_w, new_h, wx.IMAGE_QUALITY_HIGH)

    def video_details_ans(self, video):
        print("got new video in profile:", video)
        self.frame.videos_details[video.video_id] = video
        thumbnail_path = f"media\\{video.video_id}.png"
        if not os.path.isfile(thumbnail_path):
            thumbnail_path = "assets\\no_thumbnail.png"

        thumbnail = wx.Image(thumbnail_path)
        thumbnail = self.scale_thumbnail(thumbnail)
        thumbnail = wx.Bitmap(thumbnail)

        thumbnail = wx.StaticBitmap(self, bitmap=thumbnail, size=(self.COLUMN_WIDTH, int(self.COLUMN_WIDTH * self.RATIO))) # cutting the image 9X16
        self.videos_grid.Add(thumbnail)
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
        self.current_user = username
        self.req_user_info(username)

        self.Layout()
        self.Refresh()

    def Show(self, show=True):
        super().Show()
        self.set_user("Barak")

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
