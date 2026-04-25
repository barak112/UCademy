import os.path

import wx
import wx.media
from pubsub import pub

import clientProtocol
import rounded_button
import settings
import comments


class ProfileWidget(wx.Panel):
    BG_COLOR = (232, 239, 255)

    def __init__(self, frame, parent):
        super().__init__(parent)

        self.frame = frame
        self.parent = parent
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(main_sizer)

        self.SetBackgroundColour(self.BG_COLOR)

        self.current_user = None

        # profile info
        profile_info_sizer = wx.BoxSizer(wx.HORIZONTAL)

        pfp = wx.Bitmap(wx.Image("assets\\null_pfp.png").Scale(settings.PFP_SIZE, settings.PFP_SIZE))
        pfp = wx.StaticBitmap(self, bitmap=pfp)

        info_sizer = wx.BoxSizer(wx.VERTICAL)

        profile_info_sizer.Add(pfp, 0, wx.ALIGN_CENTER_VERTICAL)
        profile_info_sizer.Add(info_sizer, 1, wx.EXPAND)


        # add to main sizer
        main_sizer.Add(profile_info_sizer, 0, wx.EXPAND)

        self.Bind(wx.EVT_SIZE, self.on_resize)

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
    panel = ProfileWidget(frame, frame)
    frame.Show()
    app.MainLoop()
