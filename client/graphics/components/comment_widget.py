import os.path

import wx

import settings


class CommentWidget(wx.Panel):
    BG_COLOR = settings.OFF_WHITE
    HOVER_COLOR = (220, 220, 220)
    def __init__(self, parent, comment):
        super().__init__(parent)

        self.is_hovered = False
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(main_sizer)

        separator_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.comment = comment

        # pfp_path = f"..\\..\\media\\{comment.commenter}.png"
        # if not os.path.isfile(pfp_path):
        #     pfp_path = "\\..\\assets\\null_pfp.png"

        pfp_path = f"media\\{comment.commenter}.png"
        if not os.path.isfile(pfp_path):
            pfp_path = "assets\\null_pfp.png"


        pfp = wx.Bitmap(wx.Image(pfp_path).Scale(settings.PFP_SIZE, settings.PFP_SIZE))
        pfp = wx.StaticBitmap(self, bitmap=pfp)

        # right size
        right_sizer = wx.BoxSizer(wx.VERTICAL)


        # username label
        username_label = wx.StaticText(self, label=comment.commenter)
        font = username_label.GetFont().Scale(1.5).Bold()
        username_label.SetFont(font)

        # commented ago label
        commented_ago_label = wx.StaticText(self, label=comment.created_at)
        commented_ago_label.SetForegroundColour((100, 100, 100))

        # username and date
        username_date_sizer = wx.BoxSizer(wx.HORIZONTAL)
        username_date_sizer.Add(username_label)
        username_date_sizer.Add(commented_ago_label, 0, wx.ALIGN_CENTER_VERTICAL)

        # comment label
        comment_label = wx.StaticText(self, label=comment.comment)
        font = comment_label.GetFont().Scale(1.5)
        comment_label.SetFont(font)

        # add to right size
        right_sizer.Add(username_date_sizer)
        right_sizer.Add(comment_label)

        # add to seperator sizer
        separator_sizer.Add(pfp, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 10)
        separator_sizer.Add(right_sizer, 1)

        # add to main sizer
        main_sizer.Add((0, 20))
        main_sizer.Add(separator_sizer, 0, wx.EXPAND)
        main_sizer.Add((0, 20))


        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_check_hover, self.timer)
        self.timer.Start(100)  # Check every 100ms

    def on_check_hover(self, event):
        # Get the mouse position relative to the screen
        mouse_pos = wx.GetMousePosition()

        # Get the window's rectangle area on the screen
        window_rect = self.GetScreenRect()

        # Check if the mouse is inside that rectangle
        is_inside_now = window_rect.Contains(mouse_pos)

        if is_inside_now and not self.is_hovered:
            self.is_hovered = True
            self.SetBackgroundColour(self.HOVER_COLOR)
            self.Refresh()

        elif not is_inside_now and self.is_hovered:
            self.is_hovered = False
            self.SetBackgroundColour(self.BG_COLOR)
            self.Refresh()
