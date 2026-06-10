import os.path

import wx
import wx.media
from pubsub import pub

import clientProtocol
import rounded_button
import settings
import comments
import user


class ProfileWidget(wx.Panel):
    BG_COLOR = (243, 247, 255)

    def __init__(self, frame, parent):
        """
        Initializes the ProfileWidget, building the UI with a profile picture, username label,
        and stats for video count, followers, and following.
        :param frame: The main application frame that holds the current logged-in user.
        :param parent: The parent wx window this widget belongs to.
        """
        super().__init__(parent)

        self.frame = frame
        self.parent = parent
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(main_sizer)

        self.SetBackgroundColour(self.BG_COLOR)

        self.current_user = None

        # profile info
        profile_info_sizer = wx.BoxSizer(wx.HORIZONTAL)

        pfp = wx.Bitmap(wx.Image("assets\\null_pfp_high_quality.png"))
        self.pfp = wx.StaticBitmap(self, bitmap=pfp)

        username_and_info_sizer = wx.BoxSizer(wx.VERTICAL)
        self.username_label = wx.StaticText(self)
        self.username_label.SetFont(self.username_label.GetFont().Scale(2).Bold())

        info_sizer = wx.BoxSizer(wx.HORIZONTAL)

        numerics_font = wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

        # videos amount
        videos_amount_sizer = wx.BoxSizer(wx.VERTICAL)
        self.videos_numeric_amount_label = wx.StaticText(self)
        self.videos_numeric_amount_label.SetFont(numerics_font)
        self.videos_amount_label = wx.StaticText(self, label="Videos")

        videos_amount_sizer.Add(self.videos_numeric_amount_label, 0, wx.ALIGN_CENTER_HORIZONTAL)
        videos_amount_sizer.Add(self.videos_amount_label, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # followers amount
        followers_amount_sizer = wx.BoxSizer(wx.VERTICAL)
        self.followers_numeric_amount_label = wx.StaticText(self)
        self.followers_numeric_amount_label.SetFont(numerics_font)
        self.followers_amount_label = wx.StaticText(self, label="followers")

        followers_amount_sizer.Add(self.followers_numeric_amount_label, 0, wx.ALIGN_CENTER_HORIZONTAL)
        followers_amount_sizer.Add(self.followers_amount_label, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # following amount
        following_amount_sizer = wx.BoxSizer(wx.VERTICAL)
        self.following_numeric_amount_label = wx.StaticText(self)
        self.following_numeric_amount_label.SetFont(numerics_font)
        self.following_amount_label = wx.StaticText(self, label="following")

        following_amount_sizer.Add(self.following_numeric_amount_label, 0, wx.ALIGN_CENTER_HORIZONTAL)
        following_amount_sizer.Add(self.following_amount_label, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # follow button
        self.follow_button = rounded_button.RoundedButton(self, "Follow", settings.UNACTIVE_BUTTON, self.BG_COLOR)
        self.follow_button.SetMinSize((0, 30))
        self.follow_button.Hide()

        # change topics button
        self.change_topics_button = rounded_button.RoundedButton(self, "Change Topics", settings.THEME_COLOR, self.BG_COLOR)
        self.change_topics_button.SetMinSize((0, 30))
        self.change_topics_button.Hide()

        # add to info sizer
        info_sizer.Add(videos_amount_sizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 20)
        info_sizer.Add(followers_amount_sizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 20)
        info_sizer.Add(following_amount_sizer, 0, wx.ALIGN_CENTER_VERTICAL)

        # add to username_and_info sizer
        username_and_info_sizer.Add(self.username_label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 20)
        username_and_info_sizer.Add(info_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 20)
        username_and_info_sizer.Add(self.follow_button, 0, wx.EXPAND)
        username_and_info_sizer.Add(self.change_topics_button, 0, wx.EXPAND)

        profile_info_sizer.Add(self.pfp, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 20)
        profile_info_sizer.Add(username_and_info_sizer, 0, wx.ALIGN_CENTER_VERTICAL)

        # add to main sizer
        main_sizer.AddSpacer(10)
        main_sizer.Add(profile_info_sizer, 0, wx.EXPAND)
        main_sizer.AddSpacer(10)

        self.follow_button.Bind(wx.EVT_LEFT_UP, self.on_follow_user)
        self.change_topics_button.Bind(wx.EVT_LEFT_UP, self.on_change_topics)
        self.Bind(wx.EVT_SIZE, self.on_resize)

    def update_pfp(self):
        """
        Updates the profile picture bitmap if the current user has a local image file,
        falling back to the default placeholder if none is found.
        """
        if self.current_user:
            pfp_path = f"media\\{self.current_user.username}.png"
            if os.path.isfile(pfp_path):
                pfp = wx.Bitmap(wx.Image(pfp_path).Scale(128, 128))
            else:
                pfp = wx.Bitmap("assets\\null_pfp_high_quality.png")

            self.pfp.SetBitmap(pfp)
            self.pfp.Refresh()

        print("updated pfp in profile widget")

    def set_empty_user(self):
        """
        Sets the user to an empty state and hides relevant UI elements.

        This method modifies the current user by replacing it with an empty user
        object. Additionally, it hides the `follow_button` and
        `change_topics_button` UI elements to reflect the state change.

        """
        self.set_user(user.User("", 0, 0, [], False))

        self.follow_button.Hide()
        self.change_topics_button.Hide()



    def set_user(self, user):
        """
        Populates the widget with data from the given user, updates the profile picture,
        and conditionally binds the pfp click event if viewing the logged-in user's own profile.
        :param user: The user object whose profile data should be displayed.
        """
        self.current_user = user
        self.username_label.SetLabel(user.username)
        self.videos_numeric_amount_label.SetLabel(str(user.get_video_amount()))
        self.update_followings_label()
        self.update_followers_label()
        self.update_following(user.is_followed_by_user, user.username)
        self.update_pfp()

        self.pfp.Unbind(wx.EVT_LEFT_DOWN)

        if self.current_user.username == self.frame.user.username:
            self.pfp.Bind(wx.EVT_LEFT_DOWN, self.on_set_pfp)
            self.pfp.SetCursor(wx.Cursor(wx.CURSOR_HAND))
            self.follow_button.Hide()
            self.change_topics_button.Show()
        else:
            self.pfp.SetCursor(wx.Cursor(wx.CURSOR_DEFAULT))
            self.follow_button.Show()
            self.change_topics_button.Hide()

    def on_set_pfp(self, event):
        """
        Handles a click on the profile picture by delegating to the parent's on_set_pfp method.
        :param event: The wx mouse event triggered by clicking the profile picture.
        """
        self.parent.on_set_pfp()

    def on_follow_user(self, event):
        """
        Handles a click on the follow button by delegating to the parent's on_follow_user method.
        :param event: The wx mouse event triggered by clicking the follow button
        """
        self.parent.on_follow_user()

    def update_following(self, status, followed):
        """
        Updates the follow button state in the profile widget based on the
        current user's following status and the target user.

        :param status: The current follow status, e.g., following or not following.
        :param followed: The username of the user to check follow state against.
        """
        if followed == self.current_user.username:
            if status == settings.FOLLOWING:
                self.follow_button.label_or_path = "following"
                self.follow_button.set_active(True)
            else:
                self.follow_button.label_or_path = "follow"
                self.follow_button.set_active(False)

    def update_followings_label(self):
        """
        Updates the label displaying the number of followings for the current user.

        This method retrieves the current user's `followings_amount` and updates the
        associated label component to reflect the most recent value.

        """
        self.following_numeric_amount_label.SetLabel(str(self.current_user.followings_amount))

    def update_followers_label(self):
        """
        Updates the label displaying the total number of followers for the current user's profile
        widget. This method retrieves the current user's follower count and sets it to the
        corresponding label widget.

        """
        print("followers amount in profile widget:", str(self.current_user.followers_amount))
        self.followers_numeric_amount_label.SetLabel(str(self.current_user.followers_amount))

    def on_change_topics(self, event):
        """
        Handles a click on the follow button by delegating to the parent's on_change_topics method.
        :param event: The wx mouse event triggered by clicking the change topics button
        """
        self.parent.on_change_topics()

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
    panel = ProfileWidget(frame, frame)
    frame.Show()
    app.MainLoop()
