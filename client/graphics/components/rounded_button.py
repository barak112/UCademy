import wx


class RoundedButton(wx.Panel):
    def __init__(self, parent, label, color, pos=wx.DefaultPosition, size=wx.DefaultSize):
        super().__init__(parent, pos=pos, size=size)

        self.label = label
        self.base_color = wx.Colour(color)
        self.hover_color = self.make_darker(self.base_color, 15)  # 15% lighter
        self.mouse_over = False  # State tracker

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        # Event Bindings
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)

        # Hover Bindings
        self.Bind(wx.EVT_ENTER_WINDOW, self.on_mouse_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_mouse_leave)

    def make_darker(self, color, percent):
        """Helper to programmatically create a hover color."""
        r, g, b = color.Get()[:3]
        return wx.Colour(
            min(255, int(r * (1 - percent / 100))),
            min(255, int(g * (1 - percent / 100))),
            min(255, int(b * (1 - percent / 100)))
        )


    def on_mouse_enter(self, event):
        self.mouse_over = True
        self.Refresh()  # Redraw with hover color

    def on_mouse_leave(self, event):
        self.mouse_over = False
        self.Refresh()  # Redraw with base color

    def on_size(self, event):
        self.Refresh()
        event.Skip()

    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        gc = wx.GraphicsContext.Create(dc)

        if gc:
            w, h = self.GetClientSize()

            # Switch color based on hover state
            current_color = self.hover_color if self.mouse_over else self.base_color

            gc.SetBrush(wx.Brush(current_color))
            gc.SetPen(wx.NullGraphicsPen)
            gc.DrawRoundedRectangle(0, 0, w, h, 15)

            gc.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD), wx.WHITE)
            tw, th = gc.GetTextExtent(self.label)
            gc.DrawText(self.label, (w - tw) / 2, (h - th) / 2)
