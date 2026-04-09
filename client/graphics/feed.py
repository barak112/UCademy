import math

import wx
import wx.media
import clientProtocol
import settings


class Feed(wx.Panel):
    BG_COLOR = (232, 239, 255)
    def __init__(self, frame, parent):
        super().__init__(parent)

        self.frame = frame
        self.parent = parent

        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.SetBackgroundColour(self.BG_COLOR)

        # video
        video_sizer = wx.BoxSizer(wx.VERTICAL)

        self.video = wx.media.MediaCtrl(self, style=wx.SIMPLE_BORDER)
        self.video.Load("media\\2.mp4")  # local video file
        self.video.Play()
        # video_size = (int(self.GetClientSize()[0]), int(self.GetClientSize()[0] * (9 / 16)))
        # video_size = (int(self.GetClientSize()[1] * (9 / 16)), self.GetClientSize()[1])
        # self.video.SetInitialSize(video_size)
        self.video.SetInitialSize((90, 160))
        # self.video.SetMinSize(video_size)

        video_sizer.Add(self.video, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # comments
        comments_sizer = wx.BoxSizer(wx.VERTICAL)


        # main_sizer.Add(comments_sizer, 1, wx.EXPAND)
        # main_sizer.Add(video_sizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.Left | wx.Right, 20)
        main_sizer.Add(video_sizer, 0, wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(main_sizer)

        self.Hide()
