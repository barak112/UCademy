import os
import wx.svg
import wx

import clientProtocol
import settings


class TopicWidget(wx.Panel):
    BG_COLOR = wx.WHITE
    SELECTED_BG_COLOR = settings.BRIGHT_BLUE
    BORDER_COLOR = settings.BRIGHT_BORDER_COLOR
    HOVER_BORDER_COLOR = settings.BRIGHT_PINK  # maybe change to theme color but brighter
    SELECTED_BORDER_COLOR = settings.THEME_COLOR
    ICON_SIZE = 48

    def __init__(self, parent, topic_name):
        """
        Initializes a topic widget with an icon, topic name label, and hover/selection visual states.
        :param parent: The parent PickTopicsPanel this widget belongs to.
        :param topic_name: The name of the topic this widget represents.
        """
        super().__init__(parent)

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetBackgroundColour((204, 223, 252))
        self.SetMinSize((settings.TOPIC_WIDGET_WIDTH, settings.TOPIC_WIDGET_WIDTH // 2))

        self.selected_icon = wx.Image("assets\\selected_topic_icon.png", wx.BITMAP_TYPE_PNG)
        self.selected_icon = wx.Bitmap(self.selected_icon.Scale(60, 60))

        self.SetDoubleBuffered(True)

        self.selected = False
        self.parent = parent
        self.topic_name = topic_name

        self.hovering = False
        self.icon = wx.NullBitmap
        if os.path.isfile(f"assets\\topics_icons\\{topic_name}.png"):
            self.icon = wx.Image(f"assets\\topics_icons\\{topic_name}.png").Scale(48, 48)
            self.icon = wx.Bitmap(self.icon)
            # todo get emojies from https://github.com/microsoft/fluentui-emoji/blob/main/assets using the 3d png version

        self.Bind(wx.EVT_SIZE, self.on_resize)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_ENTER_WINDOW, self.on_hover)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_hover_stop)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)

    def on_left_up(self, event):
        """
        Toggles the selected state of the widget and notifies the parent panel.
        :param event: The wx mouse up event.
        """
        self.selected = not self.selected
        self.parent.topic_selected(self.topic_name)
        self.Refresh()
        event.Skip()

    def on_hover(self, event):
        """
        Sets the hovering state to True and triggers a repaint to show the hover border.
        :param event: The wx mouse enter event.
        """
        self.hovering = True
        self.Refresh()
        event.Skip()

    def on_hover_stop(self, event):
        """
        Clears the hovering state and triggers a repaint to restore the default border.
        :param event: The wx mouse leave event.
        """
        self.hovering = False
        self.Refresh()
        event.Skip()

    def on_resize(self, event):
        """
        Triggers a repaint when the widget is resized.
        :param event: The wx size event.
        """
        self.Refresh()
        event.Skip()

    def on_paint(self, event):
        """
        Draws the widget background, border, icon, selection indicator, and topic name label.
        :param event: The wx paint event.
        """
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
            full_height = ih + th + space

            start_pos = (h - full_height) // 2

            if self.icon != wx.NullBitmap:
                gc.DrawBitmap(self.icon, (w - 48) // 2, start_pos, iw, ih)

            if self.selected:
                gc.DrawBitmap(self.selected_icon, (w - 40), 10, 30, 30)

            gc.DrawText(self.topic_name, (w - tw) / 2, ih + space + start_pos)
