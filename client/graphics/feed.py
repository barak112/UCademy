import os.path

import wx
import wx.media
from pubsub import pub

import clientProtocol
import rounded_button
import settings
import comments


class Feed(wx.Panel):
    BG_COLOR = (232, 239, 255)

    def __init__(self, frame, parent):
        super().__init__(parent)

        self.frame = frame
        self.parent = parent
        self.is_playing = False
        self.is_muted = False

        self.scroll_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_scroll_timer, self.scroll_timer)

        self.can_scroll = True

        self.current_video_id = None  # video_id

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.SetBackgroundColour(self.BG_COLOR)

        # video
        video_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.video_ctrl = wx.media.MediaCtrl(self, style=wx.SIMPLE_BORDER, szBackend=wx.media.MEDIABACKEND_WMP10)
        self.video_ctrl.Bind(wx.media.EVT_MEDIA_LOADED, self.on_load)
        self.video_ctrl.SetVolume(0)

        # self.video.Play()
        # video_size = (int(self.GetClientSize()[0]), int(self.GetClientSize()[0] * (9 / 16)))
        # video_size = (int(self.GetClientSize()[1] * (9 / 16)), self.GetClientSize()[1])
        # self.video.SetInitialSize(video_size)
        # self.video.SetInitialSize((90, 160))
        # self.video.SetMinSize(video_size)

        # video
        video_sizer.Add(self.video_ctrl, 1, wx.EXPAND)

        # actions
        actions_sizer = wx.BoxSizer(wx.VERTICAL)
        video_sizer.Add(actions_sizer, 0, wx.ALIGN_CENTER_VERTICAL)

        # like
        like_sizer = wx.BoxSizer(wx.VERTICAL)
        img_path = "assets\\like_icon.png"
        self.like_btn = rounded_button.RoundedButton(self, img_path, wx.WHITE,
                                                     self.BG_COLOR, circle=True,use_image=True)
        self.like_btn.SetMinSize((50,50))
        self.likes_amount_label = wx.StaticText(self)

        like_sizer.Add(self.like_btn)
        like_sizer.Add(self.likes_amount_label, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # open_comments
        open_comments_sizer = wx.BoxSizer(wx.VERTICAL)

        img_path = "assets\\open_comments_icon.png"
        self.open_comments_btn = rounded_button.RoundedButton(self, img_path, wx.WHITE,
                                                     self.BG_COLOR, circle=True, use_image=True)
        self.open_comments_btn.SetMinSize((50, 50))
        self.comments_amount_label = wx.StaticText(self)

        open_comments_sizer.Add(self.open_comments_btn)
        open_comments_sizer.Add(self.comments_amount_label, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # report
        report_sizer = wx.BoxSizer(wx.VERTICAL)
        img_path = "assets\\report_icon.png"
        self.report_btn = rounded_button.RoundedButton(self, img_path, wx.WHITE,
                                                       self.BG_COLOR, circle=True, use_image=True)
        self.report_btn.SetMinSize((50, 50))
        report_label = wx.StaticText(self, label="report")

        report_sizer.Add(self.report_btn)
        report_sizer.Add(report_label, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # account
        account_sizer = wx.BoxSizer(wx.VERTICAL)

        img_path = "assets\\null_pfp.png"

        self.account_btn = wx.StaticBitmap(self, bitmap=wx.Bitmap(img_path))

        self.account_label = wx.StaticText(self)

        account_sizer.Add(self.account_btn)
        account_sizer.Add(self.account_label, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # add to actions sizer
        actions_sizer.Add(like_sizer)
        actions_sizer.Add(open_comments_sizer)
        actions_sizer.Add(report_sizer)
        actions_sizer.Add(account_sizer)


        # comments
        # comments_sizer = wx.BoxSizer(wx.VERTICAL)
        self.comments_panel = comments.Comments(frame, self)
        self.comments_panel.SetMinSize((400, 0))

        padding_sizer = wx.BoxSizer(wx.HORIZONTAL)

        padding_sizer.AddStretchSpacer()
        padding_sizer.AddSpacer(10)
        padding_sizer.Add(self.comments_panel, 10, wx.EXPAND | wx.RIGHT, 50) # top, right, bottom, left borders

        padding_sizer.Add(video_sizer, 10, wx.EXPAND)
        padding_sizer.AddSpacer(10)
        padding_sizer.AddStretchSpacer()

        main_sizer.AddSpacer(50)
        main_sizer.Add(padding_sizer, 1 , wx.EXPAND)
        main_sizer.AddSpacer(50)

        # btn = wx.Button(self, label="Play/Pause")
        # main_sizer.Add(btn, 0, wx.ALIGN_CENTER_VERTICAL)
        # btn.Bind(wx.EVT_BUTTON, self.on_play)
        self.SetSizer(main_sizer)

        pub.subscribe(self.load_new_video, "load_video")

        pub.subscribe(self.load_new_comments, "load_new_comments")

        pub.subscribe(self.on_like_video_ans, "video_like_ans")

        self.Bind(wx.EVT_MOUSEWHEEL, self.on_scroll)
        self.like_btn.Bind(wx.EVT_KEY_DOWN, self.on_like_video)
        self.open_comments_btn.Bind(wx.EVT_LEFT_DOWN, self.on_open_comments)

        self.Hide()

    def on_open_comments(self, event):
        if self.comments_panel.IsShown():
            self.comments_panel.Hide()
        else:
            self.comments_panel.Show()
        self.Layout()
        self.Refresh()
        self.Update()
        event.Skip()

    def on_like_video(self, event):
        #todo send to comm and wait for response
        print("liking video")

        msg = clientProtocol.build_

    def on_like_video_ans(self):
        if self.frame.videos_details[self.current_video_id].liked:
            self.likes_amount_label -= 1
        else:
            self.likes_amount_label += 1

    def on_scroll_timer(self, event):
        self.can_scroll = True
        self.scroll_timer.Stop()

    def on_scroll(self, event):
        rotation = event.GetWheelRotation()
        print(self.can_scroll)
        if self.can_scroll:
            self.can_scroll = False
            self.scroll_timer.Start(300)

            if rotation > 0:
                # return to last video
                if self.frame.video_index > 0:
                    self.frame.video_index -=1
                    #loads previous video, find the id of the last video using its index and than gets its video object
                    self.load_video(self.frame.videos_details[self.frame.videos_ids_with_file[self.frame.video_index]])
                    # print(self.frame.video_index, self.frame.videos_ids_with_file)
            else:

                if len(self.frame.videos_ids_with_file)>self.frame.video_index + 1:
                    self.frame.video_index += 1
                    print("going back", self.frame.video_index)
                    self.load_video(self.frame.videos_details[self.frame.videos_ids_with_file[self.frame.video_index]])
                else:
                    msg = clientProtocol.build_req_video()
                    self.frame.comm.send_msg(msg)
                    print("req")

        event.Skip()

    def on_load(self, event):
        self.video_ctrl.Play()

    def on_play(self, event):
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.video_ctrl.Play()
        else:
            self.video_ctrl.Pause()

    def mute(self, event):
        self.is_muted = not self.is_muted
        if self.is_muted:
            self.video_ctrl.SetVolume(0)
        else:
            self.video_ctrl.SetVolume(1)

    def load_new_video(self, video):
        video_id = video.video_id

        if video_id:
            self.frame.videos_details[video_id] = video

            self.frame.videos_ids_with_file.append(video_id)

            self.frame.video_index += 1
            self.load_video(video)
        else:
            self.frame.change_text_status("watched all videos")
            print("watched all videos")

    def load_video(self, video):
        video_id = video.video_id
        if video_id:
            self.current_video_id = video_id

            self.video_ctrl.Load(f"media\\{video_id}.mp4")
            self.video_ctrl.SetInitialSize((500, 500)) #todo do i really need?
            self.comments_panel.set_video(video)
            self.frame.change_text_status("")
            #load actions
            self.likes_amount_label.SetLabel(video.amount_of_likes)
            self.comments_amount_label.SetLabel(video.amount_of_comments)

            pfp_path = f"media\\{video.creator}.png"
            null_pfp_path = f"assets\\null_pfp.png"
            if os.path.isfile(pfp_path):
                self.account_btn.SetBitmap(wx.Bitmap(wx.Image(pfp_path).Scale(48,48)))
            else:
                self.account_btn.SetBitmap(wx.Bitmap(null_pfp_path))

            self.account_label.SetLabel(video.creator)

            self.Layout()

    def load_new_comments(self, video_id, comments):
        self.frame.videos_details[video_id].add_comments(comments)
        self.comments_panel.add_comments(comments)



# three parts: comments, video, video desc + video name.


if __name__ == "__main__":
    app = wx.App()
    frame = wx.Frame(None)
    frame.SetSize((800, 600))
    panel = Feed(frame, frame)
    frame.Show()
    app.MainLoop()
