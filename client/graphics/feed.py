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
        self.is_playing = True
        self.volume = 0

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
        video_sizer.Add(actions_sizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 20)

        # play/pause
        play_sizer = wx.BoxSizer(wx.VERTICAL)
        img_path = "assets\\pause.png"
        self.play_btn = rounded_button.RoundedButton(self, img_path, wx.WHITE,
                                                      self.BG_COLOR, circle=True, use_image=True)
        self.play_btn.SetMinSize((50, 50))
        self.play_label = wx.StaticText(self, label="pause")

        play_sizer.Add(self.play_btn)
        play_sizer.Add(self.play_label, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # sound/mute
        sound_sizer = wx.BoxSizer(wx.VERTICAL)
        img_path = "assets\\sound_off.png"
        self.sound_btn = rounded_button.RoundedButton(self, img_path, wx.WHITE,
                                                     self.BG_COLOR, circle=True, use_image=True)
        self.sound_btn.SetMinSize((50, 50))
        self.sound_label = wx.StaticText(self, label = "sound off")

        sound_sizer.Add(self.sound_btn)
        sound_sizer.Add(self.sound_label, 0, wx.ALIGN_CENTER_HORIZONTAL)


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
        actions_sizer.Add(play_sizer)
        actions_sizer.Add(sound_sizer, 0, wx.TOP, 10)
        actions_sizer.Add(like_sizer, 0, wx.TOP, 10)
        actions_sizer.Add(open_comments_sizer, 0, wx.TOP, 10)
        actions_sizer.Add(report_sizer, 0, wx.TOP, 10)
        actions_sizer.Add(account_sizer, 0, wx.TOP, 10)
        #todo add req test

        # comments
        # comments_sizer = wx.BoxSizer(wx.VERTICAL)
        self.comments_panel = comments.Comments(frame, self)
        self.comments_panel.SetMinSize((400, 0))

        # video description
        self.desc_panel = wx.Panel(self)

        self.video_name_label = wx.StaticText(self.desc_panel)
        font = self.video_name_label.GetFont()
        font = font.Scale(2).Bold()
        self.video_name_label.SetFont(font)

        self.desc_label = wx.StaticText(self.desc_panel)

        #padding sizer
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

        self.SetSizer(main_sizer)

        pub.subscribe(self.load_new_video, "load_video")

        pub.subscribe(self.load_new_comments, "load_new_comments")

        pub.subscribe(self.on_like_video_ans, "video_like_ans")


        self.Bind(wx.EVT_MOUSEWHEEL, self.on_scroll)
        self.like_btn.Bind(wx.EVT_LEFT_DOWN, self.on_like_video)
        self.open_comments_btn.Bind(wx.EVT_LEFT_DOWN, self.on_open_comments)
        self.sound_btn.Bind(wx.EVT_LEFT_DOWN, self.on_toggle_sound)
        self.play_btn.Bind(wx.EVT_LEFT_DOWN, self.on_toggle_play)

        self.Bind(wx.EVT_SIZE, self.on_resize)

        self.Hide()

    def Show(self, show = True):
        super().Show()
        self.comments_panel.update_pfp_bitmap()

    def on_resize(self, event):
        self.Layout()
        self.video_name_label.Wrap(self.desc_panel.GetSize()[0])
        self.Refresh()
        event.Skip()


    def on_toggle_sound(self, event):
        if self.volume:
            self.volume = 0
            self.sound_btn.label_or_path = "assets/sound_off.png"
            self.sound_label.SetLabel("sound off")
        else:
            self.volume = 1
            self.sound_btn.label_or_path = "assets\\sound_on.png"
            self.sound_label.SetLabel("sound on")

        self.video_ctrl.SetVolume(self.volume)

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
        print("liking video")
        if self.current_video_id:
            msg = clientProtocol.build_like_video(self.current_video_id)
            self.frame.comm.send_msg(msg)

    def on_like_video_ans(self, status, video_id):
        video = self.frame.videos_details[video_id]
        video.amount_of_likes += 1 if status else -1 # either + 1 or - 1
        video.liked = bool(status) # update liked

        if video_id == self.current_video_id:
            self.update_like_button(status)
            self.update_likes_amount_label(video_id)

        self.like_btn.Refresh()

    def update_like_button(self, is_liked):
        if is_liked:
            self.like_btn.label_or_path = "assets\\liked_icon.png"
        else:
            self.like_btn.label_or_path = "assets\\like_icon.png"

        self.like_btn.Refresh()

    def update_likes_amount_label(self, video_id):
        self.likes_amount_label.SetLabel(str(self.frame.videos_details[video_id].amount_of_likes))

    def on_scroll_timer(self, event):
        self.can_scroll = True
        self.scroll_timer.Stop()

    def on_scroll(self, event):
        rotation = event.GetWheelRotation()
        print(self.can_scroll)
        if self.can_scroll:
            self.can_scroll = False
            self.scroll_timer.Start(200)

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
        self.video_ctrl.SetVolume(self.volume)

    def on_toggle_play(self, event):
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.video_ctrl.Play()
            self.play_btn.label_or_path = "assets\\pause.png"
        else:
            self.video_ctrl.Pause()
            self.play_btn.label_or_path = "assets\\play2.png"

    def load_new_video(self, video):
        video_id = video.video_id
        #todo req ~6 videos and then each timer req another one, so never stuck
        #todo send pfps together with the video and in signup
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

            self.Layout()
            self.Refresh()
            self.Update()

            self.video_ctrl.Load(f"media\\{video_id}.mp4")
            self.video_ctrl.SetInitialSize((500, 500)) #todo do i really need?
            self.comments_panel.set_video(video)
            self.frame.change_text_status("")
            #load actions

            self.update_like_button(video.liked)
            self.update_likes_amount_label(video_id)
            self.update_comments_label(video_id)
            self.comments_panel.update_comments_label()

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
        self.update_comments_label(video_id)

    def update_comments_label(self, video_id):
        self.comments_amount_label.SetLabel(str(self.frame.videos_details[video_id].amount_of_comments))
        print("set label to", self.frame.videos_details[video_id].amount_of_comments)

# three parts: comments, video, video desc + video name.


if __name__ == "__main__":
    app = wx.App()
    frame = wx.Frame(None)
    frame.SetSize((800, 600))
    panel = Feed(frame, frame)
    frame.Show()
    app.MainLoop()
