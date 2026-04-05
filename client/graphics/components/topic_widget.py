import os
import wx.svg
import wx

import clientProtocol
import settings


class TopicWidget(wx.Panel):
    # BG_COLOR = wx.BLUE # todo return to white
    BG_COLOR = wx.WHITE
    ACTIVE_BG_COLOR = settings.BRIGHT_BLUE
    BORDER_COLOR = settings.BRIGHT_BORDER_COLOR
    HOVER_BORDER_COLOR = settings.BRIGHT_PINK # maybe change to theme color but brighter
    ACTIVE_BORDER_COLOR = settings.THEME_COLOR
    ICON_SIZE = 48

    def __init__(self, parent, topic_name):
        super().__init__(parent)

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetBackgroundColour((204, 223, 252))
        self.SetMinSize((200, 100))

        self.SetDoubleBuffered(True)

        self.active = False
        self.parent = parent
        self.topic_name = topic_name

        self.hovering = False
        icon = wx.NullBitmap
        if os.path.isfile(f"assets\\topics_icons\\{topic_name}.png"):
            icon = wx.Image(f"assets\\topics_icons\\{topic_name}.png").Scale(48,48)
            icon = wx.Bitmap(icon)
            #todo get emojies from https://github.com/microsoft/fluentui-emoji/blob/main/assets using the 3d png version


        icon = wx.StaticBitmap(self, bitmap=icon)
        icon.SetBackgroundColour(self.BG_COLOR)

        topic_label = wx.StaticText(self, label=topic_name)
        topic_label.SetBackgroundColour(self.BG_COLOR)

        label_and_icon_vbox = wx.BoxSizer(wx.VERTICAL)
        label_and_icon_vbox.Add(icon, 0, wx.ALIGN_CENTER_HORIZONTAL)
        label_and_icon_vbox.Add(topic_label, 0, wx.ALIGN_CENTER_HORIZONTAL)


        vbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(vbox)

        vbox.AddStretchSpacer()
        vbox.Add(label_and_icon_vbox, 0, wx.ALIGN_CENTER_HORIZONTAL)
        vbox.AddStretchSpacer()

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
            gc.DrawRoundedRectangle(0, 0, w, h, settings.SLIGHTLY_ROUND_BORDER_RADIUS)

            # Border color (changes on focus)
            border_color = self.HOVER_BORDER_COLOR if self.hovering else self.BORDER_COLOR

            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.SetPen(wx.Pen(border_color, 2))
            gc.DrawRoundedRectangle(1, 1, w - 2, h - 2, settings.SLIGHTLY_ROUND_BORDER_RADIUS)

