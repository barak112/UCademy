import wx
import clientProtocol
import rounded_button
import settings
import topic_widget


class PickTopicsPanel(wx.Panel):
    def __init__(self, frame, parent):
        super().__init__(parent)

        self.frame = frame
        self.parent = parent

        self.background_bitmap = wx.Bitmap("assets\\topic_pick_background.png")

        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(hbox)

        #title
        title = wx.StaticText(self, label="What are you interested in?")
        font = title.GetFont()
        font = font.Scale(4).Bold()
        title.SetFont(font)

        # subtitle
        subtitle = wx.StaticText(self, label="Choose topics to personalise your experience. Select at least 3 topics.")
        font = subtitle.GetFont()
        font = font.Scale(2)
        subtitle.SetFont(font)

        # grid
        grid = wx.GridSizer(4, 4, 5, 5)
        for topic_name in settings.TOPICS:
            topic = topic_widget.TopicWidget(self, topic_name)
            grid.Add(topic, 1, wx.EXPAND)

        # topics selected

        # continue button

        # vbox.AddStretchSpacer()
        vbox.Add(title,0, wx.ALIGN_CENTER_HORIZONTAL)
        vbox.Add(subtitle, 0, wx.ALIGN_CENTER_HORIZONTAL)
        #todo add the text to the paint so it would be transparent
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

    # def create_topic_widget(self, topic):
    #     # image_icon = wx.Bitmap(f"assets\\topics\\{topic}.png")
    #     pass

    def on_resize(self, event):
        self.Refresh()
        event.Skip()

    def on_paint(self, event):
        dc = wx.BufferedPaintDC(self)
        dc.DrawBitmap(self.background_bitmap, 0, 0)

    def on_key(self, event):
        """checks for keys pressed, exists on Escape, log in on Enter"""
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:
            exit()
        elif keycode == wx.WXK_RETURN:
            self.on_login(None)

        event.Skip()
