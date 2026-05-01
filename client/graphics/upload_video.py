import math
import os.path

import wx
import wx.media
from pubsub import pub

import clientProtocol
import profile_widget
import rounded_button
import rounded_input_field
import settings
import comments


class UploadVideoPanel(wx.ScrolledWindow):
    BG_COLOR = (232, 239, 255)
    COLUMN_WIDTH = 200

    RATIO = 4 / 3

    def __init__(self, frame, parent):
        super().__init__(parent)

        self.frame = frame
        self.parent = parent

        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(main_sizer)
        self.SetBackgroundColour(self.BG_COLOR)

        padded_sizer = wx.BoxSizer(wx.VERTICAL)

        # upload video title
        upload_video_label = wx.StaticText(self, label="Upload Video")
        font = upload_video_label.GetFont().Scale(2).Bold()
        upload_video_label.SetFont(font)

        labels_font = wx.Font(wx.FontInfo(14).Bold())

        # fields
        self.filled_fields = {"video_name":False, "thumbnail":False,"video":False} # [field_name] = True/False
        self.optional_fields = ["test_link", "video_description"]
        self.thumbnail_path = None
        self.video_path = None
        self.topic_names = []
        self.topic_ids = []

        # video name label and field
        video_name_sizer = wx.BoxSizer(wx.VERTICAL)
        video_name_label = wx.StaticText(self, label="Video Name")
        video_name_label.SetFont(labels_font)

        self.video_name_field = rounded_input_field.RoundedInputField(self, self, "video_name", "Enter video name", background_color=self.BG_COLOR)

        video_name_sizer.Add(video_name_label, 0, wx.BOTTOM, 10)
        video_name_sizer.Add(self.video_name_field, 0, wx.EXPAND)

        # description label and field

        description_sizer = wx.BoxSizer(wx.VERTICAL)
        description_label = wx.StaticText(self, label="Description")
        description_label.SetFont(labels_font)

        self.description_field = rounded_input_field.RoundedInputField(self, self, "video_description", "Enter video description (optional)", multiline=True,
                                                                       background_color=self.BG_COLOR)
        description_sizer.Add(description_label, 0, wx.BOTTOM, 10)
        description_sizer.Add(self.description_field, 1, wx.EXPAND)

        # test link field and button

        test_link_sizer = wx.BoxSizer(wx.VERTICAL)
        test_link_label = wx.StaticText(self, label="Test Link")
        test_link_label.SetFont(labels_font)

        self.test_link_field = rounded_input_field.RoundedInputField(self, self, "test_link",
                                                                       "Enter test link (optional)",
                                                                       background_color=self.BG_COLOR)
        test_link_sizer.Add(test_link_label, 0, wx.BOTTOM, 10)
        test_link_sizer.Add(self.test_link_field, 0, wx.EXPAND)

        # thumbnail label and button

        thumbnail_sizer = wx.BoxSizer(wx.VERTICAL)
        thumbnail_label = wx.StaticText(self, label="Thumbnail Image")
        thumbnail_label.SetFont(labels_font)

        self.pick_thumbnail_btn = rounded_button.RoundedButton(self, "Click to upload thumbnail", (249, 250, 251), self.BG_COLOR, text_color = wx.BLACK)

        thumbnail_sizer.Add(thumbnail_label, 0, wx.BOTTOM, 10)
        thumbnail_sizer.Add(self.pick_thumbnail_btn, 1, wx.EXPAND)
        

        # video file and button
        video_sizer = wx.BoxSizer(wx.VERTICAL)
        video_label = wx.StaticText(self, label="video Image")
        video_label.SetFont(labels_font)

        self.pick_video_btn = rounded_button.RoundedButton(self, "Click to upload video", (249, 250, 251),
                                                           self.BG_COLOR, text_color=wx.BLACK)
        video_sizer.Add(video_label, 0, wx.BOTTOM, 10)
        video_sizer.Add(self.pick_video_btn, 1, wx.EXPAND)

        # choose topics
        topics_sizer = wx.BoxSizer(wx.VERTICAL)
        topics_label = wx.StaticText(self, label=" 🏷️ Topics")
        topics_label.SetFont(labels_font)

        self.pick_topics_btn = rounded_button.RoundedButton(self, "Choose Topics", (249, 250, 251), self.BG_COLOR, text_color=wx.BLACK)

        topics_sizer.Add(topics_label, 0, wx.BOTTOM, 10)
        topics_sizer.Add(self.pick_topics_btn, 0, wx.EXPAND)

        # upload video button
        self.upload_video_btn = rounded_button.RoundedButton(self, "Upload Video", settings.UNACTIVE_BUTTON, self.BG_COLOR)
        self.upload_video_btn.SetMinSize((0, 50))

        # add to padded_sizer
        padded_sizer.AddSpacer(20)
        padded_sizer.Add(upload_video_label, 0, wx.TOP | wx.BOTTOM, 20)
        padded_sizer.Add(video_name_sizer, 0, wx.EXPAND | wx.BOTTOM, 20)
        padded_sizer.Add(description_sizer, 2, wx.EXPAND | wx.BOTTOM, 20)
        padded_sizer.Add(test_link_sizer, 0, wx.EXPAND | wx.BOTTOM, 20)
        padded_sizer.Add(thumbnail_sizer, 1, wx.EXPAND | wx.BOTTOM, 20)
        padded_sizer.Add(video_sizer, 1, wx.EXPAND | wx.BOTTOM, 20)
        padded_sizer.Add(topics_sizer, 0, wx.EXPAND | wx.BOTTOM, 20)
        padded_sizer.Add(self.upload_video_btn, 0, wx.EXPAND)

        padded_sizer.AddSpacer(20)

        # back arrow
        back_arrow = rounded_button.RoundedButton(self, "assets\\back_arrow.png", wx.WHITE, self.BG_COLOR, circle=True,
                                                  use_image=True, text_color=wx.WHITE)
        back_arrow.SetMinSize((50, 50))

        # add to main_sizer
        main_sizer.Add(back_arrow, 0, wx.ALL, 20)
        main_sizer.AddStretchSpacer()
        main_sizer.Add(padded_sizer, 2, wx.EXPAND)
        main_sizer.AddStretchSpacer()

        self.Bind(wx.EVT_SIZE, self.on_resize)
        self.pick_thumbnail_btn.Bind(wx.EVT_LEFT_DOWN, self.on_pick_thumbnail)
        self.pick_video_btn.Bind(wx.EVT_LEFT_DOWN, self.on_pick_video)
        self.pick_topics_btn.Bind(wx.EVT_LEFT_DOWN, self.on_topics_pick)
        self.upload_video_btn.Bind(wx.EVT_LEFT_DOWN, self.on_upload_video)
        back_arrow.Bind(wx.EVT_LEFT_DOWN, self.on_back_arrow)

        self.Hide()

    def on_back_arrow(self, event):
        self.frame.switch_panel(self.frame.user_profile_panel, self)
        event.Skip()

    def field_is_filled(self, field_name):
        self.filled_fields[field_name] = True
        if all(self.filled_fields.values()):
            self.upload_video_btn.set_active(True)
        self.Refresh()

    def field_is_unfilled(self, field_name):
        if field_name not in self.optional_fields:
            self.upload_video_btn.set_active(False)
            self.filled_fields[field_name] = False
            self.upload_video_btn.set_active(False)
            self.Refresh()

    def on_pick_thumbnail(self, event):
        """opens file dialog to pick thumbnail image"""
        dlg = wx.FileDialog(self, "Choose thumbnail image", "", "", "PNG files (*.png)|*.png", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.thumbnail_path = dlg.GetPath()
            self.pick_thumbnail_btn.label_or_path = dlg.GetFilename()
            self.pick_thumbnail_btn.Refresh()
            self.field_is_filled("thumbnail")
        dlg.Destroy()

    def on_pick_video(self, event):
        """opens file dialog to pick video file"""
        print("picking video")
        dlg = wx.FileDialog(self, "Choose video file", "", "", "MP4 files (*.mp4)|*.mp4", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.video_path = dlg.GetPath()
            self.pick_video_btn.label_or_path = dlg.GetFilename()
            self.pick_video_btn.Refresh()
            self.field_is_filled("video")
        dlg.Destroy()


    def on_topics_pick(self, event):
        self.frame.pick_video_topics_panel.set_selected_topics(self.topic_names)
        self.frame.switch_panel(self.frame.pick_video_topics_panel, self) # switch to pick video topics panel
        event.Skip()

    def handle_set_topics(self, topics:list[int]):
        self.topic_ids = topics
        self.topic_names = [settings.TOPICS[topic_id] for topic_id in topics] # build topic names from settings.TOPICS
        print("topic_names:",self.topic_names)
        self.frame.switch_panel(self, self.frame.pick_video_topics_panel) # switch back to this panel from pick video topics


    def on_upload_video(self, event):
        video_name = self.video_name_field.get_value()
        description = self.description_field.get_value()
        test_link = self.test_link_field.get_value()
        if video_name and description and self.thumbnail_path and self.video_path:
            if not os.path.isfile(self.thumbnail_path):
                self.thumbnail_path = None
                self.pick_thumbnail_btn.label_or_path = "Error loading thumbnail, pick another one"

            if not os.path.isfile(self.video_path):
                self.video_path = None
                self.pick_video_btn.label_or_path = "Error loading video, pick another one"

            if self.thumbnail_path and self.video_path:
                self.upload_video_btn.label_or_path = "Uploading..."

                #todo recv confirmation the file and information have been uploaded
                # and the option to go back to the account's panel and from there to the feed

                # send video file
                self.frame.video_comm.send_file("0.mp4", self.video_path, video_name, description, test_link, self.topic_ids)

                # send thumbnail file
                self.frame.video_comm.send_file("0.png", self.thumbnail_path)

                # send video details
                # msg = clientProtocol.build_video_details(video_name, description, test_link, self.topic_ids)
                # self.frame.video_comm.send_msg(msg)

        event.Skip()


    def scale_thumbnail(self, thumbnail_image):
        w, h = thumbnail_image.GetSize()
        print("thumbnail size:", w, h)
        column_height = self.COLUMN_WIDTH * self.RATIO

        scale_w = self.COLUMN_WIDTH / w
        scale_h = column_height / h
        # if w>self.COLUMN_WIDTH and h >column_height:
        scale = max(scale_h, scale_w)

        new_w = int(w * scale)
        new_h = int(h * scale)
        print("new thumbnail size:", new_w, new_h)
        return thumbnail_image.Scale(new_w, new_h, wx.IMAGE_QUALITY_HIGH)

    # def Show(self, show=True):
    #     super().Show()
    #     self.

    def on_resize(self, event):
        self.Layout()
        self.Refresh()
        event.Skip()


if __name__ == "__main__":
    app = wx.App()
    frame = wx.Frame(None)
    frame.SetSize((800, 600))
    frame.Maximize()
    panel = UploadVideoPanel(frame, frame)
    panel.Show()
    frame.Show()
    app.MainLoop()
