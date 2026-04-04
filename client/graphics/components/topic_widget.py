import wx
import clientProtocol
import settings


class TopicWidget(wx.Panel):
    BG_COLOR = wx.BLUE # todo return to white
    # BG_COLOR = wx.WHITE
    ACTIVE_BG_COLOR = settings.BRIGHT_BLUE
    BORDER_COLOR = settings.BORDER_COLOR
    HOVER_BORDER_COLOR = settings.BRIGHT_PINK # maybe change to theme color but brighter
    ACTIVE_BORDER_COLOR = settings.THEME_COLOR

    def __init__(self, parent, topic_name):
        super().__init__(parent)

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetDoubleBuffered(True)

        self.active = False
        self.parent = parent
        self.topic_name = topic_name

        self.hovering = False

        vbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(vbox)

        vbox.Add(wx.StaticText(self, label=topic_name))

        self.Bind(wx.EVT_SIZE, self.on_resize)

        self.Bind(wx.EVT_PAINT, self.on_paint)

        self.Bind(wx.EVT_ENTER_WINDOW, self.on_hover)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_hover_stop)

        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)


    def on_left_up(self, event):
        self.active = not self.active

    def on_hover(self, event):
        self.hovering = True
        event.Skip()

    def on_hover_stop(self, event):
        self.hovering = False
        event.Skip()

    def on_resize(self, event):
        self.Refresh()
        event.Skip()

    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        gc = wx.GraphicsContext.Create(dc)

        if gc:
            w, h = self.GetClientSize()

            background_color = self.ACTIVE_BG_COLOR if self.active else self.BG_COLOR
            print(background_color)
            # Background
            gc.SetBrush(wx.Brush(background_color))
            gc.SetPen(wx.NullGraphicsPen)
            gc.DrawRoundedRectangle(0, 0, w, h, settings.ROUND_BORDER_RADIUS)

            # Border color (changes on focus)
            border_color = self.HOVER_BORDER_COLOR if self.hovering else self.BORDER_COLOR

            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.SetPen(wx.Pen(border_color, 2))
            gc.DrawRoundedRectangle(1, 1, w - 2, h - 2, settings.ROUND_BORDER_RADIUS)

