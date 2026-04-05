import os
import wx.svg
import wx

import clientProtocol
import settings


class TopicWidget(wx.Panel):
    BG_COLOR = wx.WHITE
    SELECTED_BG_COLOR = settings.BRIGHT_BLUE
    BORDER_COLOR = settings.BRIGHT_BORDER_COLOR
    HOVER_BORDER_COLOR = settings.BRIGHT_PINK # maybe change to theme color but brighter
    SELECTED_BORDER_COLOR = settings.THEME_COLOR
    ICON_SIZE = 48

    def __init__(self, parent, topic_name):
        super().__init__(parent)

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetBackgroundColour((204, 223, 252))
        self.SetMinSize((200, 100))

        self.SetDoubleBuffered(True)

        self.selected = False
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
        self.icon = icon
        topic_label = wx.StaticText(self, label=topic_name)
        topic_label.SetBackgroundColour(self.BG_COLOR)
        self.topic_label = topic_label

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
        self.selected = not self.selected
        new_bg = self.SELECTED_BG_COLOR if self.selected else self.BG_COLOR
        # w, h = self.GetClientSize()
        # self.SetMinSize((400, 400))
        # print(w,h)
        # if self.selected:
        #     self.SetMinSize((200, 100))
        # else:
        #     self.SetMinSize((int(w*1.2), int(h*1.2)))

        self.parent.Layout()
        self.parent.Refresh()
        # self.icon.SetBackgroundColour(new_bg)
        self.topic_label.SetBackgroundColour(new_bg)
        self.Refresh()
        event.Skip()

    def on_hover(self, event):
        self.hovering = True
        self.Refresh()
        event.Skip()

    def on_hover_stop(self, event):
        self.hovering = False
        self.Refresh()
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

            if self.selected:
                scale = 1.1
                gc.Scale(scale, scale)  # scale graphics context, not the DC
                w /= scale  # adjust size to match scaling
                h /= scale

            background_color = self.SELECTED_BG_COLOR if self.selected else self.BG_COLOR
            print(self.selected, background_color)
            # Background
            gc.SetBrush(wx.Brush(background_color))
            gc.SetPen(wx.NullGraphicsPen)
            gc.DrawRoundedRectangle(0, 0, w, h, settings.SLIGHTLY_ROUND_BORDER_RADIUS)

            # Border color (changes on focus)
            border_color = self.HOVER_BORDER_COLOR if self.hovering else self.BORDER_COLOR
            border_color = self.SELECTED_BORDER_COLOR if self.selected else border_color

            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.SetPen(wx.Pen(border_color, 2))
            gc.DrawRoundedRectangle(1, 1, w - 2, h - 2, settings.SLIGHTLY_ROUND_BORDER_RADIUS)


            #todo find a way to make only one panel bigger everytime
            # and then make the text also drawed, or just make the icon and the text grow
            # if self.icon != wx.NullBitmap:
            #     gc.DrawBitmap(self.icon, (w-48)//2,1, 48, 48)

