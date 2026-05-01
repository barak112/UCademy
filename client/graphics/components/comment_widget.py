import os.path
from datetime import datetime

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
        self.username_label = wx.TextCtrl(self, value=comment.commenter, style=wx.TE_READONLY | wx.BORDER_NONE)
        self.username_label.SetBackgroundColour(self.BG_COLOR)
        font = self.username_label.GetFont().Scale(2).Bold()
        self.username_label.SetFont(font)

        w, h = self.username_label.GetTextExtent(self.username_label.GetValue())
        self.username_label.SetMinSize((w+14, h))  # +4 for padding
        self.username_label.SetCanFocus(False)

        # commented ago label
        self.commented_ago_label = wx.StaticText(self)
        self.date_to_ago()

        self.commented_ago_label.SetForegroundColour((100, 100, 100))

        # username and date
        username_date_sizer = wx.BoxSizer(wx.HORIZONTAL)
        username_date_sizer.Add(self.username_label, 0, wx.ALIGN_CENTER_VERTICAL)
        username_date_sizer.Add(self.commented_ago_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.LEFT, 5)

        # comment label
        self.comment_label = wx.TextCtrl(self, value=comment.comment, style=wx.TE_READONLY | wx.BORDER_NONE)
        self.comment_label.SetBackgroundColour(self.BG_COLOR)
        font = self.comment_label.GetFont().Scale(1.5)
        self.comment_label.SetFont(font)
        self.comment_label.SetCanFocus(False)


        # add to right size
        right_sizer.Add(username_date_sizer)
        right_sizer.Add(self.comment_label, 0, wx.EXPAND)

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
            self.comment_label.SetBackgroundColour(self.HOVER_COLOR)
            self.username_label.SetBackgroundColour(self.HOVER_COLOR)
            self.Refresh()

        elif not is_inside_now and self.is_hovered:
            self.is_hovered = False
            self.SetBackgroundColour(self.BG_COLOR)
            self.comment_label.SetBackgroundColour(self.BG_COLOR)
            self.username_label.SetBackgroundColour(self.BG_COLOR)
            self.Refresh()
        event.Skip()

    def date_to_ago(self):
        created_at = self.comment.created_at
        print("created at:", created_at)
        created_at = datetime.strptime(created_at, "%d/%m/%Y %H:%M")

        now = datetime.now()
        diff = now - created_at

        seconds = diff.total_seconds()

        minutes = seconds / 60
        hours = minutes / 60
        days = hours / 24
        weeks = days / 7
        months = days / 30
        years = days / 365


        if seconds < 60:
            ago_str =  "just now"

        elif minutes < 60:
            ago_str = f"{int(minutes)} minutes ago"

        elif hours < 24:
            ago_str = f"{int(hours)} hours ago"

        elif days < 7:
            ago_str = f"{int(days)} days ago"

        elif weeks < 4:
            ago_str = f"{int(weeks)} weeks ago"

        elif months < 12:
            ago_str = f"{int(months)} months ago"
        else:
            ago_str = f"{int(years)} years ago"

        self.commented_ago_label.SetLabel(ago_str)
