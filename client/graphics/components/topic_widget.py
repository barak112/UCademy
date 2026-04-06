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
        self.SetMinSize((250, 250//2))

        self.SetDoubleBuffered(True)

        self.selected = False
        self.parent = parent
        self.topic_name = topic_name

        self.hovering = False
        self.icon = wx.NullBitmap
        if os.path.isfile(f"assets\\topics_icons\\{topic_name}.png"):
            self.icon = wx.Image(f"assets\\topics_icons\\{topic_name}.png").Scale(48,48)
            self.icon = wx.Bitmap(self.icon)
            #todo get emojies from https://github.com/microsoft/fluentui-emoji/blob/main/assets using the 3d png version


        # icon = wx.StaticBitmap(self, bitmap=icon)
        # icon.SetBackgroundColour(self.BG_COLOR)
        # self.icon = icon
        # topic_label = wx.StaticText(self, label=topic_name)
        # topic_label.SetBackgroundColour(self.BG_COLOR)
        # self.topic_label = topic_label

        # label_and_icon_vbox = wx.BoxSizer(wx.VERTICAL)
        # label_and_icon_vbox.Add(icon, 0, wx.ALIGN_CENTER_HORIZONTAL)
        # label_and_icon_vbox.Add(topic_label, 0, wx.ALIGN_CENTER_HORIZONTAL)

        #
        # vbox = wx.BoxSizer(wx.VERTICAL)
        # self.SetSizer(vbox)

        # vbox.AddStretchSpacer()
        # vbox.Add(label_and_icon_vbox, 0, wx.ALIGN_CENTER_HORIZONTAL)
        # vbox.AddStretchSpacer()

        self.Bind(wx.EVT_SIZE, self.on_resize)

        self.Bind(wx.EVT_PAINT, self.on_paint)

        self.Bind(wx.EVT_ENTER_WINDOW, self.on_hover)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_hover_stop)

        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)


    def on_left_up(self, event):
        self.selected = not self.selected
        self.parent.topic_selected(self.topic_name)
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

            space = 10

            gc.SetFont(
                wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_SEMIBOLD),
                wx.BLACK)

            iw, ih = self.icon.GetSize()
            tw, th = gc.GetTextExtent(self.topic_name)
            full_height =  ih + th + space

            start_pos = (h-full_height)//2

            if self.icon != wx.NullBitmap:
                gc.DrawBitmap(self.icon, (w-48)//2,start_pos, iw, ih)


            gc.DrawText(self.topic_name, (w - tw) / 2, ih+space+start_pos)

