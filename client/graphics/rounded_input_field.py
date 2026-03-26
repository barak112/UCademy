import wx
import settings


class RoundedInputField(wx.Panel):
    #graphics constants
    BORDER_COLOR = wx.Colour(180, 180, 180)
    FOCUS_COLOR = settings.THEME_COLOR
    BG_COLOR = wx.Colour(249, 250, 251)


    def __init__(self, parent, placeholder, field_icon_bitmap, is_password = False):
        super().__init__(parent)
        
        #attributes
        self.has_focus = False # used to change the text box border color
        self.text_shown = True # used for password show and hide

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT) # gets control of screen paint from OS
        
        # visible text input widget
        self.text_visible = wx.TextCtrl(self, style=wx.BORDER_NONE)
        self.text_visible.SetBackgroundColour(wx.Colour((249, 250, 251)))
        
        font = self.text_visible.GetFont()
        font = font.Scale(1.5)
        self.text_visible.SetFont(font)
        self.text_visible.SetHint(placeholder)

        # hidden text input widget
        self.text_hidden = wx.TextCtrl(self, style=wx.TE_PASSWORD | wx.BORDER_NONE)
        self.text_hidden.SetBackgroundColour(wx.Colour((249, 250, 251)))
        self.text_hidden.SetFont(font)
        self.text_hidden.SetHint(placeholder)


        # Layout
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        field_icon_bitmap = wx.StaticBitmap(self, bitmap=field_icon_bitmap)

        self.sizer.Add(field_icon_bitmap, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 20)

        self.sizer.Add(self.text_visible, 1, wx.ALL | wx.EXPAND, 20)
        self.sizer.Add(self.text_hidden, 1, wx.ALL | wx.EXPAND, 20)

        self.text_hidden.Hide()

        if is_password: # if is a password field
            self.text_visible.Hide()
            self.text_hidden.Show()
            self.text_shown = False

            show_password_icon = wx.Bitmap("assets\\show_password_icon.png", wx.BITMAP_TYPE_PNG)
            self.password_visibility_icon = wx.StaticBitmap(self, bitmap=show_password_icon)
            self.sizer.Add(self.password_visibility_icon, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 20)
            # handle change password visibility on icon press
            self.password_visibility_icon.Bind(wx.EVT_LEFT_DOWN, self.toggle_show_password)

        self.SetSizer(self.sizer)

        # Events
        self.Bind(wx.EVT_PAINT, self.on_paint) # paint round field border
        self.Bind(wx.EVT_SIZE, self.on_size) # paint on every resize

        self.text_visible.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        self.text_visible.Bind(wx.EVT_KILL_FOCUS, self.on_kill_focus)

        self.text_hidden.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        self.text_hidden.Bind(wx.EVT_KILL_FOCUS, self.on_kill_focus)

    def toggle_show_password(self, event):
        if self.text_shown: # hide text
            hide_password_icon = wx.Bitmap("assets\\show_password_icon.png", wx.BITMAP_TYPE_PNG)
            self.password_visibility_icon.SetBitmap(hide_password_icon)
            self.text_shown = False

            self.text_hidden.SetValue(self.text_visible.GetValue())

            self.text_hidden.SetFocus()
            self.text_hidden.SetInsertionPoint(self.text_visible.GetInsertionPoint())

            self.text_visible.Hide()
            self.text_hidden.Show()

        else: # show text
            show_password_icon = wx.Bitmap(wx.Image("assets\\hide_password_icon.png"))
            self.password_visibility_icon.SetBitmap(show_password_icon)
            self.text_shown = True
            self.text_visible.SetValue(self.text_hidden.GetValue())

            self.text_visible.SetFocus()
            self.text_visible.SetInsertionPoint(self.text_hidden.GetInsertionPoint())

            self.text_visible.Show()
            self.text_hidden.Hide()
        self.sizer.Layout()

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
            gc.SetBrush(wx.Brush(self.BG_COLOR))
            gc.SetPen(wx.NullGraphicsPen)
            gc.DrawRoundedRectangle(0, 0, w, h, 10)

            # Border color (changes on focus)
            border_color = self.FOCUS_COLOR if self.has_focus else self.BORDER_COLOR

            gc.SetBrush(wx.TRANSPARENT_BRUSH)
            gc.SetPen(wx.Pen(border_color, 2))
            gc.DrawRoundedRectangle(1, 1, w - 2, h - 2, 10)

    def get_value(self):
        if self.text_shown:
            value = self.text_visible.GetValue()
        else:
            value = self.text_hidden.GetValue()
        return value
