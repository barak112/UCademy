import wx


class ScrollablePanel(wx.ScrolledWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.background_bitmap = wx.Bitmap(
            "C:\\Users\\barak\\PycharmProjects\\UCademy\\UCademy\\client\\assets\\topic_pick_background.png")
        self.SetScrollRate(20, 20)
        # self.panel.SetVirtualSize((1200, 5000))
        self.Bind(wx.EVT_PAINT, self.on_paint)

        sizer = wx.BoxSizer(wx.VERTICAL)
        for i in range(1000):
            sizer.Add(wx.StaticText(self, label=f"Text {i}"))
        self.SetSizer(sizer)

        self.SetSizer(sizer)

    def on_paint(self, event):
        dc = wx.BufferedPaintDC(self)
        dc.Clear()
        width, height = self.GetClientSize()

        # --- Draw fixed background first ---
        img = self.background_bitmap.ConvertToImage()
        scaled_img = img.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
        dc.DrawBitmap(wx.Bitmap(scaled_img), 0, 0, True)



class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Fixed Background Scrollable Panel", size=(800, 600))
        ScrollablePanel(self)


app = wx.App(False)
frame = MyFrame()
frame.Show()
app.MainLoop()
