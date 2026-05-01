import math
import os.path
import shutil

import wx
import wx.media
from pubsub import pub

import clientProtocol
import profile_widget
import rounded_button
import settings
import comments
import video_widget


class UserProfilePanel(wx.ScrolledWindow):
    BG_COLOR = (232, 239, 255)
    COLUMN_WIDTH = 280

    RATIO = 4 / 3

    def __init__(self, frame, parent):
        super().__init__(parent)

        self.frame = frame
        self.parent = parent
        self.SetScrollRate(0, 12)

        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(main_sizer)
        self.SetBackgroundColour(self.BG_COLOR)

        self.current_user = None  # current user object
        self.waiting_for_videos = False
        self.videos_ids = []

        #padded vertical sizer
        padding_sizer = wx.BoxSizer(wx.VERTICAL)

        # profile info
        self.profile_info = profile_widget.ProfileWidget(self.frame, self)

        # videos grid
        videos_label_and_add_video_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        videos_label = wx.StaticText(self, label="Videos")
        videos_label.SetFont(videos_label.GetFont().Scale(1.3).Bold())

        self.add_video_btn = rounded_button.RoundedButton(self, "assets\\add_video.png", (180, 200, 255), self.BG_COLOR, circle=True, use_image=True)
        self.add_video_btn.SetMinSize((25, 25))

        # add to videos_label_and_add_video_btn_sizer
        videos_label_and_add_video_btn_sizer.Add(videos_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        videos_label_and_add_video_btn_sizer.Add(self.add_video_btn, 0, wx.ALIGN_CENTER_VERTICAL)

        self.grid_columns = 4
        self.grid_rows = 1

        self.videos_grid = wx.GridSizer(self.grid_rows, self.grid_columns, 20, 20)

        videos_sizer = wx.BoxSizer(wx.VERTICAL)
        videos_sizer.Add(videos_label_and_add_video_btn_sizer, 0, wx.BOTTOM, 10)
        videos_sizer.Add(self.videos_grid, 0)


        # add to padding_sizer
        padding_sizer.Add(self.profile_info, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 20)
        padding_sizer.Add(videos_sizer, 1, wx.ALIGN_CENTER_HORIZONTAL)


        # back arrow
        back_arrow = rounded_button.RoundedButton(self, "assets\\back_arrow.png", wx.WHITE, self.BG_COLOR, circle=True, use_image=True, text_color=wx.WHITE)
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
        pub.subscribe(self.update_pfp, "update_pfp_ans")

        self.Hide()
        # todo be able to change topics

    def on_scroll(self, event):
        event_type = event.GetEventType()

        scrolling_down = event_type in (wx.wxEVT_SCROLLWIN_LINEDOWN, wx.wxEVT_SCROLLWIN_PAGEDOWN,
                                      wx.wxEVT_SCROLLWIN_THUMBTRACK)

        if scrolling_down:
            current = self.GetScrollPos(wx.VERTICAL)
            max_pos = self.GetScrollRange(wx.VERTICAL) - self.GetScrollThumb(wx.VERTICAL)
            if len(self.current_user.videos_ids) > len(self.videos_ids) and self.videos_ids:
                if not self.waiting_for_videos:  # if there are more comments to req from the server
                    if current >= max_pos - 50:
                        msg = clientProtocol.build_req_creator_videos(self.current_user.username, self.videos_ids[-1])
                        self.frame.comm.send_msg(msg)
                        self.waiting_for_videos = True
                        self.frame.change_text_status("waiting for videos from server")
                        print("req more videos: last id:", self.videos_ids[-1], "videos ids:",self.videos_ids)
            elif current >= max_pos:
                self.frame.change_text_status("this user does not have more videos")

        event.Skip()

    def update_pfp(self):
        self.profile_info.update_pfp()
        self.frame.feed_panel.update_pfp()
        self.frame.user_profile_feed_panel.update_pfp()


    # called from profile_widget
    def set_pfp(self):
        """opens file dialog to pick pfp image"""
        dlg = wx.FileDialog(self, "Choose an Image to Set Your pfp", "", "", "PNG files (*.png)|*.png", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            img_path = dlg.GetPath()
            self.frame.video_comm.send_file(f"{self.frame.user.username}.png", img_path)

        dlg.Destroy()

    def video_selected(self, video):
        # req video
        self.frame.user_profile_feed_panel.waiting_for_video = True
        msg = clientProtocol.build_req_video(video.video_id)
        self.frame.comm.send_msg(msg)
        self.frame.video_requests_by_feeds.append(self.frame.user_profile_feed_panel)
        self.frame.comments_requests_by_feeds.append(self.frame.user_profile_feed_panel)

        # set video ids to scroll through in user_profile_feed_panel
        self.frame.user_profile_feed_panel.videos_ids = self.current_user.videos_ids + [0] # 0 indicates the end of the ids list
        print("ids list:", self.frame.user_profile_feed_panel.videos_ids)
        # switch to feed associated with user profile
        self.frame.user_profile_feed_panel.video_ctrl.Hide()
        self.frame.switch_panel(self.frame.user_profile_feed_panel, self)

    def on_back_arrow(self, event):
        self.frame.switch_panel(self.frame.feed_panel, self)
        event.Skip()

    def on_move_to_upload_video(self, event):
        self.frame.switch_panel(self.frame.upload_video_panel, self)
        event.Skip()

    def video_details_ans(self, video):
        print("got new video in profile:", video)

        if not video.video_id: # video_id = 0 indicates no more users videos
            self.frame.change_text_status("this user does not have more videos")

        elif video.video_id == settings.END_OF_BATCH_SEND_ID:
            self.waiting_for_videos = False


        if video.video_id not in self.videos_ids:
            self.videos_ids.append(video.video_id)

            if self.videos_grid.GetChildren() == self.grid_columns*self.grid_rows: # if grid is full
                self.grid_rows += 1
                self.videos_grid.SetRows(self.grid_rows+1)

            thumbnail = video_widget.VideoWidget(self, video, self.COLUMN_WIDTH, self.RATIO)
            self.videos_grid.Add(thumbnail, 0, wx.EXPAND)

            self.FitInside()
            self.Layout()
            self.Refresh()

    def user_info_ans(self, user):
        if user.username != self.frame.user.username: # to not reset the info about the user that is currently logged in
            self.frame.users[user.username] = user
        self.current_user = user
        self.profile_info.set_user(user)
        self.videos_ids.clear()
        # the amount of videos to recv is either the amount of videos the user has or the limit to be sent
        self.grid_rows = math.ceil(min(user.get_video_amount(), settings.AMOUNT_OF_VIDEOS_TO_SEND) / self.grid_columns)
        self.videos_grid.SetRows(self.grid_rows)

    def req_user_info(self, username):
        msg = clientProtocol.build_req_user_info(username)
        self.frame.comm.send_msg(msg)
        msg = clientProtocol.build_req_creator_videos(username)
        self.frame.comm.send_msg(msg)

    def set_user(self, username):
        self.videos_grid.Clear(True)
        self.current_user = username
        self.req_user_info(username)

        if self.current_user == self.frame.user.username:
            self.add_video_btn.Show()
        else:
            self.add_video_btn.Hide()
        self.Layout()
        self.Refresh()


    def on_resize(self, event):
        self.Layout()
        self.Refresh()
        event.Skip()


if __name__ == "__main__":
    app = wx.App()
    frame = wx.Frame(None)
    frame.SetSize((800, 600))
    panel = UserProfilePanel(frame, frame)
    frame.Show()
    app.MainLoop()
