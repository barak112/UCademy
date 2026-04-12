import wx
import wx.media


class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Media Load Example", size=(640, 480))
        panel = wx.Panel(self)

        self.mc = wx.media.MediaCtrl(
            panel,
            style=wx.SIMPLE_BORDER,
            szBackend=wx.media.MEDIABACKEND_WMP10  # important on Windows
        )
        self.mc.Bind(wx.media.EVT_MEDIA_LOADED, self.on_loaded)
        self.mc.Load("C:\\Users\\barak\\PycharmProjects\\UCademy\\UCademy\\client\\media\\3.mp4")

        # self.timer = wx.Timer(self)
        # self.Bind(wx.EVT_TIMER, self.check_loaded, self.timer)
        # self.timer.Start(1)  # check every 100ms


        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.mc, 1, wx.EXPAND)
        panel.SetSizer(sizer)

    # def check_loaded(self, event):
    #     if self.mc.GetState() != wx.media.MEDIASTATE_STOPPED:
    #         print("Loaded (probably)")
    #         self.timer.Stop()
    #
    #         # self.mc.SetInitialSize()
    #         self.Layout()
    #         self.mc.Play()

    def on_loaded(self, event):
        print("Video loaded!")
        # self.mc.SetInitialSize()  # adjust to video size
        self.Layout()
        self.mc.Play()  # optional: start playback here


app = wx.App(False)
frame = MyFrame()
frame.Show()
app.MainLoop()
