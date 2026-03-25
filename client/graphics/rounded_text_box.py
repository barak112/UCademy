import wx

import settings


class RoundedTextBox(wx.Panel):
    def __init__(self, parent, placeholder, image_bitmap):
        super().__init__(parent)

        self.border_color = wx.Colour(180, 180, 180)
        self.focus_color = settings.THEME_COLOR
        self.bg_color = (249, 250, 251)

        self.has_focus = False

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        # Inner text control
        self.text = wx.TextCtrl(
            self,
            style=wx.BORDER_NONE
        )
        self.text.SetBackgroundColour(wx.Colour(settings.THEME_COLOR))
        font = self.text.GetFont()
        font = font.Scale(1.5)
        self.text.SetFont(font)
        self.text.SetHint(placeholder)


        # Layout
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        image_bitmap = wx.StaticBitmap(self, bitmap=image_bitmap)
        sizer.Add(image_bitmap)
        sizer.Add(self.text, 1, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(sizer)

        # Events
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)

        self.text.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        self.text.Bind(wx.EVT_KILL_FOCUS, self.on_kill_focus)

    def get_text_ctrl(self):
        return self.text

    def on_focus(self, event):
        self.has_focus = True
        self.Refresh()
        event.Skip()

    def on_kill_focus(self, event):
        self.has_focus = False
        self.Refresh()
        event.Skip()

    def on_size(self, event):
        self.Refresh()
        event.Skip()

    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()

        gc = wx.GraphicsContext.Create(dc)
        if gc:
            w, h = self.GetClientSize()

            # Background
            gc.SetBrush(wx.Brush(self.bg_color))
            gc.SetPen(wx.NullGraphicsPen)
            gc.DrawRoundedRectangle(0, 0, w, h, 10)

            # Border color (changes on focus)
            border = self.focus_color if self.has_focus else self.border_color

            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.SetPen(wx.Pen(border, 2))
            gc.DrawRoundedRectangle(1, 1, w - 2, h - 2, 10)
