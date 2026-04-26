import os.path

import wx
import wx.media
from pubsub import pub

import clientProtocol
import rounded_button
import settings
import comments


class ProfileWidget(wx.Panel):
    # BG_COLOR = (232, 239, 255)
    BG_COLOR = (243, 247, 255)
    # BG_COLOR = settings.OFF_WHITE

    def __init__(self, frame, parent):
        super().__init__(parent)

        self.frame = frame
        self.parent = parent
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(main_sizer)

        self.SetBackgroundColour(self.BG_COLOR)

        self.current_user = None # current user object

        # profile info
        profile_info_sizer = wx.BoxSizer(wx.HORIZONTAL)

        pfp = wx.Bitmap(wx.Image("assets\\null_pfp_2.png").Scale(128,128, wx.IMAGE_QUALITY_HIGH))
        self.pfp = wx.StaticBitmap(self, bitmap=pfp)

        username_and_info_sizer = wx.BoxSizer(wx.VERTICAL)
        self.username_label = wx.StaticText(self)
        self.username_label.SetFont(self.username_label.GetFont().Scale(2).Bold())

        info_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # videos amount, followers amount, following amount labels

        numerics_font = wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

        # videos amount
        videos_amount_sizer = wx.BoxSizer(wx.VERTICAL)
        self.videos_numeric_amount_label = wx.StaticText(self)
        self.videos_numeric_amount_label.SetFont(numerics_font)

        self.videos_amount_label = wx.StaticText(self, label="Videos")

        videos_amount_sizer.Add(self.videos_numeric_amount_label, 0, wx.ALIGN_CENTER_HORIZONTAL)
        videos_amount_sizer.Add(self.videos_amount_label, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # followers amount
        followers_amount_sizer = wx.BoxSizer(wx.VERTICAL)
        self.followers_numeric_amount_label = wx.StaticText(self)
        self.followers_numeric_amount_label.SetFont(numerics_font)
        self.followers_amount_label = wx.StaticText(self, label="followers")

        followers_amount_sizer.Add(self.followers_numeric_amount_label, 0, wx.ALIGN_CENTER_HORIZONTAL)
        followers_amount_sizer.Add(self.followers_amount_label, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # following amount
        following_amount_sizer = wx.BoxSizer(wx.VERTICAL)
        self.following_numeric_amount_label = wx.StaticText(self)
        self.following_numeric_amount_label.SetFont(numerics_font)
        self.following_amount_label = wx.StaticText(self, label="following")

        following_amount_sizer.Add(self.following_numeric_amount_label, 0, wx.ALIGN_CENTER_HORIZONTAL)
        following_amount_sizer.Add(self.following_amount_label, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # add to info sizer
        info_sizer.Add(videos_amount_sizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 20)
        info_sizer.Add(followers_amount_sizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 20)
        info_sizer.Add(following_amount_sizer, 0, wx.ALIGN_CENTER_VERTICAL)


        # add to username_and_info sizer
        username_and_info_sizer.Add(self.username_label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 20)
        username_and_info_sizer.Add(info_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL)

        profile_info_sizer.Add(self.pfp, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 20)
        profile_info_sizer.Add(username_and_info_sizer, 0, wx.ALIGN_CENTER_VERTICAL)
        # main_sizer.AddSpacer(10)


        # add to main sizer
        main_sizer.AddSpacer(10)
        main_sizer.Add(profile_info_sizer, 0, wx.EXPAND)
        main_sizer.AddSpacer(10)

        self.Bind(wx.EVT_SIZE, self.on_resize)


    def update_pfp(self):
        if self.current_user:
            pfp_path = f"media\\{self.current_user.username}.png"
            if os.path.isfile(pfp_path):
                pfp = wx.Bitmap(wx.Image(pfp_path).Scale(128, 128))
                self.pfp.SetBitmap(pfp)
        print("updated pfp")

    def set_user(self, user):
        self.current_user = user
        self.username_label.SetLabel(user.username)
        self.videos_numeric_amount_label.SetLabel(str(user.video_amount))
        self.followers_numeric_amount_label.SetLabel(str(user.followers_amount))
        self.following_numeric_amount_label.SetLabel(str(user.followings_amount))
        self.update_pfp()

    def on_resize(self, event):
        self.Layout()
        self.Refresh()
        event.Skip()


if __name__ == "__main__":
    app = wx.App()
    frame = wx.Frame(None)
    frame.SetSize((800, 600))
    panel = ProfileWidget(frame, frame)
    frame.Show()
    app.MainLoop()
