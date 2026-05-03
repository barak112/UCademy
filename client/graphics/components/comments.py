import math
import os
import threading

import wx
import wx.media
from pubsub import pub

import clientProtocol
import comment
import comment_widget
import rounded_button
import rounded_input_field
import settings


class Comments(wx.Panel):
    BG_COLOR = settings.OFF_WHITE

    def __init__(self, frame, parent):
        """
        Initializes the Comments panel with a scrollable comments list, an add-comment input field, and a periodic timer to update relative timestamps.
        :param frame: The main application frame.
        :param parent: The parent feed panel this comments section belongs to.
        """
        super().__init__(parent)

        self.parent = parent
        self.frame = frame

        self.video = None

        self.comments_ids = []

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.SetBackgroundColour(self.BG_COLOR)

        self.comments = {}  # video comments [comment_id] = comment object

        # comments label
        comments_label = wx.StaticText(self, label="Comments")
        font = comments_label.GetFont().Scale(1.5).Bold()
        comments_label.SetFont(font)

        # comments amount label
        self.comments_amount_label = wx.StaticText(self)
        self.comments_amount_label.SetForegroundColour((100, 100, 100))
        font = self.comments_amount_label.GetFont().Scale(1.3)
        self.comments_amount_label.SetFont(font)

        # comments
        self.comments_panel = wx.ScrolledWindow(self)
        self.comments_panel.SetScrollRate(0, 12)

        self.comments_sizer = wx.BoxSizer(wx.VERTICAL)
        self.comments_panel.SetSizer(self.comments_sizer)

        # add comment
        add_comment_sizer = wx.BoxSizer(wx.HORIZONTAL)

        pfp_path = "assets\\null_pfp.png"
        pfp = wx.Bitmap(wx.Image(pfp_path).Scale(settings.PFP_SIZE, settings.PFP_SIZE))
        self.pfp = wx.StaticBitmap(self, bitmap=pfp)

        # todo make this multiline
        self.add_comment_field = rounded_input_field.RoundedInputField(self, self, "Add a comment", "Add a comment...")
        self.add_comment_field.SetMinSize((0, 50))

        add_comment_img_path = "assets\\send.png"
        self.add_comment_button = rounded_button.RoundedButton(self, add_comment_img_path,
                                                               settings.UNACTIVE_BUTTON, self.BG_COLOR, circle=True,
                                                               use_image=True)
        self.add_comment_button.SetMinSize((50, 50))
        self.add_comment_button.Bind(wx.EVT_LEFT_UP, self.on_add_comment)

        add_comment_sizer.Add(self.pfp, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)
        add_comment_sizer.Add(self.add_comment_field, 1, wx.ALIGN_CENTER_VERTICAL)
        add_comment_sizer.Add(self.add_comment_button, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)

        main_sizer.Add(comments_label, 0, wx.LEFT, 20)
        main_sizer.Add((0, 5))
        main_sizer.Add(self.comments_amount_label, 0, wx.LEFT, 20)
        main_sizer.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10)
        main_sizer.Add(self.comments_panel, 1, wx.EXPAND)
        main_sizer.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10)
        main_sizer.Add(add_comment_sizer, 0, wx.EXPAND)

        self.SetSizer(main_sizer)

        self.add_comment_field.get_text_visible().Bind(wx.EVT_TEXT_ENTER, self.on_enter)

        self.call_date_to_ago_timer = wx.Timer()
        self.Bind(wx.EVT_TIMER, self.call_date_to_ago, self.call_date_to_ago_timer)
        self.call_date_to_ago_timer.Start(1000 * 60)  # every minute
        self.comments_panel.Bind(wx.EVT_SCROLLWIN, self.on_scroll)
        self.waiting_for_comments = False

    def on_scroll(self, event):
        """
        Handles scroll events on the comments panel to request more comments from the server when the user nears the bottom.
        :param event: The wx scroll event.
        """
        event_type = event.GetEventType()

        scrolling_down = event_type in (wx.wxEVT_SCROLLWIN_LINEDOWN, wx.wxEVT_SCROLLWIN_PAGEDOWN,
                                        wx.wxEVT_SCROLLWIN_THUMBTRACK)

        if scrolling_down:
            current = self.comments_panel.GetScrollPos(wx.VERTICAL)
            max_pos = self.comments_panel.GetScrollRange(wx.VERTICAL) - self.comments_panel.GetScrollThumb(wx.VERTICAL)
            if self.video.amount_of_comments > len(self.video.get_comments()) and self.video.get_comments():
                if not self.waiting_for_comments:  # if there are more comments to req from the server
                    if current >= max_pos - 40:
                        msg = clientProtocol.build_req_comments(self.video.video_id,
                                                                self.video.get_comments()[-1].comment_id)
                        self.frame.comm.send_msg(msg)
                        self.frame.comments_requests_by_feeds.append(self.parent)
                        self.waiting_for_comments = True
                        self.parent.status_label.SetLabel("waiting for comments from server...")
                        self.parent.Layout()

            elif current >= max_pos:
                self.parent.status_label.SetLabel("no more comments to load")
                self.parent.Layout()
        else:
            self.parent.status_label.SetLabel("")
        # todo separate status bar
        event.Skip()

    def update_pfp_bitmap(self):
        """
        Reloads and updates the current user's profile picture bitmap in the add-comment area.
        """
        user = self.frame.user
        if user:
            pfp_path = f"media\\{user.username}.png"
            if os.path.isfile(pfp_path):
                pfp = wx.Bitmap(wx.Image(pfp_path).Scale(settings.PFP_SIZE, settings.PFP_SIZE))
                self.pfp.SetBitmap(pfp)
        print("updated pfp")

    def call_date_to_ago(self, event):
        """
        Timer callback that updates the relative timestamp display on all visible comment widgets.
        :param event: The wx timer event.
        """
        for a_comment in self.comments_sizer.GetChildren():
            a_comment.date_to_ago()
        event.Skip()

    def on_enter(self, event):
        """
        Submits the comment when the Enter key is pressed in the input field.
        :param event: The wx text enter event.
        """
        self.on_add_comment(None)
        event.Skip()

    def field_is_filled(self, field_name):
        """
        Activates the add-comment button when the comment input field has content.
        :param field_name: The name of the field that became filled.
        """
        self.add_comment_button.set_active(True)

    def field_is_unfilled(self, field_name):
        """
        Deactivates the add-comment button when the comment input field is empty.
        :param field_name: The name of the field that was cleared.
        """
        self.add_comment_button.set_active(False)

    def on_add_comment(self, event):
        """
        Reads the comment input field and sends the comment to the server if it is non-empty.
        :param event: The wx mouse click event, or None if triggered by Enter key.
        """
        comment = self.add_comment_field.get_value().strip()
        if comment and self.video:
            msg = clientProtocol.build_comment(self.video.video_id, comment)
            self.frame.comm.send_msg(msg)
            self.frame.comment_requests_by_feeds.append(self.parent)
            self.add_comment_field.set_value("")
        if event:
            event.Skip()

    def on_add_comment_ans(self, video_id, comment):
        """
        Handles the server's confirmation of an added comment and inserts it at the top of the comments list.
        :param video_id: The ID of the video the comment was added to.
        :param comment: The comment object returned by the server.
        """
        self.frame.videos_details[video_id].add_comment_at_start(comment)

        if self.video.video_id == video_id:
            # add comment visually
            comment_panel = comment_widget.CommentWidget(self.comments_panel, comment)

            self.comments_sizer.Insert(0, comment_panel, 0, wx.EXPAND)
            self.update_comments_label()
            self.parent.update_comments_label(video_id)
            self.Layout()

    def add_comments(self, comments):
        """
        Appends a batch of comment widgets to the comments panel.
        :param comments: A list of comment objects to display.
        """
        self.comments_panel.Freeze()

        for a_comment in comments:
            if a_comment.comment_id not in self.comments_ids:  # make sure there are no duplicate comments
                comment_panel = comment_widget.CommentWidget(self.comments_panel, a_comment)
                self.comments_sizer.Add(comment_panel, 0, wx.EXPAND)
                self.comments_ids.append(a_comment.comment_id)

        self.comments_panel.Thaw()
        self.parent.status_label.SetLabel("")

        self.waiting_for_comments = False
        self.Layout()
        self.comments_panel.FitInside()

    def set_video(self, video):
        """
        Loads a new video's comments into the panel, clearing any previously displayed comments.
        :param video: The video object whose comments should be displayed.
        """
        self.video = video
        self.comments_sizer.Clear(True)  # clears prev comments
        print("video_id in set_video:", video.video_id, "comments:", video.comments)

        self.add_comments(video.get_comments())  # if comments already exist with the video (the video already existed)

        self.update_comments_label()
        self.Layout()
        self.Refresh()
        self.comments_panel.Scroll(0, 0)

    def update_comments_label(self):
        """
        Updates the comments count label to reflect the current number of comments on the video.
        """
        # using self.frame... because the video here and the video in details is a different obj. only update the obj in
        # frame, so i am also using it when setting the label
        self.comments_amount_label.SetLabel(
            f"{self.frame.videos_details[self.video.video_id].amount_of_comments} comments")


if __name__ == "__main__":
    app = wx.App()
    frame = wx.Frame(None)
    frame.SetSize((800, 600))
    panel = Comments(frame, frame)
    frame.Show()
    app.MainLoop()
