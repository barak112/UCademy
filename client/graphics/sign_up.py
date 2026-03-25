from pubsub import pub

import clientProtocol
import wx

import rounded_button
import settings


class SignupPanel(wx.Panel):
    LEFT_COLOR = (56, 65, 237)
    RIGHT_COLOR = (249, 250, 251)
    TEXT_BOX_BORDER_COLOR = (220, 220, 220)
    SUBTITLE_COLOR = (125, 120, 124)
    PLACE_HOLER_COLOR = (135, 140, 144)

    def __init__(self, frame, parent):
        super().__init__(parent)

        self.frame = frame
        self.parent = parent

        two_sides = wx.BoxSizer(wx.HORIZONTAL)

        # Left panel (blue)
        left = wx.Panel(self)
        left.SetBackgroundColour(wx.Colour(self.LEFT_COLOR))

        # right panel (gray)
        right = wx.Panel(self)
        right.SetBackgroundColour(wx.Colour(self.RIGHT_COLOR))
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        right.SetSizer(right_sizer)

        horizontal_right = wx.Panel(right)
        horizontal_right_sizer = wx.BoxSizer(wx.HORIZONTAL)
        horizontal_right.SetSizer(horizontal_right_sizer)

        # centered form inside the big rect
        form = wx.Panel(horizontal_right)
        form.SetBackgroundColour(wx.Colour(self.RIGHT_COLOR))
        form_sizer = wx.BoxSizer(wx.VERTICAL)
        form.SetSizer(form_sizer)

        # title
        title = wx.StaticText(form, label="Create Account             ")
        font = title.GetFont()
        font = font.Bold().Scale(4)
        title.SetFont(font)
        form_sizer.Add(title, 0, wx.BOTTOM, 10)

        # subtitle
        subtitle = wx.StaticText(form, label="Sign up to get started")
        font = subtitle.GetFont()
        font = font.Scale(1.5)
        subtitle.SetForegroundColour(wx.Colour(self.SUBTITLE_COLOR))
        subtitle.SetFont(font)
        form_sizer.Add(subtitle, 0, wx.BOTTOM, 20)

        # signup button

        signup_button = rounded_button.RoundedButton(form, "Sign Up", self.LEFT_COLOR)
        signup_button.SetMinSize((0, 50))

        # move to sign up label

        no_account_label = wx.StaticText(form, label="Already have an account?")
        log_in = wx.StaticText(form, label="Log in")
        log_in.SetForegroundColour(wx.BLUE)
        log_in.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        log_in.Bind(wx.EVT_LEFT_DOWN, self.on_login)

        log_in_container = wx.BoxSizer(wx.HORIZONTAL)
        log_in_container.Add(no_account_label)
        log_in_container.Add(log_in)

        username_icon_img = wx.Image("assets\\username_icon.png", wx.BITMAP_TYPE_PNG)
        email_icon_img = wx.Image("assets\\email_icon.png", wx.BITMAP_TYPE_PNG)
        password_icon_img = wx.Image("assets\\password_icon.png", wx.BITMAP_TYPE_PNG)

        username_icon = wx.Bitmap(username_icon_img)
        email_icon = wx.Bitmap(email_icon_img)
        password_icon = wx.Bitmap(password_icon_img)

        user_sizer, self.username = self.labeled_input("Username", form, "Enter your username", username_icon)
        email_sizer, self.email = self.labeled_input("Email", form, "Enter your email", email_icon)
        password_sizer, self.password = self.labeled_input("Password", form, "Create a password", password_icon)

        form_sizer.Add(user_sizer, 0, wx.EXPAND | wx.BOTTOM | wx.TOP, 10)
        form_sizer.Add(email_sizer, 0, wx.EXPAND | wx.BOTTOM | wx.TOP, 10)
        form_sizer.Add(password_sizer, 0, wx.EXPAND | wx.BOTTOM | wx.TOP, 10)

        form_sizer.Add(signup_button, 0, wx.EXPAND | wx.TOP, 50)
        form_sizer.Add(log_in_container, 0, wx.TOP | wx.ALIGN_CENTER_HORIZONTAL, 20)

        horizontal_right_sizer.AddStretchSpacer()
        horizontal_right_sizer.Add(form, 0, wx.EXPAND)
        horizontal_right_sizer.AddStretchSpacer()

        right_sizer.AddStretchSpacer()  # push down
        right_sizer.Add(horizontal_right, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 40)  # center horizontally
        right_sizer.AddStretchSpacer()  # push up

        # add to panels to screen
        two_sides.Add(left, 1, wx.EXPAND)
        two_sides.Add(right, 1, wx.EXPAND)
        self.SetSizer(two_sides)

        self.Hide()

        pub.subscribe(self.on_signup_response, "signup_ans")

        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)

    def labeled_input(self, label_text, parent, placeholder, image_bitmap):
        sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(parent, label=label_text)

        # whole box panel
        box = wx.Panel(parent)
        box.SetBackgroundColour(wx.Colour(self.TEXT_BOX_BORDER_COLOR))  # border color
        inner = wx.BoxSizer(wx.VERTICAL)

        #
        image_and_text = wx.Panel(box)
        image_and_text_sizer = wx.BoxSizer(wx.HORIZONTAL)
        image_and_text.SetBackgroundColour(wx.Colour(self.RIGHT_COLOR))
        image_and_text.SetSizer(image_and_text_sizer)

        text = wx.TextCtrl(image_and_text, style=wx.BORDER_NONE, size=(100, 45))  # parent = box now!
        text.SetBackgroundColour(wx.Colour(self.RIGHT_COLOR))
        font = text.GetFont()
        font = font.Scale(1.5)
        text.SetFont(font)
        text.SetHint(placeholder)
        image = wx.StaticBitmap(image_and_text, bitmap=image_bitmap)
        image.SetBackgroundColour(wx.Colour(self.RIGHT_COLOR))
        image_and_text_sizer.Add(image, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 20)
        image_and_text_sizer.Add(text, 1, wx.TOP, 20)

        inner.Add(image_and_text, 1, wx.EXPAND | wx.ALL, 1)
        box.SetSizer(inner)

        sizer.Add(label, 0, wx.BOTTOM, 8)
        sizer.Add(box, 0, wx.EXPAND)

        return sizer, text

    def on_key(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:
            exit()
        elif keycode == wx.WXK_RETURN:
            self.on_signup(None)

        event.Skip()

    def on_login(self, event):
        self.frame.switch_panel(self.frame.login_panel, self)

    def on_signup(self, event):
        # Assume validation is done elsewhere
        username = self.username.GetValue()
        email = self.email.GetValue()
        password = self.password.GetValue()

        print("credentials at signup", username, password, email)

        if username and password:
            msg2send = clientProtocol.build_sign_up(username, password, email)
            self.frame.comm.send_msg(msg2send)
        else:
            self.frame.change_text_status("you must enter ...")

    def on_signup_response(self, status):
        if not any(status):
            self.frame.change_text_status("an email verification code has been sent to the user's email account")
            self.frame.switch_panel(self.frame.email_verification, self)
        else:
            username_status, password_status, email_status = status
            if username_status:
                self.frame.change_text_status("username error: ",settings.USERNAME_ERRORS[username_status])
            if password_status:
                self.frame.change_text_status("password error: ", settings.PASSWORD_ERRORS[password_status])
            if email_status:
                self.frame.change_text_status("email error: ", settings.EMAIL_ERRORS[email_status])
