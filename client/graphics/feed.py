import math

import pubsub.pub
import wx
import wx.media
from pubsub import pub
from wx.core import EVT_SIZE

import clientProtocol
import settings
import comments


class Feed(wx.Panel):
    BG_COLOR = (232, 239, 255)

    def __init__(self, frame, parent):
        super().__init__(parent)

        self.frame = frame
        self.parent = parent
        self.is_playing = False
        self.is_muted = False

        self.current_video_id = None  # video_id

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.SetBackgroundColour(self.BG_COLOR)

        # video
        video_sizer = wx.BoxSizer(wx.VERTICAL)

        self.video_ctrl = wx.media.MediaCtrl(self, style=wx.SIMPLE_BORDER, szBackend=wx.media.MEDIABACKEND_WMP10)
        self.video_ctrl.Bind(wx.media.EVT_MEDIA_LOADED, self.on_play)
        self.video_ctrl.SetVolume(0)

        # self.video.Play()
        # video_size = (int(self.GetClientSize()[0]), int(self.GetClientSize()[0] * (9 / 16)))
        # video_size = (int(self.GetClientSize()[1] * (9 / 16)), self.GetClientSize()[1])
        # self.video.SetInitialSize(video_size)
        # self.video.SetInitialSize((90, 160))
        # self.video.SetMinSize(video_size)

        # video
        video_sizer.Add(self.video_ctrl, 1, wx.EXPAND)

        # actions
        actions_sizer = wx.BoxSizer(wx.VERTICAL)
        # video_sizer.Add(actions_sizer, 0, wx.ALIGN_CENTER_VERTICAL)

        # comments
        # comments_sizer = wx.BoxSizer(wx.VERTICAL)
        comments_panel = comments.Comments(frame, self)
        comments_panel.SetMinSize((400, 0))

        padding_sizer = wx.BoxSizer(wx.HORIZONTAL)

        padding_sizer.AddStretchSpacer()
        padding_sizer.AddSpacer(10)
        padding_sizer.Add(comments_panel, 10, wx.EXPAND | wx.RIGHT, 50) # top, right, bottom, left borders

        padding_sizer.Add(video_sizer, 10, wx.EXPAND)
        padding_sizer.AddSpacer(10)
        padding_sizer.AddStretchSpacer()

        main_sizer.AddSpacer(50)
        main_sizer.Add(padding_sizer, 1 , wx.EXPAND)
        main_sizer.AddSpacer(50)

        # btn = wx.Button(self, label="Play/Pause")
        # main_sizer.Add(btn, 0, wx.ALIGN_CENTER_VERTICAL)
        # btn.Bind(wx.EVT_BUTTON, self.on_play)
        self.SetSizer(main_sizer)

        pub.subscribe(self.load_video, "load_video")
        self.Bind(wx.EVT_MOUSEWHEEL, self.on_scroll)
        self.Hide()

    def on_scroll(self, event):
        rotation = event.GetWheelRotation()

        if rotation > 0:
            # return to last video
            if self.frame.video_index > 0:
                self.frame.video_index -=1
                self.load_video(self.frame.videos_ids_with_file[self.frame.video_index])
        else:
            msg = clientProtocol.build_req_video()
            self.frame.comm.send_msg(msg)
            print("req")
        #todo add a timer so it would scroll so much from a single scroll
        event.Skip()

    def on_play(self, event):
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.video_ctrl.Play()
        else:
            self.video_ctrl.Pause()

    def mute(self, event):
        self.is_muted = not self.is_muted
        if self.is_muted:
            self.video_ctrl.SetVolume(0)
        else:
            self.video_ctrl.SetVolume(1)

    def load_video(self, video):
        video_id = video.video_id
        if video_id:
            self.current_video_id = video_id

            if video_id not in self.frame.videos_details.keys():
                self.frame.videos_details[video_id] = video

            if video_id not in self.frame.videos_ids_with_file:
                self.frame.videos_ids_with_file.append(video_id)

            self.frame.video_index +=1

            self.video_ctrl.Load(f"media\\{video_id}.mp4")
            self.video_ctrl.SetInitialSize((500, 500))
            print("video arrived:", video)
            self.Layout()
        else:
            self.frame.change_text_status("watched all videos")
            print("watched all videos")

# three parts: comments, video, video desc + video name.


if __name__ == "__main__":
    app = wx.App()
    frame = wx.Frame(None)
    frame.SetSize((800, 600))
    panel = Feed(frame, frame)
    frame.Show()
    app.MainLoop()
