import os
import wx.svg
import wx
import clientProtocol
import settings


class VideoWidget(wx.Panel):
    BG_COLOR = wx.WHITE
    SELECTED_BG_COLOR = settings.BRIGHT_BLUE
    BORDER_COLOR = settings.BRIGHT_BORDER_COLOR
    HOVER_BORDER_COLOR = settings.BRIGHT_PINK  # maybe change to theme color but brighter
    SELECTED_BORDER_COLOR = settings.THEME_COLOR
    ICON_SIZE = 48
    ZOOM_FACTOR = 1.1

    def __init__(self, parent, video, width, ratio = 4 / 3):
        super().__init__(parent)

        self.parent = parent
        self.video = video

        self.width = width
        self.ratio = ratio
        self.height = int(width*ratio)

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetBackgroundColour((204, 223, 252))
        self.SetMinSize((width, self.height))

        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))

        self.SetDoubleBuffered(True)

        self.hovering = False

        thumbnail_path = f"media\\{video.video_id}.png"
        if not os.path.isfile(thumbnail_path):
            thumbnail_path = "assets\\no_thumbnail.png"

        self.thumbnail = self.scale_thumbnail(wx.Image(thumbnail_path))
        self.zoomed_in_thumbnail = self.scale_thumbnail(self.thumbnail, self.ZOOM_FACTOR)

        self.thumbnail = wx.Bitmap(self.thumbnail)
        self.zoomed_in_thumbnail = wx.Bitmap(self.zoomed_in_thumbnail)

        self.Bind(wx.EVT_SIZE, self.on_resize)

        self.Bind(wx.EVT_PAINT, self.on_paint)

        self.Bind(wx.EVT_ENTER_WINDOW, self.on_hover)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_hover_stop)

        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)

    def on_left_up(self, event):
        self.parent.video_selected(self.video)

    def scale_thumbnail(self, thumbnail_image, zoom_factor = 1.0):
        w, h = thumbnail_image.GetSize()

        scale_w = self.width / w
        scale_h = self.height / h

        scale = max(scale_h, scale_w) * zoom_factor

        new_w = int(w * scale)
        new_h = int(h * scale)
        print("new thumbnail size:", new_w, new_h)

        # scale image
        img = thumbnail_image.Scale(new_w, new_h, wx.IMAGE_QUALITY_HIGH)
        # center crop
        x = (new_w - self.width) // 2
        y = (new_h - self.height) // 2

        x = max(0, x)
        y = max(0, y)

        img = img.GetSubImage((x, y, self.width, self.height))

        return img

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

        w,h = self.GetClientSize()

        bitmap = self.zoomed_in_thumbnail if self.hovering else self.thumbnail
        dc.DrawBitmap(bitmap, 0, 0)

        icons_size = 24

        #font
        font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_SEMIBOLD)
        dc.SetTextForeground(wx.WHITE)
        dc.SetFont(font)

        if self.hovering:
            # draw likes amount
            like_bitmap = wx.Bitmap(wx.Image("assets\\like_icon_white.png").Scale(icons_size, icons_size))
            dc.DrawBitmap(like_bitmap, 10, h - 70)
            dc.DrawText(str(self.video.amount_of_likes), 40, h-68)

            # draw comments amount
            comments_bitmap = wx.Bitmap(wx.Image("assets\\comments_icon_white.png").Scale(icons_size, icons_size))
            dc.DrawBitmap(comments_bitmap, 10, h - 38)
            dc.DrawText(str(self.video.amount_of_comments), 40, h - 36)

            # draw creator's name
            # like_bitmap = wx.Bitmap(wx.Image("assets\\like_icon_white.png").Scale(icons_size, icons_size))
            # dc.DrawBitmap(like_bitmap, 10, h - 50)
            # dc.DrawText(str(self.video.amount_of_likes), 40, h - 48)

        # gc = wx.GraphicsContext.Create(dc)
        # if gc:
        #     w, h = self.GetClientSize()
        #
        #     # if self.hovering:
        #     #     scale = 1.1
        #     #     gc.Scale(scale, scale)  # scale graphics context, not the DC
        #     #     w /= scale  # adjust size to match scaling
        #     #     h /= scale
        #
        #     # Background image
        #     gc.DrawBitmap(self.thumbnail)
        #
        #
        #     # Border color (changes on focus)
        #     border_color = self.HOVER_BORDER_COLOR if self.hovering else self.BORDER_COLOR
        #     border_color = self.SELECTED_BORDER_COLOR if self.selected else border_color
        #
        #     gc.SetBrush(wx.TRANSPARENT_BRUSH)
        #     gc.SetPen(wx.Pen(border_color, 2))
        #     gc.DrawRoundedRectangle(1, 1, w - 2, h - 2, settings.SLIGHTLY_ROUND_BORDER_RADIUS)
        #
        #     space = 10
        #
        #     gc.SetFont(
        #         wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_SEMIBOLD),
        #         wx.BLACK)
        #
        #     iw, ih = self.icon.GetSize()
        #     tw, th = gc.GetTextExtent(self.topic_name)
        #     full_height = ih + th + space
        #
        #     start_pos = (h - full_height) // 2
        #
        #     if self.icon != wx.NullBitmap:
        #         gc.DrawBitmap(self.icon, (w - 48) // 2, start_pos, iw, ih)
        #
        #     if self.selected:
        #         gc.DrawBitmap(self.selected_icon, (w - 40), 10, 30, 30)
        #
        #     gc.DrawText(self.topic_name, (w - tw) / 2, ih + space + start_pos)

