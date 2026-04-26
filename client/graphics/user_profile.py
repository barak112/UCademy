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

    def __init__(self, frame, parent):
        super().__init__(parent)

        self.frame = frame
        self.parent = parent
        self.SetScrollRate(0, 7)

        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(main_sizer)
        self.SetBackgroundColour(self.BG_COLOR)

        self.current_user = None
        self.video_ids = []

        #padded vertical sizer
        padding_sizer = wx.BoxSizer(wx.VERTICAL)

        # profile info
        profile_info = profile_widget.ProfileWidget(self.frame, self)
        # profile_info.SetMinSize((400, 100))
        # profile_info.SetBackgroundColour(wx.BLACK)

        # videos grid
        videos_label = wx.StaticText(self, label="Videos")
        videos_label.SetFont(videos_label.GetFont().Scale(1.2).Bold())

        self.grid_columns = 4
        # self.grid_rows = math.ceil(len(settings.TOPICS) / self.grid_columns)
        self.grid_rows = 100

        videos_grid = wx.GridSizer(self.grid_rows, self.grid_columns, 5, 5)

        for videos_grid_row in range(self.grid_rows):
            for videos_grid_col in range(self.grid_columns):
                videos_grid.Add(wx.StaticText(self, label="video"), 1, wx.EXPAND | wx.ALL, 5)

        videos_sizer = wx.BoxSizer(wx.VERTICAL)
        videos_sizer.Add(videos_label)
        videos_sizer.Add(videos_grid, 1, wx.EXPAND)



        # add to padding_sizer
        padding_sizer.Add(profile_info, 0, wx.ALIGN_CENTER_HORIZONTAL)
        padding_sizer.Add(videos_sizer, 1, wx.ALIGN_CENTER_HORIZONTAL)


        # add to main_sizer
        main_sizer.AddStretchSpacer()
        main_sizer.Add(padding_sizer, 0, wx.EXPAND)
        main_sizer.AddStretchSpacer()


        self.Bind(wx.EVT_SIZE, self.on_resize)

        self.Layout()
        self.FitInside()  # calculates virtual size

        self.Hide()

    # def update_pfp(self):
    #     user = self.frame.user
    #     if user:
    #         pfp_path = f"media\\{user.username}.png"
    #         if os.path.isfile(pfp_path):
    #             pfp = wx.Bitmap(wx.Image(pfp_path).Scale(settings.PFP_SIZE, settings.PFP_SIZE))
    #             self.personal_account_btn.SetBitmap(pfp)
    #     print("updated pfp")

    def set_user(self, username):
        self.current_user = username

    def Show(self, show=True):
        super().Show()
        # self.update_pfp()

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
