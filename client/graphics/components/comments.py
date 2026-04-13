import math
import os

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
        super().__init__(parent)

        self.frame = frame

        self.video = None

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.SetBackgroundColour(self.BG_COLOR)

        self.comments = {} # video comments [comment_id] = comment object

        # comments label
        comments_label = wx.StaticText(self, label="Comments")
        font = comments_label.GetFont().Scale(1.5).Bold()
        comments_label.SetFont(font)

        # comments amount label
        comments_amount_label = wx.StaticText(self, label=f"{len(self.comments)} comments")
        comments_amount_label.SetForegroundColour((100, 100, 100))
        font = comments_amount_label.GetFont().Scale(1.3)
        comments_amount_label.SetFont(font)

        #comments
        self.comments_panel = wx.ScrolledWindow(self)
        self.comments_panel.SetScrollRate(0, 7)

        self.comments_sizer = wx.BoxSizer(wx.VERTICAL)
        self.comments_panel.SetSizer(self.comments_sizer)

        # add comment
        add_comment_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # pfp_path = f"..\\media\\{self.frame.user.username}.png"
        # pfp_path = f"..\\..\\media\\user1.png"
        # if not os.path.isfile(pfp_path):
        #     pfp_path = "..\\..\\assets\\null_pfp.png"

        pfp_path = f"media/Barak.png"
        if not os.path.isfile(pfp_path):
            pfp_path = "assets\\null_pfp.png"

        pfp = wx.Bitmap(wx.Image(pfp_path).Scale(settings.PFP_SIZE, settings.PFP_SIZE))
        pfp = wx.StaticBitmap(self, bitmap=pfp)

        self.add_comment_field = rounded_input_field.RoundedInputField(self, self, "Add a comment", "Add a comment...")
        self.add_comment_field.SetMinSize((0,50))

        add_comment_img_path = "assets\\send.png"
        self.add_comment_button = rounded_button.RoundedButton(self, add_comment_img_path,
                        settings.UNACTIVE_BUTTON, self.BG_COLOR, circle=True, use_image=True)
        self.add_comment_button.SetMinSize((50,50))
        self.add_comment_button.Bind(wx.EVT_LEFT_UP, self.on_add_comment)

        add_comment_sizer.Add(pfp, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)
        add_comment_sizer.Add(self.add_comment_field, 1, wx.ALIGN_CENTER_VERTICAL)
        add_comment_sizer.Add(self.add_comment_button, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)


        main_sizer.Add(comments_label, 0, wx.LEFT, 20)
        main_sizer.Add((0, 5))
        main_sizer.Add(comments_amount_label, 0, wx.LEFT, 20)
        main_sizer.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10)
        main_sizer.Add(self.comments_panel, 1, wx.EXPAND)
        main_sizer.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10)
        main_sizer.Add(add_comment_sizer, 0, wx.EXPAND)

        self.SetSizer(main_sizer)

        pub.subscribe(self.on_add_comment_ans, "added_comment")
        self.add_comment_field.get_text_visible().Bind(wx.EVT_TEXT_ENTER, self.on_enter)

        self.call_date_to_ago_timer = wx.Timer()
        self.Bind(wx.EVT_TIMER, self.call_date_to_ago, self.call_date_to_ago_timer)
        self.call_date_to_ago_timer.Start(1000*60) # every minute

    def call_date_to_ago(self, event):
        for a_comment in self.comments_sizer.GetChildren():
            a_comment.date_to_ago()

    def on_enter(self, event):
        self.on_add_comment(None)
        event.Skip()

    def field_is_filled(self, field_name):
        self.add_comment_button.set_active(True)

    def field_is_unfilled(self, field_name):
        self.add_comment_button.set_active(False)

    def on_add_comment(self, event):
        comment = self.add_comment_field.get_value()
        if comment and self.video:
            msg = clientProtocol.build_comment(self.video.video_id, comment)
            self.frame.comm.send_msg(msg)
            print("sending comment:",comment)
            self.add_comment_field.set_value("")


    def on_add_comment_ans(self, video_id, comment):
        print(self.frame.videos_details)
        self.frame.videos_details[video_id].add_comment_at_start(comment)

        if self.video.video_id == video_id:
            # add comment visually
            comment_panel = comment_widget.CommentWidget(self.comments_panel, comment)
            self.comments_sizer.Insert(0, comment_panel, 0, wx.EXPAND)
            self.Layout()
            print("added comment ")

    def add_comments(self, comments):
        for a_comment in comments:
            comment_panel = comment_widget.CommentWidget(self.comments_panel, a_comment)
            self.comments_sizer.Add(comment_panel, 0, wx.EXPAND)
        self.Layout()

    def set_video(self, video):
        self.video = video
        self.comments_sizer.Clear(True) # clears prev comments
        self.add_comments(video.get_comments()) # if comments already exist with the video (the video already existed)
        self.Layout()
    
if __name__ == "__main__":
    app = wx.App()
    frame = wx.Frame(None)
    frame.SetSize((800, 600))
    panel = Comments(frame, frame)
    frame.Show()
    app.MainLoop()
