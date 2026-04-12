import time

import wx
import wx.media
import os


class VideoPlayerFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="wxPython Video Player", size=(800, 600))

        self.panel = wx.Panel(self)

        # 1. Initialize the MediaCtrl
        try:
            self.media_ctrl = wx.media.MediaCtrl(self.panel, style=wx.SIMPLE_BORDER,
                                                 szBackend=wx.media.MEDIABACKEND_WMP10  # important on Windows
                                                 )
        except NotImplementedError:
            wx.MessageBox("Media backend not found on this system.", "Error")
            self.Destroy()
            return

        self.is_muted = False

        # 2. Create UI Controls
        self.btn_load = wx.Button(self.panel, label="Load Video")
        self.btn_play = wx.Button(self.panel, label="Play")
        self.btn_pause = wx.Button(self.panel, label="Pause")

        # 3. Bind events to functions
        self.btn_load.Bind(wx.EVT_BUTTON, self.on_load)
        self.btn_play.Bind(wx.EVT_BUTTON, self.on_play)
        self.btn_pause.Bind(wx.EVT_BUTTON, self.on_pause)

        # self.Bind(wx.media.EVT_MEDIA_LOADED, self.on_media_loaded, self.media_ctrl)
        self.media_ctrl.Bind(wx.media.EVT_MEDIA_LOADED, self.on_media_loaded)
        self.media_ctrl.Load("C:\\Users\\barak\\PycharmProjects\\UCademy\\UCademy\\client\\media\\3.mp4")

        # 4. Set up the Layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        # Add the media control to take up most of the screen
        main_sizer.Add(self.media_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        # Add the buttons in a horizontal row at the bottom
        control_sizer = wx.BoxSizer(wx.HORIZONTAL)
        control_sizer.Add(self.btn_load, flag=wx.ALL, border=5)
        control_sizer.Add(self.btn_play, flag=wx.ALL, border=5)
        control_sizer.Add(self.btn_pause, flag=wx.ALL, border=5)

        main_sizer.Add(control_sizer, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=5)
        self.panel.SetSizer(main_sizer)

    def on_load(self, event):
        # Open a file dialog to select a video
        wildcard = "Video Files (*.mp4;*.avi;*.mkv)|*.mp4;*.avi;*.mkv|All Files (*.*)|*.*"
        with wx.FileDialog(self, "Choose a video file", wildcard=wildcard,
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as file_dialog:

            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return  # The user changed their mind

            path = file_dialog.GetPath()

            # Load the media. Note: This doesn't start playing it yet.
            if not self.media_ctrl.Load(path):
                wx.MessageBox("Unable to load the video. Unsupported format?", "Error")
            # else:
            #     wx.CallLater(800, self.on_media_loaded)

    def on_media_loaded(self, event):
        # This ensures the first frame stays on screen
        print("media loaded")
        self.media_ctrl.Play()
        # self.media_ctrl.Pause()
        # Optional: Seek to 0 to be safe
        # self.media_ctrl.Seek(0)

    def on_play(self, event):
        self.media_ctrl.Play()

    def on_pause(self, event):
        self.media_ctrl.Pause()

    def mute(self, event):
        self.is_muted = not self.is_muted
        if self.is_muted:
            self.media_ctrl.SetVolume(0)
        else:
            self.media_ctrl.SetVolume(1)
if __name__ == "__main__":
    app = wx.App()
    frame = VideoPlayerFrame()
    frame.Show()
    app.MainLoop()
