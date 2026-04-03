import string

import wx

import settings


class VerificationCodeCubes(wx.Panel):
    BG_COLOR = wx.WHITE
    # BG_COLOR = settings.OFF_WHITE
    BORDER_COLOR = settings.BORDER_COLOR
    FOCUSED_BORDER_COLOR = settings.THEME_COLOR
    FILLED_BOX_BG = settings.BRIGHT_PINK
    BOX_SIZE = (62, 75)
    SPACING = 10
    BOXES_AMOUNT = 6


    def __init__(self, code_ver_panel, parent):
        super().__init__(parent)

        self.code_ver_panel = code_ver_panel

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)  # gets control of screen paint from OS
        self.SetBackgroundColour(self.BG_COLOR) # fallback, drawing is done in on_paint
        self.SetWindowStyleFlag(wx.WANTS_CHARS)

        self.code = ""


        self.Bind(wx.EVT_SIZE, self.on_resize)
        self.Bind(wx.EVT_PAINT, self.on_paint)

        x_size = self.BOX_SIZE[0] * self.BOXES_AMOUNT + self.SPACING* (self.BOXES_AMOUNT-1)
        self.SetMinSize((x_size + 2, self.BOX_SIZE[1] + 2))

        self.start_end_spacing = self.GetClientSize()[0] - x_size
        self.start_end_spacing /= 2

        self.Bind(wx.EVT_CHAR, self.on_char_down)

    def on_char_down(self, event):
        key = event.GetKeyCode()

        if key == wx.WXK_BACK:
            self.code = self.code[:-1]

        elif key == wx.WXK_RETURN and len(self.code) == self.BOXES_AMOUNT:
            print("enter")

        elif key < 256 and len(self.code)<self.BOXES_AMOUNT:
            key = chr(key)
            if key in string.digits:
                self.code += key

        if len(self.code) == self.BOXES_AMOUNT:
            self.code_ver_panel.verification_code_full()
        else:
            self.code_ver_panel.verification_code_not_full()

        self.Refresh()
        event.Skip()

    def on_resize(self, event):
        self.Refresh()
        event.Skip()
        self.start_end_spacing = self.GetClientSize()[0] - self.BOXES_AMOUNT * self.BOX_SIZE[0]
        self.start_end_spacing -= self.SPACING * (self.BOXES_AMOUNT - 1)
        self.start_end_spacing /= 2

    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.Clear()

        gc = wx.GraphicsContext.Create(dc)
        if gc:
            x, y = self.start_end_spacing, 1
            for box_index in range(self.BOXES_AMOUNT):
                background_color = self.FILLED_BOX_BG if len(self.code) > box_index else self.BG_COLOR

                gc.SetBrush(wx.Brush(background_color))
                gc.SetPen(wx.NullGraphicsPen)
                gc.DrawRoundedRectangle(x, y, self.BOX_SIZE[0], self.BOX_SIZE[1], settings.ROUND_BORDER_RADIUS)

                border_color = self.FOCUSED_BORDER_COLOR if len(self.code) == box_index else self.BORDER_COLOR

                gc.SetBrush(wx.TRANSPARENT_BRUSH)
                gc.SetPen(wx.Pen(border_color, 2))
                gc.DrawRoundedRectangle(x, y, self.BOX_SIZE[0], self.BOX_SIZE[1], settings.ROUND_BORDER_RADIUS)

                # draw digit
                if len(self.code) > box_index:
                    digit = self.code[box_index]
                    gc.SetFont(wx.Font(settings.VERIFICATION_CODE_FONT_SIZE, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                                       wx.FONTWEIGHT_BOLD, faceName="Roboto"), wx.BLACK)
                    tw, th = gc.GetTextExtent(digit)
                    gc.DrawText(digit, x+(self.BOX_SIZE[0]-tw)/2,y +1+ (self.BOX_SIZE[1] - th) / 2)

                x += self.BOX_SIZE[0] + self.SPACING

    def get_value(self):
        return self.code
