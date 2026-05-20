import os.path
import re

import cv2
import requests
import wx
import wx.media
from pubsub import pub
import clientProtocol
import rounded_button
import rounded_input_field
import settings


class UploadVideoPanel(wx.ScrolledWindow):
    BG_COLOR = (232, 239, 255)
    COLUMN_WIDTH = 200

    RATIO = 4 / 3

    def __init__(self, frame, parent):
        """
        Initializes the UploadVideoPanel, building all UI elements and binding events.
        :param frame: The main application frame that manages panel switching and communication.
        :param parent: The parent wx window this panel belongs to.
        """
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

        # status label
        self.status_label = wx.StaticText(self)
        self.frame.status_labels.append(self.status_label)

        self.status_label.SetFont(
            wx.Font(settings.status_label_font_size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.status_label.SetForegroundColour(wx.RED)

        upload_video_label_and_status_sizer = wx.BoxSizer(wx.HORIZONTAL)

        upload_video_label_and_status_sizer.Add(upload_video_label)
        upload_video_label_and_status_sizer.AddStretchSpacer()
        upload_video_label_and_status_sizer.Add(self.status_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.TOP, 5)


        labels_font = wx.Font(wx.FontInfo(14).Bold())

        # fields
        self.filled_fields = {"video_name": False, "video_description":False, "test_link":True, "thumbnail": False, "video": False}  # [field_name] = True/False
        self.optional_fields = ["test_link"]
        self.thumbnail_path = ""
        self.video_path = ""
        self.topic_names = []
        self.topic_ids = []

        # video name label and field
        video_name_sizer = wx.BoxSizer(wx.VERTICAL)
        video_name_label = wx.StaticText(self, label="Video Name")
        video_name_label.SetFont(labels_font)

        self.video_name_field = rounded_input_field.RoundedInputField(self, self, "video_name", "Enter video name",
                                                                      background_color=self.BG_COLOR)

        # video name status and label
        video_name_status_and_label_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # video name status label
        self.video_name_status_label = wx.StaticText(self)
        self.video_name_status_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.video_name_status_label.SetForegroundColour(wx.RED)

        video_name_status_and_label_sizer.Add(video_name_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        video_name_status_and_label_sizer.Add(self.video_name_status_label,0, wx.ALIGN_CENTER_VERTICAL)

        # add to video_name_sizer
        video_name_sizer.Add(video_name_status_and_label_sizer, 0, wx.BOTTOM, 10)
        video_name_sizer.Add(self.video_name_field, 0, wx.EXPAND)


        # description label and field

        description_sizer = wx.BoxSizer(wx.VERTICAL)
        description_label = wx.StaticText(self, label="Description")
        description_label.SetFont(labels_font)

        self.description_field = rounded_input_field.RoundedInputField(self, self, "video_description",
                                                                       "Enter video description",
                                                                       multiline=True,
                                                                       background_color=self.BG_COLOR)

        # video name status and label
        description_status_and_label_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # video name status label
        self.description_status_label = wx.StaticText(self)
        self.description_status_label.SetFont(
            wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.description_status_label.SetForegroundColour(wx.RED)

        description_status_and_label_sizer.Add(description_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        description_status_and_label_sizer.Add(self.description_status_label, 0, wx.ALIGN_CENTER_VERTICAL)

        # add to description_sizer
        description_sizer.Add(description_status_and_label_sizer, 0, wx.BOTTOM, 10)
        description_sizer.Add(self.description_field, 1, wx.EXPAND)

        # test link field and button

        test_link_sizer = wx.BoxSizer(wx.VERTICAL)
        test_link_label = wx.StaticText(self, label="Test Link")
        test_link_label.SetFont(labels_font)

        self.test_link_field = rounded_input_field.RoundedInputField(self, self, "test_link",
                                                                     "Enter google forms test link (optional)",
                                                                     background_color=self.BG_COLOR)

        test_link_status_and_label_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # video name status label
        self.test_link_status_label = wx.StaticText(self)
        self.test_link_status_label.SetFont(
            wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.test_link_status_label.SetForegroundColour(wx.RED)

        test_link_status_and_label_sizer.Add(test_link_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        test_link_status_and_label_sizer.Add(self.test_link_status_label, 0, wx.ALIGN_CENTER_VERTICAL)
        
        
        test_link_sizer.Add(test_link_status_and_label_sizer, 0, wx.BOTTOM, 10)
        test_link_sizer.Add(self.test_link_field, 0, wx.EXPAND)

        # thumbnail label and button

        thumbnail_sizer = wx.BoxSizer(wx.VERTICAL)
        thumbnail_label = wx.StaticText(self, label="Thumbnail Image")
        thumbnail_label.SetFont(labels_font)

        self.pick_thumbnail_btn = rounded_button.RoundedButton(self, "Click to upload thumbnail", (249, 250, 251),
                                                               self.BG_COLOR, text_color=wx.BLACK)

        thumbnail_sizer.Add(thumbnail_label, 0, wx.BOTTOM, 10)
        thumbnail_sizer.Add(self.pick_thumbnail_btn, 1, wx.EXPAND)

        # video file and button
        video_sizer = wx.BoxSizer(wx.VERTICAL)
        video_label = wx.StaticText(self, label="video File")
        video_label.SetFont(labels_font)

        self.pick_video_btn = rounded_button.RoundedButton(self, "Click to upload video", (249, 250, 251),
                                                           self.BG_COLOR, text_color=wx.BLACK)
        video_sizer.Add(video_label, 0, wx.BOTTOM, 10)
        video_sizer.Add(self.pick_video_btn, 1, wx.EXPAND)

        # choose topics
        topics_sizer = wx.BoxSizer(wx.VERTICAL)
        topics_label = wx.StaticText(self, label=" 🏷️ Topics")
        topics_label.SetFont(labels_font)

        self.pick_topics_btn = rounded_button.RoundedButton(self, "Choose Topics", (249, 250, 251), self.BG_COLOR,
                                                            text_color=wx.BLACK)

        topics_sizer.Add(topics_label, 0, wx.BOTTOM, 10)
        topics_sizer.Add(self.pick_topics_btn, 0, wx.EXPAND)

        # upload video button
        self.upload_video_btn = rounded_button.RoundedButton(self, "Upload Video", settings.UNACTIVE_BUTTON,
                                                             self.BG_COLOR)
        self.upload_video_btn.SetMinSize((0, 50))

        # add to padded_sizer
        padded_sizer.AddSpacer(20)
        padded_sizer.Add(upload_video_label_and_status_sizer, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 20)
        # padded_sizer.Add(upload_video_label, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 20)
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

        pub.subscribe(self.on_video_upload_ans, "video_upload_ans")

        self.dots_animation_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.uploading_dots_animation, self.dots_animation_timer)

        self.Hide()

    def on_back_arrow(self, event):
        """
        Handles the back arrow button click, switching back to the user profile panel.
        :param event: The wx mouse event triggered by the button click.
        """
        self.frame.switch_panel(self.frame.user_profile_panel, self)
        event.Skip()

    def field_is_filled(self, field_name):
        """
        Marks a field as filled and activates the upload button if all required fields are filled.
        :param field_name: The name of the field that was just filled.
        """
        valid_val = True

        if field_name == "test_link":
            if self.gform_valid_form(self.test_link_field.get_value()):
                self.test_link_status_label.SetLabel("")
            else:
                self.test_link_status_label.SetLabel("google forms test link is not valid")
                self.filled_fields[field_name] = False
                valid_val = False

        elif field_name == "video_description":
            if len(self.description_field.get_value()) > settings.MAX_VIDEO_DESC_LENGTH:
                self.description_status_label.SetLabel(
                    f"Description is too long, a description cannot exceed {settings.MAX_VIDEO_DESC_LENGTH} characters")
                valid_val = False
            else:
                self.description_status_label.SetLabel("")

        elif field_name == "video_name":
            if len(self.video_name_field.get_value()) > settings.MAX_VIDEO_NAME_LENGTH:
                self.video_name_status_label.SetLabel(f"Video name is too long, a video name cannot exceed {settings.MAX_VIDEO_NAME_LENGTH} characters")
                valid_val = False

            else:
                self.video_name_status_label.SetLabel("")


        self.filled_fields[field_name] = valid_val
        if all(self.filled_fields.values()):
            self.upload_video_btn.set_active(True)
        else:
            self.upload_video_btn.set_active(False)

        self.Layout()
        self.Refresh()

    def field_is_unfilled(self, field_name):
        """
        Marks a required field as unfilled and deactivates the upload button.
        :param field_name: The name of the field that was cleared.
        """
        if field_name == "test_link":
            self.test_link_status_label.SetLabel("")
        elif field_name == "video_description":
            self.description_status_label.SetLabel("Description is required")
        elif field_name == "video_name":
            self.video_name_status_label.SetLabel("Video name is required")

        self.filled_fields[field_name] = False

        if field_name in self.optional_fields:
            self.filled_fields[field_name] = True

        if all(self.filled_fields.values()):
            self.upload_video_btn.set_active(True)
        else:
            self.upload_video_btn.set_active(False)

        self.Refresh()
        self.Layout()

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
        """
        Handles the topics button click, pre-loading selected topics and switching to the topic picker panel.
        :param event: The wx mouse event triggered by the button click.
        """
        self.frame.pick_video_topics_panel.set_selected_topics(self.topic_names)
        self.frame.switch_panel(self.frame.pick_video_topics_panel, self)
        event.Skip()

    def handle_set_topics(self, topics: list[int]):
        """
        Receives the chosen topic IDs from the topic picker panel, updates local state, and switches back to this panel.
        :param topics: A list of topic IDs selected by the user.
        """
        self.topic_ids = topics
        self.topic_names = [settings.TOPICS[topic_id] for topic_id in topics]
        print("topic_names:", self.topic_names)
        self.frame.switch_panel(self, self.frame.pick_video_topics_panel)

    @staticmethod
    def get_duration(file_path):
        """
        Calculates the duration of a video file in seconds using OpenCV.
        :param file_path: The file system path to the video file.
        :return: The duration of the video in seconds, or 0 if it cannot be determined.
        """
        cap = cv2.VideoCapture(file_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        duration = 0
        if frame_count > 0:
            duration = frame_count / fps
        cap.release()
        return duration

    def on_upload_video(self, event):
        """
        Handles the upload button click, validates all fields and file paths, checks video length,
        then sends the video and thumbnail files to the server.
        :param event: The wx mouse event triggered by the button click.
        """

        if all(self.filled_fields.values()):
            video_name = self.video_name_field.get_value().strip()
            description = self.description_field.get_value().strip()
            test_link = self.test_link_field.get_value().strip()
            test_link_valid = True

            if self.test_link_field.get_value():
                if not self.gform_exists(self.test_link_field.get_value()):
                    self.test_link_status_label.SetLabel("google forms test link is not valid")
                    test_link_valid = False

            if not os.path.isfile(self.thumbnail_path):
                self.thumbnail_path = ""
                self.pick_thumbnail_btn.label_or_path = "Error loading thumbnail, pick another one"

            if not os.path.isfile(self.video_path):
                self.video_path = ""
                self.pick_video_btn.label_or_path = "Error loading video, pick another one"
            else:
                duration = self.get_duration(self.video_path)
                if duration / 60 > settings.MAX_VIDEO_LENGTH:
                    self.video_path = ""
                    self.pick_video_btn.label_or_path = "Click to upload video"
                    self.upload_video_btn.label_or_path = f"Video length is too long, pick another one under {settings.MAX_VIDEO_LENGTH} minutes"

            if self.thumbnail_path and self.video_path and test_link_valid:
                self.upload_video_btn.label_or_path = "Uploading"
                self.dots_animation_timer.Start(500)  # every half a minute

                self.frame.video_comm.send_file("0.mp4", self.video_path, video_name, description, test_link,
                                                self.topic_ids)
                self.frame.video_comm.send_file("0.png", self.thumbnail_path)

        self.Layout()
        event.Skip()

    @staticmethod
    def gform_valid_form(url):
        pattern = r'(https?://)?docs\.google\.com/forms/d/[a-zA-Z0-9_-]+(/.*)?'
        return bool(re.match(pattern, url))

    @staticmethod
    def gform_exists(url):
        """
        Determines whether a given URL corresponds to an existing Google Form.

        :param url: The URL to verify as a valid and existing Google Form.
        :return: True if the URL corresponds to an existing Google Form, False otherwise.
        """
        pattern = r'(https?://)?docs\.google\.com/forms/d/[a-zA-Z0-9_-]+(/.*)?'
        ret_val = False
        if bool(re.match(pattern, url)):  # makes sure the url is a google form
            try:  # makes sure the google form is reachable
                response = requests.head(url, timeout=5, allow_redirects=True)
                ret_val = response.status_code == 200
            except requests.RequestException:
                pass

        return ret_val

    def on_video_upload_ans(self, video_id):
        """
        Handles the server's response after a video upload attempt, resetting the form on success
        or showing an error message on failure.
        :param video_id: The ID assigned to the uploaded video, or None/falsy if the upload failed.
        """
        print("video uploaded", video_id)
        if video_id:
            self.dots_animation_timer.Stop()
            self.upload_video_btn.label_or_path = "Video uploaded"
            self.test_link_field.set_value("")
            self.description_field.set_value("")
            self.video_name_field.set_value("")
            self.test_link_status_label.SetLabel("")
            self.pick_thumbnail_btn.label_or_path = "Click to upload thumbnail"
            self.pick_video_btn.label_or_path = "Click to upload video"
            self.pick_topics_btn.label_or_path = "Choose Topics"
            self.thumbnail_path = None
            self.video_path = None
            self.topic_names = []
            self.topic_ids = []
            self.upload_video_btn.set_active(False)
            self.filled_fields = {"video_name": False, "thumbnail": False, "video": False}

            feed_panel = self.frame.feed_panel
            feed_panel.videos_ids.insert(feed_panel.video_index, video_id)

            msg = clientProtocol.build_req_video(video_id)
            self.frame.video_requests_by_feeds.append(self.frame.feed_panel)
            self.frame.comments_requests_by_feeds.append(self.frame.feed_panel)
            self.frame.video_comm.send_msg(msg)

        else:
            self.upload_video_btn.label_or_path = "Video file already exists, upload a different one"
            self.video_path = None
            self.upload_video_btn.set_active(False)
            self.filled_fields["video"] = False

        self.Refresh()

    def uploading_dots_animation(self, event):
        if self.upload_video_btn.label_or_path.strip(".") == "Uploading":
            if self.upload_video_btn.label_or_path[-3:] == "...":
                self.upload_video_btn.label_or_path = self.upload_video_btn.label_or_path[:-3]
            else:
                self.upload_video_btn.label_or_path = self.upload_video_btn.label_or_path + "."

        self.upload_video_btn.Refresh()

    def scale_thumbnail(self, thumbnail_image):
        """
        Scales a thumbnail image to fit within the column dimensions while preserving aspect ratio,
        scaling up to whichever axis needs it most.
        :param thumbnail_image: The wx.Image object to be scaled.
        :return: A new wx.Image scaled to fit the column width and height.
        """
        w, h = thumbnail_image.GetSize()
        print("thumbnail size:", w, h)
        column_height = self.COLUMN_WIDTH * self.RATIO

        scale_w = self.COLUMN_WIDTH / w
        scale_h = column_height / h
        scale = max(scale_h, scale_w)

        new_w = int(w * scale)
        new_h = int(h * scale)
        print("new thumbnail size:", new_w, new_h)
        return thumbnail_image.Scale(new_w, new_h, wx.IMAGE_QUALITY_HIGH)

    def on_resize(self, event):
        """
        Handles window resize events by refreshing the layout and redrawing the panel.
        :param event: The wx size event triggered on window resize.
        """
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
