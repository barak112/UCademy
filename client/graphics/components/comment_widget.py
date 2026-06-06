import os.path
from datetime import datetime

import wx

import clientProtocol
import rounded_button
import settings


class CommentWidget(wx.Panel):
    BG_COLOR = settings.OFF_WHITE
    HOVER_COLOR = (220, 220, 220)

    def __init__(self, parent, frame, comment):
        """
        Initializes the CommentWidget, building the UI with the commenter's profile picture,
        username, timestamp, and comment text.
        :param parent: The parent wx window this widget belongs to.
        :param comment: A comment object containing commenter, comment, and created_at fields.
        """
        super().__init__(parent)

        self.is_hovered = False
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(main_sizer)

        separator_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.comment = comment
        self.parent = parent
        self.frame = frame

        pfp_path = f"media\\{comment.commenter}.png"
        if not os.path.isfile(pfp_path):
            pfp_path = "assets\\null_pfp.png"

        self.pfp = wx.Bitmap(wx.Image(pfp_path).Scale(settings.PFP_SIZE, settings.PFP_SIZE))
        self.pfp = wx.StaticBitmap(self, bitmap=self.pfp)
        self.pfp.SetCursor(wx.Cursor(wx.CURSOR_HAND))

        # right sizer
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        # username label
        self.username_label = wx.TextCtrl(self, value=comment.commenter, style=wx.TE_READONLY | wx.BORDER_NONE)
        self.username_label.SetBackgroundColour(self.BG_COLOR)
        font = self.username_label.GetFont().Scale(2).Bold()
        self.username_label.SetFont(font)

        w, h = self.username_label.GetTextExtent(self.username_label.GetValue())
        self.username_label.SetMinSize((w + 14, h))
        self.username_label.SetCanFocus(False)

        # commented ago label
        self.commented_ago_label = wx.StaticText(self)
        self.date_to_ago()

        self.commented_ago_label.SetForegroundColour((100, 100, 100))

        # action_button
        img_path = "assets\\report_icon.png"
        if self.parent.GetParent().frame.user.is_system_manager():
            img_path = "assets\\moderate.png"

        elif self.parent.GetParent().frame.user.username == self.comment.commenter:
            img_path = "assets\\delete_video_icon.png"

        self.action_button = rounded_button.RoundedButton(self, img_path, wx.WHITE, self.BG_COLOR, circle=True, use_image=True, icon_size=24)

        self.action_button.SetMinSize((32, 32))

        # username and date
        username_date_sizer = wx.BoxSizer(wx.HORIZONTAL)
        username_date_sizer.Add(self.username_label, 0, wx.ALIGN_CENTER_VERTICAL)
        username_date_sizer.Add(self.commented_ago_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.LEFT, 5)
        username_date_sizer.Add(self.action_button, 0, wx.ALIGN_CENTER_VERTICAL | wx.TOP | wx.LEFT, 5)

        # comment label
        self.comment_label = wx.TextCtrl(self, value=comment.comment, style=wx.TE_READONLY | wx.BORDER_NONE)
        self.comment_label.SetBackgroundColour(self.BG_COLOR)
        font = self.comment_label.GetFont().Scale(1.5)
        self.comment_label.SetFont(font)
        self.comment_label.SetCanFocus(False)

        # add to right sizer
        right_sizer.Add(username_date_sizer)
        right_sizer.Add(self.comment_label, 0, wx.EXPAND)

        # add to separator sizer
        separator_sizer.Add(self.pfp, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 10)
        separator_sizer.Add(right_sizer, 1)

        # add to main sizer
        main_sizer.Add((0, 20))
        main_sizer.Add(separator_sizer, 0, wx.EXPAND)
        main_sizer.Add((0, 20))

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_check_hover, self.timer)
        self.timer.Start(100)

        self.pfp.Bind(wx.EVT_LEFT_UP, self.move_to_commenter_profile)
        self.action_button.Bind(wx.EVT_LEFT_UP, self.on_comment_action)

    def on_comment_action(self, event):
        print("comment action")
        msg = ""
        if self.frame.user.is_system_manager(): # if system manager moderating comment
            answer = wx.MessageBox(
                "Would you like to delete this comment?\nThis action is not reversable\nClick Yes to delete\nClick No to keep\nClick cancel to avoid moderating this comment",
                "Moderate Comment", wx.ICON_INFORMATION | wx.YES_NO | wx.CANCEL)

            if answer != wx.CANCEL:
                status = settings.REPORT_ACCEPTED if answer == wx.YES else settings.REPORT_DENIED

                msg = clientProtocol.build_comment_or_video_status(self.comment.comment_id, settings.COMMENT_DIGIT_REPR,status)
                self.parent.GetParent().parent.status_label.SetLabel("Moderation sent to the server")
                self.parent.GetParent().parent.Layout()
                wx.MessageBox("Moderation has been sent to the server", "Moderation sent",wx.OK | wx.ICON_INFORMATION)

        elif self.parent.GetParent().frame.user.username == self.comment.commenter: # if commenter deleting comment
            answer = wx.MessageBox(
                "Are you sure you want to delete this comment?\nThis action is not reverseable\n",
                "Delete Comment", wx.ICON_INFORMATION | wx.YES_NO)

            if answer == wx.YES:
                msg = clientProtocol.build_del_comment(self.comment.comment_id)
                self.parent.GetParent().parent.status_label.SetLabel("Delete req sent to the server")
                self.parent.GetParent().parent.Layout()

                wx.MessageBox("Delete req has been sent to the server", "Delete req sent", wx.OK | wx.ICON_INFORMATION)

        else: # if a user reporting comment
            answer = wx.MessageBox(
                "Are you sure you want to report this comment?\nReport this comment only if its content is harmful\n",
                f'Report comment "{self.comment.comment}"?',
                wx.YES_NO | wx.ICON_INFORMATION,
            )

            if answer == wx.YES:
                self.parent.GetParent().parent.status_label.SetLabel("Report req sent to the server")
                self.parent.GetParent().parent.Layout()

                wx.MessageBox("Your report has been sent to the server", "Report Sent", wx.OK | wx.ICON_INFORMATION)
                msg = clientProtocol.build_report(self.comment.comment_id, settings.COMMENT_DIGIT_REPR)


        if msg:
            self.frame.comm.send_msg(msg)

        event.Skip()

    def move_to_commenter_profile(self, event):
        self.parent.GetParent().frame.user_profile_panel.set_new_user(self.comment.commenter)
        self.parent.GetParent().frame.switch_panel(self.parent.GetParent().frame.user_profile_panel, self.parent.GetParent().parent)
        event.Skip()

    def on_check_hover(self, event):
        """
        Periodically checks whether the mouse is hovering over this widget and updates
        the background color of the panel and its text controls accordingly.
        :param event: The wx timer event fired every 100ms.
        """
        mouse_pos = wx.GetMousePosition()
        window_rect = self.GetScreenRect()
        is_inside_now = window_rect.Contains(mouse_pos)

        if is_inside_now and not self.is_hovered:
            self.is_hovered = True
            self.SetBackgroundColour(self.HOVER_COLOR)
            self.comment_label.SetBackgroundColour(self.HOVER_COLOR)
            self.username_label.SetBackgroundColour(self.HOVER_COLOR)
            self.action_button.SetBackgroundColour(self.HOVER_COLOR)
            self.action_button.current_color = wx.Colour(self.HOVER_COLOR)
            self.Refresh()

        elif not is_inside_now and self.is_hovered:
            self.is_hovered = False
            self.SetBackgroundColour(self.BG_COLOR)
            self.comment_label.SetBackgroundColour(self.BG_COLOR)
            self.username_label.SetBackgroundColour(self.BG_COLOR)
            self.action_button.SetBackgroundColour(self.BG_COLOR)
            self.action_button.current_color = wx.WHITE

            self.Refresh()
        event.Skip()

    def date_to_ago(self):
        """
        Converts the comment's creation timestamp into a human-readable relative time string
        (e.g. "3 hours ago") and updates the commented_ago_label with it.
        """
        created_at = self.comment.created_at
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
            ago_str = "just now"
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
