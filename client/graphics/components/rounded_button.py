import os.path

import wx

import settings


class RoundedButton(wx.Panel):
    def __init__(self, parent, label_or_path, base_color=settings.UNACTIVE_BUTTON, background_color=settings.OFF_WHITE,
                 radius=settings.ROUND_BORDER_RADIUS, font_size=settings.BUTTON_TEXT_FONT_SIZE, circle=False,
                 use_image=False, text_color=wx.WHITE):
        """
        Initializes a custom rounded button panel with hover, click, and image support.
        :param parent: parent to add the button to
        :param label_or_path: which label to put inside the button
        :param base_color: what color should be the button
        :param background_color: the color of the area surrounding the button.
        :param radius: the corner radius of the rounded rectangle.
        :param font_size: font size of the button label text.
        :param circle: if True, draws the button as a circle instead of a rounded rectangle.
        :param use_image: if True, renders an image from label_or_path instead of text.
        :param text_color: the color of the button label text.
        """
        super().__init__(parent)

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.SetDoubleBuffered(True)
        self.SetWindowStyleFlag(wx.WANTS_CHARS)
        self.SetMinSize((0, settings.BUTTON_SIZE_Y))
        self.SetBackgroundColour(background_color)

        self.label_or_path = label_or_path
        self.base_color = wx.Colour(base_color)
        self.current_color = wx.Colour(base_color)
        self.radius = radius
        self.font_size = font_size
        self.circle = circle
        self.text_color = text_color
        if use_image and os.path.isfile(label_or_path):
            self.use_image = use_image
        else:
            self.use_image = wx.NullImage
        self.hover_color = self.make_darker(self.current_color, 15)  # 15% darker
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

    def set_active(self, active):
        """
        Toggles the button between its active (theme color) and inactive (base color) appearance.
        :param active: If True, sets the button to its active color; otherwise reverts to base color.
        """
        if active:
            self.current_color = wx.Colour(settings.THEME_COLOR)
        else:
            self.current_color = wx.Colour(self.base_color)
        self.Refresh()

    def make_darker(self, color, percent):
        """creates a hover color."""
        r, g, b = color.Get()[:3]
        return wx.Colour(
            min(255, int(r * (1 - percent / 100))),
            min(255, int(g * (1 - percent / 100))),
            min(255, int(b * (1 - percent / 100)))
        )

    def on_mouse_click(self, event):
        """
        Handles mouse button down, marking the button as clicked and triggering a repaint.
        :param event: The wx mouse down event.
        """
        self.mouse_clicked = True
        self.Refresh()
        self.Update()
        event.Skip()

    def on_mouse_release(self, event):
        """
        Handles mouse button release and schedules a reset of the clicked state after a short delay.
        :param event: The wx mouse up event.
        """
        wx.CallLater(100, self.reset_click_state)
        event.Skip()

    def reset_click_state(self):
        """
        Resets the clicked state of the button and triggers a repaint.
        """
        self.mouse_clicked = False
        self.Refresh()

    def on_mouse_enter(self, event):
        """triggers when hovering over button"""
        self.mouse_over = True
        self.Refresh()  # Redraw with hover color
        event.Skip()

    def on_mouse_leave(self, event):
        """
        Resets hover and click states when the mouse leaves the button area.
        :param event: The wx mouse leave event.
        """
        self.mouse_clicked = False
        self.mouse_over = False
        self.Refresh()  # Redraw with base color
        event.Skip()

    def on_size(self, event):
        """
        Triggers a repaint when the button is resized.
        :param event: The wx size event.
        """
        self.Refresh()
        event.Skip()

    def on_paint(self, event):
        """
        Draws the button shape and its label or image, applying the correct color based on hover and click state.
        :param event: The wx paint event.
        """
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()
        gc = wx.GraphicsContext.Create(dc)

        self.hover_color = self.make_darker(self.current_color, 15)  # 15% darker
        self.mouse_clicked_color = self.make_darker(self.hover_color, 20)

        if gc:
            w, h = self.GetClientSize()

            # Switch color based on hover state
            current_color = self.hover_color if self.mouse_over else self.current_color  # hover color if hovering
            current_color = self.mouse_clicked_color if self.mouse_clicked else current_color  # clicked color if clicked

            gc.SetBrush(wx.Brush(current_color))
            gc.SetPen(wx.NullGraphicsPen)
            if self.circle:
                gc.DrawEllipse(0, 0, w, h)

            else:
                gc.DrawRoundedRectangle(0, 0, w, h, self.radius)

            if self.use_image:
                if self.label_or_path:
                    iw, ih = 32, 32
                    gc.DrawBitmap(wx.Bitmap(wx.Image(self.label_or_path).Scale(iw, ih, wx.IMAGE_QUALITY_HIGH)),
                                  (w - iw) / 2, (h - ih) / 2,
                                  iw, ih)
            else:
                gc.SetFont(wx.Font(self.font_size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD),
                           self.text_color)
                tw, th = gc.GetTextExtent(self.label_or_path)
                gc.DrawText(self.label_or_path, (w - tw) / 2, (h - th) / 2)

    def set_background_color(self, color):
        """
        Updates the button's current draw color and triggers a repaint.
        :param color: The new color to apply to the button.
        """
        self.current_color = wx.Colour(color)
