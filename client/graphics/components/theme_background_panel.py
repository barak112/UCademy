import wx

import settings


class ThemeBackgroundPanel(wx.Panel):
    BG_COLOR = settings.THEME_COLOR

    def __init__(self, parent, image_bitmap):
        super().__init__(parent)

        # background image
        self.background_bitmap = wx.Bitmap("assets\\blue_bg.png", wx.BITMAP_TYPE_PNG)
        self.SetMaxSize(self.background_bitmap.GetSize())
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_resize)

        # Ucademy logo
        self.icon_with_text = image_bitmap

    def on_paint(self, event):
        """draws the background image on the left side of the screen"""
        dc = wx.BufferedPaintDC(self)
        dc.DrawBitmap(self.background_bitmap, 0, 0)

        left_width, left_height, = self.GetSize()

        icon_width, icon_height = self.icon_with_text.GetSize()
        x = (left_width - icon_width) // 2
        y = (left_height - icon_height) // 2
        dc.DrawBitmap(self.icon_with_text, x, y)

    def on_resize(self, event):
        """redraws the screen whenever the screen resizes, used to redraw the background image"""
        self.Refresh()  # trigger repaint
        event.Skip()
