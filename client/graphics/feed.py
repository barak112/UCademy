import os.path

import wx
import wx.media
from pubsub import pub

import clientProtocol
import rounded_button
import settings
import comments


class FeedPanel(wx.Panel):
    BG_COLOR = (232, 239, 255)

    def __init__(self, frame, parent, associated_panel = None):
        super().__init__(parent)

        self.frame = frame
        self.parent = parent

        self.associated_panel = associated_panel
        if not self.associated_panel:
            self.associated_panel = self

        self.is_playing = True
        self.volume = 0

        self.scroll_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_scroll_timer, self.scroll_timer)

        self.video_index = 0

        self.waiting_for_video = True

        self.videos_ids = []

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

        # personal account
        personal_account_sizer = wx.BoxSizer(wx.VERTICAL)
        img_path = "assets\\null_pfp.png"
        self.personal_account_btn = wx.StaticBitmap(self, bitmap=wx.Bitmap(img_path))
        self.personal_account_btn.SetCursor(wx.Cursor(wx.CURSOR_HAND))

        self.personal_account_btn.Bind(wx.EVT_LEFT_UP, self.on_personal_account)
        self.personal_account_label = wx.StaticText(self, label="Profile")

        personal_account_sizer.Add(self.personal_account_btn)
        personal_account_sizer.Add(self.personal_account_label, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # search
        search_sizer = wx.BoxSizer(wx.VERTICAL)
        img_path = "assets\\search.png"
        self.search_btn = rounded_button.RoundedButton(self, img_path, wx.WHITE,
                                                     self.BG_COLOR, circle=True, use_image=True)
        self.search_btn.SetMinSize((50, 50))
        self.search_label = wx.StaticText(self, label="search")

        search_sizer.Add(self.search_btn)
        search_sizer.Add(self.search_label, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # play/pause
        play_sizer = wx.BoxSizer(wx.VERTICAL)
        img_path = "assets\\pause.png"
        self.play_btn = rounded_button.RoundedButton(self, img_path, wx.WHITE,
                                                      self.BG_COLOR, circle=True, use_image=True)
        self.play_btn.SetMinSize((50, 50))
        self.play_label = wx.StaticText(self, label="pause")

        play_sizer.Add(self.play_btn)
        play_sizer.Add(self.play_label, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.play_sizer = play_sizer

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

        # open test
        test_sizer = wx.BoxSizer(wx.VERTICAL)

        img_path = "assets\\test.png"
        self.test_btn = rounded_button.RoundedButton(self, img_path, wx.WHITE,
                                                              self.BG_COLOR, circle=True, use_image=True)
        self.test_btn.SetMinSize((50, 50))
        self.test_label = wx.StaticText(self, label="test")

        test_sizer.Add(self.test_btn)
        test_sizer.Add(self.test_label, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # report
        report_sizer = wx.BoxSizer(wx.VERTICAL)
        img_path = "assets\\report_icon.png"
        self.report_btn = rounded_button.RoundedButton(self, img_path, wx.WHITE,
                                                       self.BG_COLOR, circle=True, use_image=True)
        self.report_btn.SetMinSize((50, 50))
        report_label = wx.StaticText(self, label="report")

        report_sizer.Add(self.report_btn)
        report_sizer.Add(report_label, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # creator account
        account_sizer = wx.BoxSizer(wx.VERTICAL)

        img_path = "assets\\null_pfp.png"

        self.account_btn = wx.StaticBitmap(self, bitmap=wx.Bitmap(img_path))
        self.account_btn.SetCursor(wx.Cursor(wx.CURSOR_HAND))

        self.account_label = wx.StaticText(self)

        account_sizer.Add(self.account_btn)
        account_sizer.Add(self.account_label, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # add to actions sizer
        actions_sizer.Add(personal_account_sizer)
        actions_sizer.Add(search_sizer, 0, wx.TOP, 10)

        actions_sizer.AddSpacer(150)

        actions_sizer.Add(play_sizer, 0, wx.TOP, 10)
        actions_sizer.Add(sound_sizer, 0, wx.TOP, 10)
        actions_sizer.Add(like_sizer, 0, wx.TOP, 10)
        actions_sizer.Add(open_comments_sizer, 0, wx.TOP, 10)
        actions_sizer.Add(test_sizer, 0, wx.TOP, 10)
        actions_sizer.Add(report_sizer, 0, wx.TOP, 10)
        actions_sizer.Add(account_sizer, 0, wx.TOP, 10)

        # comments
        self.comments_panel = comments.Comments(frame, self)
        self.comments_panel.SetMinSize((400, 0))

        # video description and name
        self.desc_and_name_panel = wx.Panel(self)
        self.desc_and_name_panel.SetBackgroundColour(self.BG_COLOR)
        desc_and_name_sizer = wx.BoxSizer(wx.VERTICAL)

        self.video_name_label = wx.StaticText(self.desc_and_name_panel)
        font = self.video_name_label.GetFont()
        font = font.Scale(4).Bold()
        self.video_name_label.SetFont(font)

        # video description
        desc_panel = wx.ScrolledWindow(self.desc_and_name_panel, style=wx.NO_BORDER)
        desc_panel.SetScrollRate(0, 20)
        desc_sizer = wx.BoxSizer(wx.VERTICAL)
        desc_panel.SetSizer(desc_sizer)

        self.video_desc_label = wx.StaticText(desc_panel)
        font = self.video_desc_label.GetFont()
        font = font.Scale(2)
        self.video_desc_label.SetFont(font)

        desc_sizer.Add(self.video_desc_label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.RIGHT | wx.LEFT, 5)

        # add to desc_and_name_sizer
        desc_and_name_sizer.Add(self.video_name_label, 0, wx.ALIGN_CENTER_HORIZONTAL)
        desc_and_name_sizer.Add(desc_panel, 1, wx.EXPAND | wx.TOP, 20)

        self.desc_and_name_panel.SetSizer(desc_and_name_sizer)

        #padding sizer
        padding_sizer = wx.BoxSizer(wx.HORIZONTAL)

        padding_sizer.AddStretchSpacer()
        padding_sizer.AddSpacer(10)

        #adding comments
        padding_sizer.Add(self.comments_panel, 10, wx.EXPAND)
        padding_sizer.AddSpacer(50)

        #adding video
        padding_sizer.Add(video_sizer, 10, wx.EXPAND)
        padding_sizer.AddSpacer(10)

        #adding video name and description
        padding_sizer.Add(self.desc_and_name_panel, 10, wx.EXPAND)

        padding_sizer.AddSpacer(10)
        padding_sizer.AddStretchSpacer()

        main_sizer.AddSpacer(50)
        main_sizer.Add(padding_sizer, 1 , wx.EXPAND)
        main_sizer.AddSpacer(50)

        self.SetSizer(main_sizer)

        #todo subscribe to different events for diffrent feeds or use self.isShown
        pub.subscribe(self.load_new_video, "load_new_video")

        pub.subscribe(self.load_new_comments, "load_new_comments")

        pub.subscribe(self.on_like_video_ans, "video_like_ans")

        # keep the 3 panels the same size
        self.comments_panel.SetMinSize((100, -1))
        video_sizer.SetMinSize((100, -1))  # if video_sizer is a sizer, not a panel
        self.desc_and_name_panel.SetMinSize((100, -1))

        self.Bind(wx.EVT_MOUSEWHEEL, self.on_scroll)
        self.like_btn.Bind(wx.EVT_LEFT_UP, self.on_like_video)
        self.open_comments_btn.Bind(wx.EVT_LEFT_UP, self.on_open_comments)
        self.sound_btn.Bind(wx.EVT_LEFT_UP, self.on_toggle_sound)
        self.play_btn.Bind(wx.EVT_LEFT_UP, self.on_toggle_play)

        self.Bind(wx.EVT_SIZE, self.on_resize)

        self.Hide()

    def on_personal_account(self, event):
        self.frame.user_profile_panel.set_user(self.frame.user.username)
        self.frame.switch_panel(self.frame.user_profile_panel, self)
        event.Skip()

    def update_pfp(self):
        user = self.frame.user
        if user:
            pfp_path = f"media\\{user.username}.png"
            if os.path.isfile(pfp_path):
                pfp = wx.Bitmap(wx.Image(pfp_path).Scale(settings.PFP_SIZE, settings.PFP_SIZE))
                self.personal_account_btn.SetBitmap(pfp)
        print("updated pfp")

    def Show(self, show = True):
        super().Show()
        self.update_pfp()
        self.comments_panel.update_pfp_bitmap()

    def update_video_desc_and_name(self):
        if self.current_video_id in self.frame.videos_details:
            self.video_desc_label.SetLabel(self.frame.videos_details[self.current_video_id].video_desc)
            self.video_name_label.SetLabel(self.frame.videos_details[self.current_video_id].video_name)

            self.video_name_label.Wrap(self.desc_and_name_panel.GetSize()[0])
            self.video_desc_label.Wrap(self.desc_and_name_panel.GetSize()[0])

    def on_resize(self, event):
        self.update_video_desc_and_name()
        self.Layout()
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

        self.sound_btn.Refresh()
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
        print("got like ans:", "status:", status, "new amount:",video.amount_of_likes)

        if video_id == self.current_video_id:
            self.update_like_button(status)
            self.update_likes_amount_label(video_id)

    def update_like_button(self, is_liked):
        if is_liked:
            self.like_btn.label_or_path = "assets\\liked_icon.png"
        else:
            self.like_btn.label_or_path = "assets\\like_icon.png"

        self.like_btn.Refresh()

    def update_likes_amount_label(self, video_id):
        self.likes_amount_label.SetLabel(str(self.frame.videos_details[video_id].amount_of_likes))
        print("set label to:", str(self.frame.videos_details[video_id].amount_of_likes))

    def on_scroll_timer(self, event):
        self.can_scroll = True
        self.scroll_timer.Stop()

    def on_scroll(self, event):
        rotation = event.GetWheelRotation()
        if self.can_scroll:
            self.play_btn.label_or_path = "assets\\pause.png"
            self.play_label.SetLabel("pause")

            self.can_scroll = False
            self.scroll_timer.Start(200)

            load_a_new_video = False
            new_index = self.video_index

            if rotation > 0: # scroll up
                # return to the previous video
                if self.video_index > 0:
                    new_index -= 1 # last video
                    load_a_new_video = True
            else:
                if len(self.videos_ids)>self.video_index + 1:
                    new_index += 1
                    load_a_new_video = True
                    if isinstance(self.associated_panel, FeedPanel):
                        msg = clientProtocol.build_req_video()
                        self.frame.comm.send_msg(msg)
                else:
                    # in the feed, the amount settings.VIDEOS_TO_REQ of videos that was req from the server were
                    # all watched, and so now waiting for the new videos to arrive.
                    #todo handle req new videos in profile or firsly all of the user's video ids list
                    self.waiting_for_video = True
                    self.frame.change_text_status("waiting for video from server...")

            if load_a_new_video:
                video_id = self.videos_ids[new_index]
                # checks if there already is this video's file.
                if video_id in self.frame.videos_ids_with_file:
                    video_to_load = self.frame.videos_details[self.videos_ids[new_index]]
                    self.load_video(video_to_load)
                    self.video_index = new_index
                else:
                    # if not, req it and dont set new index
                    msg = clientProtocol.build_req_video(video_id)
                    self.frame.comm.send_msg(msg)
                    self.waiting_for_video = True
                    self.frame.change_text_status("waiting for video from server...")
                    # if now req video, then you need to wait for it to arrive from the servr
        event.Skip()

    def on_load(self, event):
        self.video_ctrl.Play()
        self.video_ctrl.SetVolume(self.volume)
        # self.can_scroll = True

    def on_toggle_play(self, event):
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.video_ctrl.Play()
            self.play_btn.label_or_path = "assets\\pause.png"
            self.play_label.SetLabel("pause")
        else:
            self.video_ctrl.Pause()
            self.play_btn.label_or_path = "assets\\play.png"
            self.play_label.SetLabel("play")
        self.play_sizer.Layout()

    def load_new_video(self, video):
        print("loading new video:", type(self.associated_panel).__name__)
        video_id = video.video_id
        #todo req ~6 videos and then each timer req another one, so never stuck
        #todo send pfps together with the video and in signup
        if video_id:
            self.frame.videos_details[video_id] = video

            if video_id not in self.frame.videos_ids_with_file:
                self.frame.videos_ids_with_file.append(video_id)

            # if video_id in self.videos_ids:
            #     # if video_id was already on self.videos_ids, it means that it is part of the videos list to watch.
            #     # and that the user has just requested it, and so to play it now and to make it the current video.
            #     self.video_index = self.videos_ids.index(video_id)
            #     self.load_video(video)
            # else:
            #     self.videos_ids.append(video_id)

            if video_id not in self.videos_ids:
                self.videos_ids.append(video_id)

            if self.waiting_for_video: # checks if waiting for a video to arrive from server, if so, load it immediately
                self.load_video(video)
                self.video_index = self.videos_ids.index(video_id)
                self.waiting_for_video = False
                self.frame.change_text_status("video_loaded!")
        else:
            # reset videos so the user could watch them again
            self.frame.change_text_status("watched all videos")
            self.videos_ids = []
            msg = clientProtocol.build_req_video()
            self.frame.comm.send_msg(msg)
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

            self.update_video_desc_and_name()

            pfp_path = f"media\\{video.creator}.png"
            null_pfp_path = f"assets\\null_pfp.png"
            if os.path.isfile(pfp_path):
                self.account_btn.SetBitmap(wx.Bitmap(wx.Image(pfp_path).Scale(48,48)))
            else:
                self.account_btn.SetBitmap(wx.Bitmap(null_pfp_path))

            self.account_label.SetLabel(video.creator)

            self.Layout()

    def load_new_comments(self, video_id, comments):
        if video_id in self.frame.videos_details:
            self.frame.videos_details[video_id].add_comments(comments)
            self.comments_panel.add_comments(comments)

    def update_comments_label(self, video_id):
        self.comments_amount_label.SetLabel(str(self.frame.videos_details[video_id].amount_of_comments))
        print("set label to", self.frame.videos_details[video_id].amount_of_comments)

# three parts: comments, video, video desc + video name.


if __name__ == "__main__":
    app = wx.App()
    frame = wx.Frame(None)
    frame.SetSize((800, 600))
    panel = FeedPanel(frame, frame)
    frame.Show()
    app.MainLoop()
