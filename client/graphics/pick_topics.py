import wx
import clientProtocol
import rounded_button
import settings
import topic_widget


class PickTopicsPanel(wx.Panel):
    TITLE = "What are you interested in?"
    SUBTITLE = "Choose topics to personalise your experience. Select at least 3 topics."
    def __init__(self, frame, parent):
        super().__init__(parent)

        self.frame = frame
        self.parent = parent

        self.background_bitmap = wx.Bitmap("assets\\topic_pick_background.png")
        self.grid_start_pos = 0

        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(hbox)

        #title
        # title = wx.StaticText(self, label="What are you interested in?")
        # font = title.GetFont()
        # font = font.Scale(4).Bold()
        # title.SetFont(font)
        # self.title = title
        # title.Hide()


        # subtitle
        # subtitle = wx.StaticText(self, label="Choose topics to personalise your experience. Select at least 3 topics.")
        # font = subtitle.GetFont()
        # font = font.Scale(2)
        # subtitle.SetFont(font)

        # grid
        grid = wx.GridSizer(4, 4, 5, 5)
        self.grid = grid
        for topic_name in settings.TOPICS:
            topic = topic_widget.TopicWidget(self, topic_name)
            grid.Add(topic, 1, wx.EXPAND)

        # topics selected

        # continue button

        # vbox.AddStretchSpacer()
        # vbox.Add(title,0, wx.ALIGN_CENTER_HORIZONTAL)
        self.spacer = vbox.Add((0, 100))
        # vbox.Add(subtitle, 0, wx.ALIGN_CENTER_HORIZONTAL)
        # vbox.AddStretchSpacer()
        vbox.Add(grid, 1, wx.EXPAND)
        # vbox.AddStretchSpacer()

        hbox.AddStretchSpacer()
        hbox.Add(vbox, 1, wx.EXPAND)
        hbox.AddStretchSpacer()


        # handles key press
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)
        # handle background disappearance
        self.Bind(wx.EVT_SIZE, self.on_resize)

        self.Bind(wx.EVT_PAINT, self.on_paint)

        self.Hide()

    def on_resize(self, event):
        self.Refresh()
        event.Skip()

    def on_paint(self, event):
        dc = wx.BufferedPaintDC(self)
        dc.DrawBitmap(self.background_bitmap, 0, 0)

        gc = wx.GraphicsContext.Create(dc)
        if gc:
            w, h = self.GetClientSize()
            # draw title
            gc.SetFont(
                wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD),
                wx.BLACK)
            tw, th = gc.GetTextExtent(self.TITLE)
            gc.DrawText(self.TITLE, (w - tw) / 2, 10)

            #draw subtitle
            gc.SetFont(
                wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD),wx.BLACK
            )

            tw2, th2 = gc.GetTextExtent(self.SUBTITLE)
            gc.DrawText(self.SUBTITLE, (w - tw2) / 2, th+20)
            if not self.grid_start_pos:
                self.spacer.SetMinSize((100, int(th+th2+60)))
                # self.spacer.SetMinSize((100, 200))
                self.Layout()
                self.grid_start_pos = th2+th+30
                # self.Layout()
                pass
    def on_key(self, event):
        """checks for keys pressed, exists on Escape, log in on Enter"""
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:
            exit()
        elif keycode == wx.WXK_RETURN:
            self.on_login(None)

        event.Skip()
