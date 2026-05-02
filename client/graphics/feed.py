import os.path

import wx
import wx.media
from pubsub import pub

import clientProtocol
import rounded_button
import settings
import comments
from user_profile import UserProfilePanel


class FeedPanel(wx.Panel):
    BG_COLOR = (232, 239, 255)

    volume = 0

    def __init__(self, frame, parent, associated_panel=None):
        super().__init__(parent)

        self.frame = frame
        self.parent = parent

        self.SetWindowStyle(self.GetWindowStyle() | wx.WANTS_CHARS)
        self.SetFocus()

        self.associated_panel = associated_panel
        if not self.associated_panel:
            self.associated_panel = self

        self.is_playing = True

        self.video_index = 0

        self.waiting_for_video = True

        self.videos_ids = []

        self.can_scroll = True

        self.current_video_id = None  # video_id

        self.no_videos = False

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.SetBackgroundColour(self.BG_COLOR)

        # video
        video_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.video_ctrl = wx.media.MediaCtrl(self, style=wx.SIMPLE_BORDER, szBackend=wx.media.MEDIABACKEND_WMP10)
        self.video_ctrl.Bind(wx.media.EVT_MEDIA_LOADED, self.on_load)
        self.video_ctrl.Bind(wx.media.EVT_MEDIA_FINISHED, self.on_video_finished)

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
        self.sound_label = wx.StaticText(self, label="sound off")

        sound_sizer.Add(self.sound_btn)
        sound_sizer.Add(self.sound_label, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # like
        like_sizer = wx.BoxSizer(wx.VERTICAL)
        img_path = "assets\\like_icon.png"
        self.like_btn = rounded_button.RoundedButton(self, img_path, wx.WHITE,
                                                     self.BG_COLOR, circle=True, use_image=True)
        self.like_btn.SetMinSize((50, 50))
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

        # padding sizer
        padding_sizer = wx.BoxSizer(wx.HORIZONTAL)

        padding_sizer.AddStretchSpacer()
        padding_sizer.AddSpacer(10)

        # adding comments
        padding_sizer.Add(self.comments_panel, 10, wx.EXPAND)
        padding_sizer.AddSpacer(50)

        # adding video
        padding_sizer.Add(video_sizer, 10, wx.EXPAND)
        padding_sizer.AddSpacer(10)

        # adding video name and description
        padding_sizer.Add(self.desc_and_name_panel, 10, wx.EXPAND)

        padding_sizer.AddSpacer(10)
        padding_sizer.AddStretchSpacer()

        if isinstance(self.associated_panel, UserProfilePanel):
            # back arrow
            back_arrow = rounded_button.RoundedButton(self, "assets\\back_arrow.png", wx.WHITE, self.BG_COLOR,
                                                      circle=True, use_image=True)
            back_arrow.SetMinSize((50, 50))
            back_arrow.Bind(wx.EVT_LEFT_DOWN, self.on_back_arrow)
            main_sizer.Add(back_arrow, 0, wx.ALL, 20)

        # add to main_sizer
        self.status_label = wx.StaticText(self, label="Loading video")
        self.status_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.status_label.SetForegroundColour(wx.Colour(wx.RED))

        main_sizer.AddSpacer(25)
        main_sizer.Add(self.status_label, 0, wx.ALIGN_CENTER_HORIZONTAL)
        main_sizer.AddSpacer(25)
        main_sizer.Add(padding_sizer, 1, wx.EXPAND)
        main_sizer.AddSpacer(50)

        self.SetSizer(main_sizer)

        # keep the 3 panels the same size
        self.comments_panel.SetMinSize((100, -1))
        video_sizer.SetMinSize((100, -1))
        self.desc_and_name_panel.SetMinSize((100, -1))

        self.personal_account_btn.Bind(wx.EVT_LEFT_UP, self.on_personal_account)
        self.like_btn.Bind(wx.EVT_LEFT_UP, self.on_like_video)
        self.open_comments_btn.Bind(wx.EVT_LEFT_UP, self.on_open_comments)
        self.sound_btn.Bind(wx.EVT_LEFT_UP, self.on_toggle_sound)
        self.play_btn.Bind(wx.EVT_LEFT_UP, self.on_toggle_play)
        self.account_btn.Bind(wx.EVT_LEFT_UP, self.on_move_to_creator_account)

        self.Bind(wx.EVT_MOUSEWHEEL, self.on_scroll)
        self.Bind(wx.EVT_SIZE, self.on_resize)

        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.video_ctrl.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.comments_panel.comments_panel.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.comments_panel.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        desc_panel.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

        self.Hide()

    def on_key_down(self, event):
        """
            Toggles play/pause when the spacebar is pressed.
        :param event: The key down event triggered by a keypress.
        """
        if event.GetKeyCode() == wx.WXK_SPACE:
            self.on_toggle_play(None)
        event.Skip()

    def on_move_to_creator_account(self, event):
        """
            Navigates to the current video's creator profile page.
        :param event: The mouse click event that triggered this handler.
        """
        self.frame.user_profile_panel.set_user(self.frame.videos_details[self.current_video_id].creator)
        self.frame.switch_panel(self.frame.user_profile_panel, self)
        event.Skip()

    def on_add_comment_ans(self, video_id, comment):
        """
            Forwards a new comment confirmation to the comments panel.
        :param video_id: The ID of the video the comment was posted on.
        :param comment: The comment data to display.
        """
        self.comments_panel.on_add_comment_ans(video_id, comment)

    def on_back_arrow(self, event):
        """
            Navigates back to the current user's profile page.
        :param event: The mouse click event that triggered this handler.
        """
        self.frame.user_profile_panel.set_user(self.frame.user.username)
        self.frame.switch_panel(self.frame.user_profile_panel, self)
        event.Skip()

    def on_personal_account(self, event):
        """
            Navigates to the logged-in user's own profile page.
        :param event: The mouse click event that triggered this handler.
        """
        self.frame.user_profile_panel.set_user(self.frame.user.username)
        self.frame.switch_panel(self.frame.user_profile_panel, self)
        event.Skip()

    def update_pfp(self):
        """
            Updates the personal account button bitmap with the user's current profile picture.
        """
        user = self.frame.user
        if user:
            pfp_path = f"media\\{user.username}.png"
            if os.path.isfile(pfp_path):
                pfp = wx.Bitmap(wx.Image(pfp_path).Scale(settings.PFP_SIZE, settings.PFP_SIZE))
                self.personal_account_btn.SetBitmap(pfp)
        print("updated pfp")

    def Show(self, show=True):
        """
            Shows the panel, resumes video playback, updates the profile picture,
            and restores the current volume state.
        :param show: Whether to show the panel.
        """
        super().Show()
        self.video_ctrl.Play()
        self.update_pfp()
        self.comments_panel.update_pfp_bitmap()
        self.video_ctrl.SetVolume(FeedPanel.volume)
        self.update_sound_button_and_label(FeedPanel.volume)

    def Hide(self):
        """
            Hides the panel and pauses video playback.
        """
        super().Hide()
        self.video_ctrl.Pause()

    def update_video_desc_and_name(self):
        """
            Updates the video name and description labels with the current video's details.
        """
        if self.current_video_id in self.frame.videos_details:
            self.video_desc_label.SetLabel(self.frame.videos_details[self.current_video_id].video_desc)
            self.video_name_label.SetLabel(
                str(self.current_video_id) + " " + self.frame.videos_details[self.current_video_id].video_name)

            self.video_name_label.Wrap(self.desc_and_name_panel.GetSize()[0])
            self.video_desc_label.Wrap(self.desc_and_name_panel.GetSize()[0])

    def on_resize(self, event):
        """
            Refreshes the layout and video description labels when the panel is resized.
        :param event: The resize event triggered when the panel size changes.
        """
        self.update_video_desc_and_name()
        self.Layout()
        self.Refresh()
        event.Skip()

    def update_sound_button_and_label(self, volume):
        """
            Updates the sound button icon and label to reflect the current volume state.
        :param volume: The current volume level; non-zero means sound is on, zero means muted.
        """
        if volume:
            self.sound_btn.label_or_path = "assets\\sound_on.png"
            self.sound_label.SetLabel("sound on")
        else:
            self.sound_btn.label_or_path = "assets\\sound_off.png"
            self.sound_label.SetLabel("sound off")
        self.sound_btn.Refresh()

    def on_toggle_sound(self, event):
        """
            Toggles the video sound between muted and unmuted.
        :param event: The mouse click event that triggered this handler.
        """
        FeedPanel.volume = int(not FeedPanel.volume)
        self.video_ctrl.SetVolume(FeedPanel.volume)
        self.update_sound_button_and_label(FeedPanel.volume)
        event.Skip()

    def on_open_comments(self, event):
        """
            Toggles the visibility of the comments panel.
        :param event: The mouse click event that triggered this handler.
        """
        if self.comments_panel.IsShown():
            self.comments_panel.Hide()
        else:
            self.comments_panel.Show()
        self.Layout()
        self.Refresh()
        self.Update()
        event.Skip()

    def on_like_video(self, event):
        """
            Sends a like or unlike request to the server for the current video.
        :param event: The mouse click event that triggered this handler.
        """
        print("liking video")
        if self.current_video_id:
            msg = clientProtocol.build_like_video(self.current_video_id)
            self.frame.comm.send_msg(msg)
            self.frame.like_requests_by_feeds.append(self)
        event.Skip()

    def on_like_video_ans(self, status, video_id):
        """
            Handles the server's response to a like or unlike request,
            updating the like button and count label accordingly.
        :param status: 1 if the video was liked, 0 if the like was removed.
        :param video_id: The ID of the video that was liked or unliked.
        """
        video = self.frame.videos_details[video_id]
        video.amount_of_likes += 1 if status else -1  # either + 1 or - 1
        video.liked = bool(status)  # update liked
        print("got like ans:", "status:", status, "new amount:", video.amount_of_likes)

        if video_id == self.current_video_id:
            self.update_like_button(status)
            self.update_likes_amount_label(video_id)

    def update_like_button(self, is_liked):
        """
            Updates the like button icon to reflect whether the video is currently liked.
        :param is_liked: True or 1 if the video is liked, False or 0 otherwise.
        """
        if is_liked:
            self.like_btn.label_or_path = "assets\\liked_icon.png"
        else:
            self.like_btn.label_or_path = "assets\\like_icon.png"

        self.like_btn.Refresh()

    def update_likes_amount_label(self, video_id):
        """
            Updates the likes count label with the current like count for the given video.
        :param video_id: The ID of the video whose like count should be displayed.
        """
        self.likes_amount_label.SetLabel(str(self.frame.videos_details[video_id].amount_of_likes))
        print("set label to:", str(self.frame.videos_details[video_id].amount_of_likes))

    def on_scroll(self, event):
        """
            Handles mouse wheel scrolling to navigate between videos.
            Scrolling up loads the previous video and scrolling down loads the next,
            requesting new videos from the server when necessary.
        :param event: The mouse wheel event triggered by scrolling.
        """
        rotation = event.GetWheelRotation()
        if self.can_scroll:
            self.play_btn.label_or_path = "assets\\pause.png"
            self.play_label.SetLabel("pause")

            load_a_new_video = False
            new_index = self.video_index

            if rotation > 0:  # scroll up
                # return to the previous video
                if self.video_index > 0:
                    print("current video index:", self.video_index, "ids:", self.videos_ids)
                    new_index -= 1  # last video
                    load_a_new_video = True
            else:
                if len(self.videos_ids) > self.video_index + 1:
                    new_index += 1
                    load_a_new_video = True
                    if isinstance(self.associated_panel, FeedPanel):  # if in the feed, then preload a video
                        msg = clientProtocol.build_req_video()
                        self.frame.comm.send_msg(msg)
                        self.frame.video_requests_by_feeds.append(self)
                        self.frame.comments_requests_by_feeds.append(self)
                else:
                    # in the feed, the amount settings.VIDEOS_TO_REQ of videos that was req from the server were
                    # all watched, and so now waiting for the new videos to arrive.
                    self.waiting_for_video = True
                    self.status_label.SetLabel("waiting for video from server...")
                    if self.no_videos:
                        msg = clientProtocol.build_req_video()
                        self.frame.comm.send_msg(msg)

                        self.frame.video_requests_by_feeds.append(self)
                        self.frame.comments_requests_by_feeds.append(self)

            if load_a_new_video:
                video_id = self.videos_ids[new_index]
                # checks if there already is this video's file.
                if not video_id:  # no more videos, either watched them all or no more in search/profile
                    # reset videos so the user could watch them again
                    if isinstance(self.associated_panel, FeedPanel):
                        self.status_label.SetLabel("Watched all videos, reseting watched history")

                        self.videos_ids = []
                        self.video_index = 0
                        self.waiting_for_video = True
                        msg = clientProtocol.build_req_video()
                        for req in range(settings.AMOUNT_OF_VIDEOS_TO_REQ):
                            self.frame.comm.send_msg(msg)
                            self.frame.video_requests_by_feeds.append(self.frame.feed_panel)
                            self.frame.comments_requests_by_feeds.append(self.frame.feed_panel)
                        print("watched all videos")

                    elif isinstance(self.associated_panel, UserProfilePanel):
                        self.status_label.SetLabel("This user does not have more videos")

                        print("This user does not have more videos")

                elif video_id in self.frame.videos_details:
                    video_to_load = self.frame.videos_details[self.videos_ids[new_index]]
                    print("loading video:", video_id, 'comments', video_to_load.get_comments())
                    self.load_video(video_to_load)
                    self.video_index = new_index
                else:
                    # if not, req it and dont set new index
                    msg = clientProtocol.build_req_video(video_id)
                    self.frame.comm.send_msg(msg)

                    self.frame.video_requests_by_feeds.append(self)
                    self.frame.comments_requests_by_feeds.append(self)

                    self.waiting_for_video = True
                    # if now requested video, then you need to wait for it to arrive from the server
                    self.status_label.SetLabel("waiting for video from server...")
        self.Layout()
        event.Skip()

    def on_load(self, event):
        """
            Handles the media loaded event by playing the video and re-enabling scrolling.
        :param event: The media loaded event fired when a video finishes loading.
        """
        self.video_ctrl.Show()
        self.video_ctrl.Play()
        self.video_ctrl.SetVolume(FeedPanel.volume)
        self.video_ctrl.Thaw()  # unfreeze the video once it loads
        print("video has thawed")
        self.can_scroll = True
        self.Layout()
        event.Skip()

    def on_video_finished(self, event):
        """
            Loops the current video by seeking back to the start and replaying it.
        :param event: The media finished event fired when a video reaches its end.
        """
        self.video_ctrl.Seek(0)
        self.video_ctrl.Play()
        event.Skip()

    def on_toggle_play(self, event):
        """
            Toggles the video between playing and paused states,
            updating the play button icon and label accordingly.
        :param event: The mouse click or key event that triggered this handler, or None.
        """
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
        if event:
            event.Skip()

    def load_new_video(self, video):
        """
            Registers a newly received video, appends it to the video list,
            and immediately loads it if the panel is currently waiting for one.
        :param video: The video object received from the server.
        """
        video_id = video.video_id
        if video_id > 0:  # if not a special id
            self.no_videos = False

            self.frame.videos_details[video_id] = video

            if video_id not in self.videos_ids:
                self.videos_ids.append(video_id)

            if self.waiting_for_video:  # checks if waiting for a video to arrive from server, if so, load it immediately
                self.load_video(video)
                self.video_index = self.videos_ids.index(video_id)
                print(video_id, "video loaded at index", self.video_index)
                self.waiting_for_video = False
                self.status_label.SetLabel("video loaded")
                self.status_label.Layout()

        elif video_id == settings.END_OF_LIST_ID:
            self.videos_ids.append(
                video_id)  # add 0 to indicate the end of the videos or -2 to indicate the video has been deleted
            self.frame.comments_requests_by_feeds.pop(0)

        elif video_id == settings.NO_VIDEOS_ID:
            self.frame.comments_requests_by_feeds.pop(0)
            self.status_label.SetLabel("No videos in the system, go to your profile to upload a video")
            self.no_videos = True
            self.Layout()

    def load_video(self, video):
        """
            Loads and plays a video in the media control, updating all associated
            UI elements including likes, comments, description, and creator info.
        :param video: The video object to load and display.
        """
        video_id = video.video_id
        if video_id:
            self.current_video_id = video_id

            self.video_ctrl.Freeze()
            self.Layout()
            self.Refresh()
            self.Update()

            print("loading video:", video_id)
            self.can_scroll = False
            print("has freezed")

            self.video_ctrl.Load(f"media\\{video_id}.mp4")
            self.video_ctrl.SetInitialSize((500, 500))
            self.comments_panel.set_video(video)
            self.status_label.SetLabel("")

            # load actions
            self.update_like_button(video.liked)
            self.update_likes_amount_label(video_id)
            self.update_comments_label(video_id)

            self.update_video_desc_and_name()
            self.update_creator_account_pfp_and_label(video)

            self.Layout()

    def update_creator_account_pfp_and_label(self, video):
        """
            Updates the creator account button bitmap and label with the video creator's
            profile picture and username.
        :param video: The video object whose creator info should be displayed.
        """
        pfp_path = f"media\\{video.creator}.png"
        null_pfp_path = f"assets\\null_pfp.png"
        if os.path.isfile(pfp_path):
            self.account_btn.SetBitmap(wx.Bitmap(wx.Image(pfp_path).Scale(48, 48)))
        else:
            self.account_btn.SetBitmap(wx.Bitmap(null_pfp_path))

        self.account_label.SetLabel(video.creator)

    def load_new_comments(self, video_id, comments):
        """
            Adds newly received comments to the video's details and updates the
            comments panel if the video is currently being viewed.
        :param video_id: The ID of the video the comments belong to.
        :param comments: A list of comment data to add.
        """
        print("loading new comments for video:", video_id)
        if video_id in self.frame.videos_details:
            self.frame.videos_details[video_id].add_comments(comments)

            if video_id == self.current_video_id:
                self.comments_panel.add_comments(comments)

    def update_comments_label(self, video_id):
        """
            Updates the comments count label with the current comment count for the given video.
        :param video_id: The ID of the video whose comment count should be displayed.
        """
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
