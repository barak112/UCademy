import math
import os

import wx
import wx.media
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

        self.comments = [] # video comments
        self.comments.append(comment.Comment(0, "This is a comment", "user1", "15:10"))
        self.comments.append(comment.Comment(0, "This is a comment 2", "user 2", "18:10"))
        self.comments.append(comment.Comment(0, "This is a comment 3", "user3", "15:10"))
        self.comments.append(comment.Comment(0, "This is a comment 4", "user 4", "18:10"))

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
        comments_panel = wx.ScrolledWindow(self)
        comments_panel.SetScrollRate(0, 7)

        comments_sizer = wx.BoxSizer(wx.VERTICAL)
        comments_panel.SetSizer(comments_sizer)

        for a_comment in self.comments:
            comment_panel = comment_widget.CommentWidget(comments_panel, a_comment)
            comments_sizer.Add(comment_panel, 0, wx.EXPAND)


        # add comment
        add_comment_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # pfp_path = f"..\\media\\{self.frame.user.username}.png"
        # pfp_path = f"..\\..\\media\\user1.png"
        # if not os.path.isfile(pfp_path):
        #     pfp_path = "..\\..\\assets\\null_pfp.png"

        pfp_path = f"media\\user1.png"
        if not os.path.isfile(pfp_path):
            pfp_path = "assets\\null_pfp.png"

        pfp = wx.Bitmap(wx.Image(pfp_path).Scale(settings.PFP_SIZE, settings.PFP_SIZE))
        pfp = wx.StaticBitmap(self, bitmap=pfp)

        self.add_comment_field = rounded_input_field.RoundedInputField(self, self, "Add a comment", "Add a comment...")
        self.add_comment_field.SetMinSize((0,50))

        add_comment_img_path = "assets\\send.png"
        self.add_comment_button = rounded_button.RoundedButton(self, add_comment_img_path, settings.UNACTIVE_BUTTON, self.BG_COLOR, circle=True, use_image=True)
        self.add_comment_button.SetMinSize((50,50))

        add_comment_sizer.Add(pfp, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)
        add_comment_sizer.Add(self.add_comment_field, 1, wx.ALIGN_CENTER_VERTICAL)
        add_comment_sizer.Add(self.add_comment_button, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)


        main_sizer.Add(comments_label, 0, wx.LEFT, 20)
        main_sizer.Add((0, 5))
        main_sizer.Add(comments_amount_label, 0, wx.LEFT, 20)
        main_sizer.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10)
        main_sizer.Add(comments_panel, 1, wx.EXPAND)
        main_sizer.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10)
        main_sizer.Add(add_comment_sizer, 0, wx.EXPAND)

        self.SetSizer(main_sizer)

    def field_is_filled(self, field_name):
        self.add_comment_button.set_active(True)

    def field_is_unfilled(self, field_name):
        self.add_comment_button.set_active(False)

    def on_add_comment(self, event):
        #todo add comment to server
        comment = self.add_comment_field.get_value()
        if comment and self.video:
            msg = clientProtocol.build_comment(self.video.video_id, comment)
            self.frame.comm.send_msg(msg)

    def on_add_comment_ans(self, comment):
        self.comments.insert(0,comment)

    def set_video(self, video):
        self.video = video
        self.comments = video.get_comments()

if __name__ == "__main__":
    app = wx.App()
    frame = wx.Frame(None)
    frame.SetSize((800, 600))
    panel = Comments(frame, frame)
    frame.Show()
    app.MainLoop()
