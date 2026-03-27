import wx


class RoundedButton(wx.Panel):
    def __init__(self, parent, label, color):
        """

        :param parent: parent to add the button to
        :param label: which label to put inside the button
        :param color: what color should be the button
        """
        super().__init__(parent)

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetDoubleBuffered(True)
        self.SetWindowStyleFlag(wx.WANTS_CHARS)  # 👈 important

        self.label = label
        self.base_color = wx.Colour(color)
        self.hover_color = self.make_darker(self.base_color, 15)  # 15% darker
        self.mouse_clicked_color = self.make_darker(self.hover_color, 20)
        self.mouse_over = False
        self.mouse_clicked = False

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        # Event Bindings
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)

        # Hover Bindings
        self.Bind(wx.EVT_ENTER_WINDOW, self.on_mouse_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_mouse_leave)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_click)
        self.Bind(wx.EVT_LEFT_UP, self.on_mouse_release)

    def make_darker(self, color, percent):
        """creates a hover color."""
        r, g, b = color.Get()[:3]
        return wx.Colour(
            min(255, int(r * (1 - percent / 100))),
            min(255, int(g * (1 - percent / 100))),
            min(255, int(b * (1 - percent / 100)))
        )

    def on_mouse_click(self, event):
        """handles button mouse click, indicates to change the button's color"""
        self.mouse_clicked = True
        self.CaptureMouse()
        self.Refresh()
        self.Update()

    def on_mouse_release(self, event):
        """handles button mouse release, indicates to change the button's color"""
        if self.HasCapture():
            self.ReleaseMouse()

        # Delay resetting the state (e.g. 100ms)
        wx.CallLater(100, self.reset_click_state)

    def reset_click_state(self):
        self.mouse_clicked = False
        self.Refresh()

    def on_mouse_enter(self, event):
        """triggers when hovering over button"""
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
            current_color = self.mouse_clicked_color if self.mouse_clicked else current_color

            gc.SetBrush(wx.Brush(current_color))
            gc.SetPen(wx.NullGraphicsPen)
            gc.DrawRoundedRectangle(0, 0, w, h, 15)

            gc.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD), wx.WHITE)
            tw, th = gc.GetTextExtent(self.label)
            gc.DrawText(self.label, (w - tw) / 2, (h - th) / 2)
