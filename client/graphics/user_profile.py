import math
import os.path
import shutil

import wx
import wx.media
from PIL import Image
from pubsub import pub

import clientProtocol
import profile_widget
import rounded_button
import settings
import video_widget


class UserProfilePanel(wx.ScrolledWindow):
    BG_COLOR = (232, 239, 255)
    COLUMN_WIDTH = 280

    RATIO = 4 / 3

    def __init__(self, frame, parent):
        """
        Initializes the UserProfilePanel, setting up the profile info widget, videos grid, navigation buttons, and event bindings.
        :param frame: The main application frame.
        :param parent: The parent wx window this panel belongs to.
        """
        super().__init__(parent)

        self.frame = frame
        self.parent = parent
        self.SetScrollRate(0, 18)

        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(main_sizer)
        self.SetBackgroundColour(self.BG_COLOR)

        self.current_username = None  # current user username
        self.waiting_for_videos = False
        self.videos_ids = []
        self.videos_details = {}  # [creator_username] = [videos objects]

        # padded vertical sizer
        padding_sizer = wx.BoxSizer(wx.VERTICAL)

        # profile info
        self.profile_info = profile_widget.ProfileWidget(self.frame, self)
        self.profile_info.SetMinSize((800, -1))

        # videos grid
        videos_label_and_add_video_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        videos_label = wx.StaticText(self, label="Videos")
        videos_label.SetFont(videos_label.GetFont().Scale(1.3).Bold())

        self.add_video_btn = rounded_button.RoundedButton(self, "assets\\add_video.png", (180, 200, 255), self.BG_COLOR,
                                                          circle=True, use_image=True)
        self.add_video_btn.SetMinSize((25, 25))

        # add to videos_label_and_add_video_btn_sizer
        videos_label_and_add_video_btn_sizer.Add(videos_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        videos_label_and_add_video_btn_sizer.Add(self.add_video_btn, 0, wx.ALIGN_CENTER_VERTICAL)

        grid_columns = 4
        grid_rows = 1

        self.videos_grid = wx.GridSizer(grid_rows, grid_columns, 20, 20)

        videos_sizer = wx.BoxSizer(wx.VERTICAL)
        videos_sizer.Add(videos_label_and_add_video_btn_sizer, 0, wx.BOTTOM, 10)
        videos_sizer.Add(self.videos_grid, 0)

        # status label
        self.status_label = wx.StaticText(self, label="Loading Content From Server")
        self.frame.status_labels.append(self.status_label)
        self.status_label.SetFont(
            wx.Font(settings.status_label_font_size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.status_label.SetForegroundColour(wx.RED)

        # add to padding_sizer
        padding_sizer.Add(self.profile_info, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 20)
        padding_sizer.Add(videos_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL)
        padding_sizer.Add(self.status_label, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # back arrow
        back_arrow = rounded_button.RoundedButton(self, "assets\\back_arrow.png", wx.WHITE, self.BG_COLOR, circle=True,
                                                  use_image=True, text_color=wx.WHITE)
        back_arrow.SetMinSize((50, 50))

        # add to main_sizer
        main_sizer.Add(back_arrow, 0, wx.ALL, 20)
        main_sizer.AddStretchSpacer()
        main_sizer.Add(padding_sizer, 0, wx.EXPAND)
        main_sizer.AddStretchSpacer()

        self.Bind(wx.EVT_SIZE, self.on_resize)
        self.add_video_btn.Bind(wx.EVT_LEFT_UP, self.on_move_to_upload_video)
        back_arrow.Bind(wx.EVT_LEFT_DOWN, self.on_back_arrow)
        self.Bind(wx.EVT_SCROLLWIN, self.on_scroll)

        self.FitInside()  # calculates virtual size
        pub.subscribe(self.user_info_ans, "user_details_in_profile_ans")
        pub.subscribe(self.video_details_ans, "video_details_in_profile_ans")
        pub.subscribe(self.update_pfp_ans, "update_pfp_ans")
        pub.subscribe(self.uploaded_pfp_ans, "uploaded_pfp_ans")
        pub.subscribe(self.on_follow_user_ans, "follow_user_ans")

        self.Hide()

    def on_scroll(self, event):
        """
        Handles scroll events to request more videos from the server when the user reaches the bottom of the panel.
        :param event: The wx scroll event.
        """
        event_type = event.GetEventType()

        scrolling_down = event_type in (wx.wxEVT_SCROLLWIN_LINEDOWN, wx.wxEVT_SCROLLWIN_PAGEDOWN,
                                        wx.wxEVT_SCROLLWIN_THUMBTRACK)

        if self.current_username in self.frame.users:
            if scrolling_down:
                current = self.GetScrollPos(wx.VERTICAL)
                max_pos = self.GetScrollRange(wx.VERTICAL) - self.GetScrollThumb(wx.VERTICAL)
                if len(self.frame.users[self.current_username].videos_ids) > len(
                        self.videos_ids) and self.videos_ids:  # if there are more comments to req from the server
                    if not self.waiting_for_videos:
                        if current >= max_pos - 50:
                            msg = clientProtocol.build_req_creator_videos(self.current_username, self.videos_ids[-1])
                            self.frame.comm.send_msg(msg)
                            self.waiting_for_videos = True
                            self.status_label.SetLabel("waiting for videos from server")
                            self.Layout()
                            print("req more videos: last id:", self.videos_ids[-1], "videos ids:", self.videos_ids)
                elif current >= max_pos: # if this user doesnt have more videos and trying to scroll past the end of the videos list
                    self.status_label.SetLabel("this user does not have more videos")
                    self.Layout()
            else:
                self.status_label.SetLabel("")

        event.Skip()

    def uploaded_pfp_ans(self, status):
        if status == settings.SUCCESSFUL:
            wx.MessageBox("Profile picture has been change",
                          "Profile Picture Upload Successful", wx.OK | wx.ICON_INFORMATION)

        elif status == settings.INVALID_IMAGE:
            wx.MessageBox("The image you uploaded is not valid, please try another one!", "Error uploading new profile picture", wx.OK | wx.ICON_ERROR)

    def update_pfp_ans(self):
        """
        Refreshes the profile picture across the profile panel and both feed panels.
        """
        self.profile_info.update_pfp()
        self.frame.feed_panel.update_pfp()
        self.frame.user_profile_feed_panel.update_pfp()

    def on_set_pfp(self):
        """
            Opens a file dialog for the user to select a new profile picture and sends it to the server.
        """
        img_path = None
        dlg = wx.FileDialog(self, "Choose an Image to Set Your pfp", "", "", "PNG files (*.png)|*.png", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            img_path = dlg.GetPath()

        dlg.Destroy()
        if img_path:
            if self.is_img_valid(img_path):
                self.frame.video_comm.send_file(f"{self.frame.user.username}.png", img_path)
                wx.MessageBox("Profile picture change req sent to server",
                              "Profile Picture Upload", wx.OK | wx.ICON_INFORMATION)
            else:
                wx.MessageBox("The image you uploaded is not valid, please try another one!",
                              "Error uploading new profile picture", wx.OK | wx.ICON_ERROR)

    def on_follow_user(self):
        """
        Handles the action when the user attempts to follow another user.

        """
        if not self.frame.user.username == self.current_username:
            msg = clientProtocol.build_follow_req(self.current_username)
            self.frame.comm.send_msg(msg)

    def on_follow_user_ans(self, status, following):
        """
        Updates the following status of a user and updates the profile information
        accordingly.

        :param status: The new following status of the user. Should be a boolean value
            where True indicates the user is now followed, and False indicates the user
            is no longer followed.
        :param following: The identifier of the user whose following status is being
            updated.
        """
        self.frame.users[following].is_followed_by_user = bool(status)
        self.profile_info.update_following(status, following)

    def on_change_topics(self):
        """
        Handles the event triggered when topic selection changes.

        This method updates the topics in the pick topics panel and switches
        the current panel to the pick topics panel.
        """
        topic_names = [settings.TOPICS[topic_id] for topic_id in self.frame.user.topics]
        self.frame.pick_topics_panel.set_selected_topics(topic_names)
        self.frame.pick_topics_panel.panel_set_topics_handler = self
        self.frame.switch_panel(self.frame.pick_topics_panel, self)

    def on_set_topics_ans(self, topics):
        """
        Handles the process of setting topics and updating corresponding UI components.

        This method processes the provided topics, assigns them to the user's data, and
        then transitions the application to a different panel for further user interaction.

        :param topics: The topics selected by the user.
        """
        self.frame.user.topics = topics
        self.frame.switch_panel(self, self.frame.pick_topics_panel)

    def handle_set_topics(self, topics):
        """
        Builds and sends a set-topics message to the server.
        :param topics: A list of topic indices to send to the server.
        """
        msg = clientProtocol.build_set_topics(topics)
        self.frame.comm.send_msg(msg)

    @staticmethod
    def is_img_valid(path):
        """
            Checks whether a file at the given path is a valid image.
            Attempts to open and verify the file's integrity using PIL.
        :param path: The file path of the image to validate.
        :return: True if the file is a valid image, False otherwise.
        """
        try:
            with Image.open(path) as img:
                img.verify()  # checks file integrity
            ret_val = True
        except Exception:
            ret_val = False

        return ret_val

    def video_selected(self, video):
        """
        Handles the selection of a video thumbnail, requests the full video, and switches to the user profile feed panel.
        :param video: The video object that was selected.
        """
        # req video
        self.frame.user_profile_feed_panel.waiting_for_video = True
        msg = clientProtocol.build_req_video(settings.USER_PROFILE_FEED_ID, video.video_id)
        self.frame.comm.send_msg(msg)


        print("ids list:", self.frame.user_profile_feed_panel.videos_ids)
        # switch to feed associated with user profile
        self.frame.user_profile_feed_panel.video_ctrl.Hide()
        self.frame.switch_panel(self.frame.user_profile_feed_panel, self)

    def on_back_arrow(self, event):
        """
        Navigates back to the main feed panel.
        :param event: The wx mouse click event.
        """
        self.frame.switch_panel(self.frame.feed_panel, self)
        event.Skip()

    def on_move_to_upload_video(self, event):
        """
        Switches to the upload video panel.
        :param event: The wx mouse click event.
        """
        self.frame.switch_panel(self.frame.upload_video_panel, self)
        event.Skip()

    def video_details_ans(self, video):
        """
        Handles an incoming video detail response and adds the video thumbnail to the grid if it is new.
        :param video: The video object received from the server.
        """
        print("got new video in profile:", video.video_id)
        self.status_label.SetLabel("Loading Content")
        self.add_video_details(video)

    def add_video_details(self, video):
        """
            Adds a video to the local data structures and inserts its thumbnail into the
            grid if it belongs to the currently displayed user and is not already shown.
        :param video: The video object to add and display.
        """
        print("video in add_video_details:", video.video_id, video.creator)

        index = 0
        if video.video_id > 0:
            index = self.frame.users[video.creator].videos_ids.index(
                video.video_id)  # using index so if a creator added video insert it at index 0

            if video.video_id not in [video.video_id for video in self.videos_details[video.creator]]:  # ensure no dups
                # save video information to be used now and when loading this profile later
                self.videos_details[video.creator].insert(index, video)

        if video.creator == self.current_username:  # if video arriving belongs to user shown on screen
            if video.video_id == settings.END_OF_LIST_ID:  # video_id = 0 indicates no more users videos
                self.waiting_for_videos = False
                if not self.videos_ids:
                    if self.current_username == self.frame.user.username:
                        self.status_label.SetLabel("You do not have any content yet, upload one to get started!")
                        print("You do not have any content yet, upload one to get started!")
                    else:
                        self.status_label.SetLabel("This user does not have any content")
                else:
                    self.status_label.SetLabel("this user does not have more videos")
                self.Layout()

            elif video.video_id == settings.END_OF_BATCH_SEND_ID:  # ready for a new videos batch send
                self.waiting_for_videos = False
                self.status_label.SetLabel("")

            elif video.video_id > 0 and video.video_id not in self.videos_ids:  # ensures no dups
                self.videos_ids.insert(index, video.video_id)

                if len(self.videos_grid.GetChildren()) == self.videos_grid.GetCols() * self.videos_grid.GetRows():  # if grid is full
                    self.videos_grid.SetRows(self.videos_grid.GetRows() + 1)

                thumbnail = video_widget.VideoWidget(self, video, self.COLUMN_WIDTH, self.RATIO)
                self.videos_grid.Add(thumbnail, 0, wx.EXPAND)

            self.FitInside()
            self.Layout()
            self.Refresh()

    def user_info_ans(self, user):
        """
        Handles the server response with user details and initialises the profile view for that user.
        :param user: The user object received from the server.
        """
        self.videos_details[user.username] = []
        self.frame.users[user.username] = user
        self.set_user_details(user)

    def req_user_info_and_videos(self, username):
        """
        Sends requests to the server for the user's profile info and their uploaded videos.
        :param username: The username of the user whose info is being requested.
        """
        msg = clientProtocol.build_req_user_info(username)
        self.frame.comm.send_msg(msg)
        msg = clientProtocol.build_req_creator_videos(username)
        self.frame.comm.send_msg(msg)

    def set_user_details(self, user):
        """
            Sets the currently displayed user's details in the profile info widget.
        :param user: The user object whose details should be displayed.
        """
        self.current_username = user.username
        self.profile_info.set_user(user)

        # set video ids to scroll through in user_profile_feed_panel
        self.frame.user_profile_feed_panel.videos_ids = user.videos_ids.copy() + [
            0]  # 0 indicates the end of the ids list

        print("videos ids in user profile feed:", self.frame.user_profile_feed_panel.videos_ids)

    def set_new_user(self, username):
        """
        Clears the current profile view and loads the profile for the given username.
        :param username: The username of the user to display.
        """
        # todo: delete all info until new info arrives. update instantly when user info arrives

        self.waiting_for_videos = False
        self.videos_grid.Clear(True)
        self.videos_ids.clear()
        self.videos_grid.SetRows(1)
        self.status_label.SetLabel("")

        self.current_username = username

        # if user already has some of his videos in the user profile
        if username in self.videos_details.keys():
            user = self.frame.users[username]
            self.set_user_details(user)

            print("user:", user.username, "videos ids:", user.videos_ids)
            if not user.videos_ids:
                if self.frame.user.username == user.username:
                    self.status_label.SetLabel("You do not have any content yet, upload one to get started!")
                else:
                    self.status_label.SetLabel("This user does not have any content")
                self.Layout()

            for video in self.videos_details[username]:
                self.add_video_details(video)
        else:
            self.req_user_info_and_videos(username)
            self.status_label.SetLabel("Loading Content From Server")

        if self.current_username == self.frame.user.username:
            self.add_video_btn.Show()
        else:
            self.add_video_btn.Hide()
        self.Layout()
        self.Refresh()

    def on_resize(self, event):
        """
        Refreshes the layout when the panel is resized.
        :param event: The wx resize event.
        """
        self.Layout()
        self.Refresh()
        event.Skip()

    def on_a_user_added_comment(self, video_id):
        """
            Increments the comment count for the matching video and refreshes the
            display if the video is currently on screen.
        :param video_id: The ID of the video that received a new comment.
        """
        # combines all the videos from each list to one list. for each video_list in values collects every video
        videos = [video for video_list in self.videos_details.values() for video in video_list]

        for video in videos:
            if video.video_id == video_id:
                video.amount_of_comments += 1
                break

        # update the video comments amount label
        if video_id in self.videos_ids:
            self.Refresh()  # refresh if the video is currently on screen

    def on_a_user_liked_video(self, status, video_id):
        """
            Updates the like count for the matching video and refreshes the display
            if the video is currently on screen.
        :param status: 1 if the video was liked, 0 if the like was removed.
        :param video_id: The ID of the video that was liked or unliked.
        """
        videos = [video for video_list in self.videos_details.values() for video in video_list]

        for video in videos:
            if video.video_id == video_id:
                video.amount_of_likes += 1 if status else -1
                break

        # update the video comments amount label
        if video_id in self.videos_ids:
            self.Refresh()  # refresh if the video is currently on screen

    def on_a_user_upload_video(self, username, video_id):
        """
            Handles a video upload event by re-requesting the creator's videos from the
            server and refreshing the grid if the uploader is currently being viewed.
        :param username: The username of the user who uploaded the video.
        :param video_id: The ID of the newly uploaded video.
        """
        print("creator has uploaded new video:", username)
        msg = clientProtocol.build_req_creator_videos(username)
        self.frame.comm.send_msg(msg)

        if self.current_username == username:
            self.waiting_for_videos = True
            self.videos_grid.Clear(True)
            self.videos_ids.clear()

            if username == self.frame.user.username:
                self.status_label.SetLabel("You have uploaded a new video, loading it now from server")
            else:
                self.status_label.SetLabel("This creator uploaded a new video, loading it now from server")
            self.Layout()

            self.frame.user_profile_feed_panel.videos_ids.insert(0, video_id)

            print("inserted video id:",video_id, "new videos_ids:", self.frame.user_profile_feed_panel.videos_ids )

            self.profile_info.videos_numeric_amount_label.SetLabel(
                str(self.frame.users[username].get_video_amount()))

    def on_a_user_deleted_comment(self, video_id):
        """
            Handles the event where a user deletes a comment on a video.
            Decrements the comment count for the matching video, and refreshes the display if the video is currently on screen.
        :param video_id: The ID of the video whose comment count should be decremented.
        """
        videos = [video for video_list in self.videos_details.values() for video in video_list]

        for video in videos:
            if video.video_id == video_id:
                video.amount_of_comments -= 1
                break

        if video_id in self.videos_ids:
            self.Refresh()  # refresh if the video is currently on screen

    def on_a_user_deleted_video(self, video_id):
        """
            Handles the event where a user deletes a video.
            Removes the video from the local data structures, and if the video is currently on screen,
            marks its thumbnail as deleted and updates the video count label.
        :param video_id: The ID of the video that was deleted.
        """
        videos = [video for video_list in self.videos_details.values() for video in video_list]

        for video in videos:
            if video.video_id == video_id:
                self.videos_details[video.creator].remove(video)
                self.frame.users[video.creator].videos_ids.remove(video_id)

                if video_id in self.videos_ids:  # if video is currently on screen
                    self.videos_grid.GetChildren()[self.videos_ids.index(video_id)].GetWindow().set_deleted()
                    self.profile_info.videos_numeric_amount_label.SetLabel(
                        str(self.frame.users[video.creator].get_video_amount()))

                break

        if os.path.isfile(f"media\\{video_id}.png"):
            try:
                os.remove(f"media\\{video_id}.png")
            except Exception as e:
                print("error deleting image:", e)

        self.Layout()


if __name__ == "__main__":
    app = wx.App()
    frame = wx.Frame(None)
    frame.SetSize((800, 600))
    panel = UserProfilePanel(frame, frame)
    frame.Show()
    app.MainLoop()
