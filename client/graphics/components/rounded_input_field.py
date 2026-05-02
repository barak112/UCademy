import wx
import settings


class RoundedInputField(wx.Panel):
    # graphics constants
    BORDER_COLOR = settings.BORDER_COLOR
    FOCUS_COLOR = settings.THEME_COLOR
    BG_COLOR = settings.OFF_WHITE

    def __init__(self, panel, parent, field_name, placeholder, field_icon_bitmap=None, is_password=False,
                 multiline=False, background_color=settings.OFF_WHITE):
        """
        Initializes the RoundedInputField with a styled text control, optional icon, and optional password visibility toggle.
        :param panel: The panel that owns this field, used to call field_is_filled and field_is_unfilled.
        :param parent: The parent wx window this widget is added to.
        :param field_name: The identifier used when notifying the panel of fill state changes.
        :param placeholder: The placeholder hint text shown inside the text control when empty.
        :param field_icon_bitmap: An optional bitmap icon displayed to the left of the text control.
        :param is_password: Whether this field should obscure input as a password field.
        :param multiline: Whether this field should support multiple lines of text.
        :param background_color: The background color of the panel surrounding the input field.
        """
        super().__init__(parent)
        self.panel = panel
        self.field_name = field_name

        self.has_focus = False
        self.text_shown = True

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.SetBackgroundColour(background_color)

        style = wx.BORDER_NONE | wx.TE_PROCESS_ENTER
        if multiline:
            style = style | wx.TE_MULTILINE | wx.TE_WORDWRAP

        self.text_visible = wx.TextCtrl(self, style=style)
        self.text_visible.SetBackgroundColour(wx.Colour((249, 250, 251)))

        font = self.text_visible.GetFont()
        font = font.Scale(1.5)
        self.text_visible.SetFont(font)
        self.text_visible.SetHint(placeholder)

        self.text_hidden = wx.TextCtrl(self, style=style | wx.TE_PASSWORD)
        self.text_hidden.SetBackgroundColour(wx.Colour((249, 250, 251)))
        self.text_hidden.SetFont(font)
        self.text_hidden.SetHint(placeholder)

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        if field_icon_bitmap:
            field_icon_bitmap = wx.StaticBitmap(self, bitmap=field_icon_bitmap)
            self.sizer.Add(field_icon_bitmap, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 20)

        self.SetMinSize((0, 65))

        if multiline:
            self.sizer.Add(self.text_visible, 1, wx.EXPAND | wx.ALL, 20)
        else:
            self.sizer.Add(self.text_visible, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 20)
        self.sizer.Add(self.text_hidden, 1, wx.EXPAND | wx.ALL, 20)

        self.text_hidden.Hide()

        if is_password:
            self.text_visible.Hide()
            self.text_hidden.Show()
            self.text_shown = False

            show_password_icon = wx.Bitmap("assets\\show_password_icon.png", wx.BITMAP_TYPE_PNG)
            self.password_visibility_icon = wx.StaticBitmap(self, bitmap=show_password_icon)
            self.sizer.Add(self.password_visibility_icon, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 20)
            self.password_visibility_icon.Bind(wx.EVT_LEFT_UP, self.toggle_show_password)

        self.SetSizer(self.sizer)

        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)

        self.text_visible.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        self.text_visible.Bind(wx.EVT_KILL_FOCUS, self.on_kill_focus)

        self.text_hidden.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        self.text_hidden.Bind(wx.EVT_KILL_FOCUS, self.on_kill_focus)

        self.text_visible.Bind(wx.EVT_TEXT, self.on_text_change)
        self.text_hidden.Bind(wx.EVT_TEXT, self.on_text_change)

    def on_text_change(self, event):
        """
        Handles text change events by notifying the parent panel whether the field is filled or empty.
        :param event: The wx text event triggered whenever the field's content changes.
        """
        ctrl = event.GetEventObject()
        value = ctrl.GetValue()

        if value.strip() == "":
            self.panel.field_is_unfilled(self.field_name)
        else:
            self.panel.field_is_filled(self.field_name)

        event.Skip()

    def toggle_show_password(self, event):
        """triggered once clicked on the eye icon on the password field, toggles between text shown and hidden"""
        if self.text_shown:
            hide_password_icon = wx.Bitmap("assets\\show_password_icon.png", wx.BITMAP_TYPE_PNG)
            self.password_visibility_icon.SetBitmap(hide_password_icon)
            self.text_shown = False

            self.text_hidden.SetValue(self.text_visible.GetValue())

            self.text_hidden.SetFocus()
            self.text_hidden.SetInsertionPoint(self.text_visible.GetInsertionPoint())

            self.text_visible.Hide()
            self.text_hidden.Show()

        else:
            show_password_icon = wx.Bitmap(wx.Image("assets\\hide_password_icon.png"))
            self.password_visibility_icon.SetBitmap(show_password_icon)
            self.text_shown = True
            self.text_visible.SetValue(self.text_hidden.GetValue())

            self.text_visible.SetFocus()
            self.text_visible.SetInsertionPoint(self.text_hidden.GetInsertionPoint())

            self.text_visible.Show()
            self.text_hidden.Hide()
        self.sizer.Layout()
        event.Skip()

    def on_focus(self, event):
        """once field focused, indicates to change the field border color"""
        self.has_focus = True
        self.Refresh()
        event.Skip()

    def on_kill_focus(self, event):
        """once field focused, indicates to change the field border color back to default"""
        self.has_focus = False
        self.Refresh()
        event.Skip()

    def on_size(self, event):
        """triggers field redraw once field resized"""
        self.Refresh()
        event.Skip()

    def on_paint(self, event):
        """paints the rounded field borders, color of them is according to self.has_focused"""
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()

        gc = wx.GraphicsContext.Create(dc)
        if gc:
            w, h = self.GetClientSize()

            gc.SetBrush(wx.Brush(self.BG_COLOR))
            gc.SetPen(wx.NullGraphicsPen)
            gc.DrawRoundedRectangle(0, 0, w, h, settings.ROUND_BORDER_RADIUS)

            border_color = self.FOCUS_COLOR if self.has_focus else self.BORDER_COLOR

            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.SetPen(wx.Pen(border_color, 2))
            gc.DrawRoundedRectangle(1, 1, w - 2, h - 2, settings.ROUND_BORDER_RADIUS)

    def get_value(self):
        """returns the value of the field"""
        if self.text_shown:
            value = self.text_visible.GetValue()
        else:
            value = self.text_hidden.GetValue()
        return value

    def get_text_visible(self):
        """returns the visible text textCtrl widget"""
        return self.text_visible

    def get_text_hidden(self):
        """returns the hidden text textCtrl widget"""
        return self.text_hidden

    def set_value(self, value):
        """sets the value of the field"""
        if self.text_shown:
            self.text_visible.SetValue(value)
        else:
            self.text_hidden.SetValue(value)

        if value == "":
            self.panel.field_is_unfilled(self.field_name)
        else:
            self.panel.field_is_filled(self.field_name)
