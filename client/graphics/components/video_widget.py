import os
import wx.svg
import wx
import clientProtocol
import settings


class VideoWidget(wx.Panel):
    BG_COLOR = wx.WHITE
    SELECTED_BG_COLOR = settings.BRIGHT_BLUE
    BORDER_COLOR = settings.BRIGHT_BORDER_COLOR
    HOVER_BORDER_COLOR = settings.BRIGHT_PINK
    SELECTED_BORDER_COLOR = settings.THEME_COLOR
    ICON_SIZE = 48
    ZOOM_FACTOR = 1.1

    def __init__(self, parent, video, width, ratio=4 / 3):
        """
        Initializes the VideoWidget, loading and scaling the video thumbnail and its zoomed
        variant, and binding hover, click, and paint events.
        :param parent: The parent wx window this widget belongs to.
        :param video: The video object containing video_id, amount_of_likes, and amount_of_comments.
        :param width: The display width of the widget in pixels.
        :param ratio: The height-to-width ratio used to calculate the widget's height.
        """
        super().__init__(parent)

        self.parent = parent
        self.video = video

        self.width = width
        self.ratio = ratio
        self.height = int(width * ratio)

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
        """
        Handles a left mouse button release by notifying the parent that this video was selected.
        :param event: The wx mouse event triggered on left click release.
        """
        self.parent.video_selected(self.video)

    def scale_thumbnail(self, thumbnail_image, zoom_factor=1.0):
        """
        Scales a thumbnail image to fill the widget's dimensions, applying an optional zoom factor,
        then center-crops it to the exact widget size.
        :param thumbnail_image: The wx.Image to scale and crop.
        :param zoom_factor: A multiplier applied on top of the base scale to zoom in. Defaults to 1.0.
        :return: A wx.Image cropped and scaled to fit the widget's width and height.
        """
        w, h = thumbnail_image.GetSize()

        scale_w = self.width / w
        scale_h = self.height / h

        scale = max(scale_h, scale_w) * zoom_factor

        new_w = int(w * scale)
        new_h = int(h * scale)
        print("new thumbnail size:", new_w, new_h)

        img = thumbnail_image.Scale(new_w, new_h, wx.IMAGE_QUALITY_HIGH)

        x = max(0, (new_w - self.width) // 2)
        y = max(0, (new_h - self.height) // 2)

        img = img.GetSubImage((x, y, self.width, self.height))
        return img

    def on_hover(self, event):
        """
        Handles the mouse entering the widget by enabling the hover state and triggering a repaint.
        :param event: The wx mouse event triggered when the cursor enters the widget.
        """
        self.hovering = True
        self.Refresh()
        event.Skip()

    def on_hover_stop(self, event):
        """
        Handles the mouse leaving the widget by disabling the hover state and triggering a repaint.
        :param event: The wx mouse event triggered when the cursor leaves the widget.
        """
        self.hovering = False
        self.Refresh()
        event.Skip()

    def on_resize(self, event):
        """
        Handles window resize events by triggering a repaint to redraw the thumbnail correctly.
        :param event: The wx size event triggered on window resize.
        """
        self.Refresh()
        event.Skip()

    def on_paint(self, event):
        """
        Paints the widget, drawing the thumbnail (zoomed in on hover) and overlaying like and
        comment counts when the user is hovering.
        :param event: The wx paint event triggered on each repaint.
        """
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()

        w, h = self.GetClientSize()

        bitmap = self.zoomed_in_thumbnail if self.hovering else self.thumbnail
        dc.DrawBitmap(bitmap, 0, 0)

        icons_size = 24

        font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_SEMIBOLD)
        dc.SetTextForeground(wx.WHITE)
        dc.SetFont(font)

        if self.hovering:
            like_bitmap = wx.Bitmap(wx.Image("assets\\like_icon_white.png").Scale(icons_size, icons_size))
            dc.DrawBitmap(like_bitmap, 10, h - 70)
            dc.DrawText(str(self.video.amount_of_likes), 40, h - 68)

            comments_bitmap = wx.Bitmap(wx.Image("assets\\comments_icon_white.png").Scale(icons_size, icons_size))
            dc.DrawBitmap(comments_bitmap, 10, h - 38)
            dc.DrawText(str(self.video.amount_of_comments), 40, h - 36)
