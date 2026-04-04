import wx
import clientProtocol
import settings
import topic_widget


class PickTopicsPanel(wx.Panel):
    def __init__(self, frame, parent):
        super().__init__(parent)

        self.frame = frame
        self.parent = parent

        self.background_bitmap = wx.Bitmap("assets\\topic_pick_background.png")

        vbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(vbox)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        grid = wx.GridSizer(4,4,5,5)

        hbox.AddStretchSpacer()
        hbox.Add(grid, 1, wx.EXPAND)
        hbox.AddStretchSpacer()

        vbox.AddStretchSpacer()
        vbox.Add(hbox, 1, wx.EXPAND)
        vbox.AddStretchSpacer()

        for topic_name in settings.TOPICS:
            # topics_widget = create_topic_widget(topics)
            topic = topic_widget.TopicWidget(self,topic_name)
            # topic = wx.StaticText(self, label=topic_name)
            grid.Add(topic, 1, wx.EXPAND)
            #todo remove expand and set min side to topic widget

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
