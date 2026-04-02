import wx
from pubsub import pub

import clientProtocol
import rounded_button
import settings
import theme_background_panel
import verification_code_cubes

class EmailVerification(wx.Panel):
    # graphics constants
    LEFT_COLOR = settings.THEME_COLOR
    RIGHT_COLOR = settings.OFF_WHITE
    SUBTITLE_COLOR = settings.SUBTITLE_COLOR

    def __init__(self, frame, parent):
        super().__init__(parent)

        self.frame = frame
        self.parent = parent

        # distributes the screen to left and right
        two_sides = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(two_sides)

        # the self.right panel - including the log-in form
        self.right = wx.Panel(self)

        min_size = (630, 680)
        frame.SetMinSize(min_size)

        # right background color -> off-white
        self.right.SetBackgroundColour(wx.Colour(self.RIGHT_COLOR))

        # right side sizer -> contains stretchers and horizontal_right which contains form
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        self.right.SetSizer(right_sizer)

        # horizontal_right -> contains form and stretchers, keeps form horizontally centered inside right
        horizontal_right = wx.Panel(self.right)
        horizontal_right_sizer = wx.BoxSizer(wx.HORIZONTAL)
        horizontal_right.SetSizer(horizontal_right_sizer)

        # form -> contains all the credentials fields and buttons
        form = wx.Panel(horizontal_right)
        form.SetBackgroundColour(wx.Colour(self.RIGHT_COLOR))

        # form sizer
        form_sizer = wx.BoxSizer(wx.VERTICAL)
        form.SetSizer(form_sizer)

        # --- form widgets ---

        # email ver icon
        icon = wx.StaticBitmap(form, bitmap=wx.Bitmap("assets\\email_verification_icon.png"))

        # title
        title = wx.StaticText(form, label="       Verify Your Email       ")
        font = title.GetFont()
        font = font.Bold().Scale(4)
        title.SetFont(font)

        # subtitle
        subtitle = wx.StaticText(form, label="We've sent a 6-digit verification code to your email")
        font = subtitle.GetFont()
        font = font.Scale(1.5)
        # subtitle.SetForegroundColour(wx.Colour(self.SUBTITLE_COLOR))
        subtitle.SetFont(font)

        # verification code label
        enter_ver_code_label = wx.StaticText(form, label="Enter verification code")
        font = enter_ver_code_label.GetFont()
        font = font.Scale(1.2)
        font = font.Bold()
        enter_ver_code_label.SetFont(font)

        # verification code cubes
        #todo implement verification_code_cubes
        # ver_code_cubes = verification_code_cubes.VerificationCodeCubes(form)

        # status message
        self.status_message = wx.StaticText(form)
        font = self.status_message.GetFont()
        font = font.Scale(1.5)
        self.status_message.SetForegroundColour(wx.Colour(self.SUBTITLE_COLOR))
        self.status_message.SetFont(font)
        self.status_message.SetForegroundColour(wx.RED)

        # verify email button
        self.verify_email_button = rounded_button.RoundedButton(form, "Verify Email", self.LEFT_COLOR)
        self.verify_email_button.SetMinSize((0, 50))
        self.verify_email_button.Bind(wx.EVT_LEFT_UP, self.on_email_verification)

        # didnt recv code label
        didnt_recv_code = wx.StaticText(form, label="Didn't recieve the code?")
        resend = wx.StaticText(form, label="resend")
        resend.SetForegroundColour(wx.BLUE)
        resend.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        resend.Bind(wx.EVT_LEFT_UP, self.on_resend_code)

        didnt_recv_code_container = wx.BoxSizer(wx.HORIZONTAL)
        didnt_recv_code_container.Add(didnt_recv_code)
        didnt_recv_code_container.Add(resend)


        # back to sign up label

        back_to_sign_up = wx.StaticText(form, label="← Back to sign up")
        font = back_to_sign_up.GetFont()
        font = font.Bold()
        back_to_sign_up.SetFont(font)
        back_to_sign_up.Bind(wx.EVT_LEFT_UP, self.on_back_to_sign_up)
        back_to_sign_up.SetCursor(wx.Cursor(wx.CURSOR_HAND))

        # add all form widgets to form_sizer
        form_sizer.Add(icon, 0, wx.ALIGN_CENTER_HORIZONTAL)
        form_sizer.Add(title, 0, wx.BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, 10)

        form_sizer.Add(subtitle, 0, wx.BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, 30)

        form_sizer.Add(self.status_message, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP | wx.BOTTOM, 40)

        form_sizer.Add(enter_ver_code_label, 0 , wx.ALIGN_CENTER_HORIZONTAL)

        form_sizer.Add(self.verify_email_button, 0, wx.EXPAND)

        form_sizer.Add(didnt_recv_code_container, 0, wx.TOP | wx.ALIGN_CENTER_HORIZONTAL, 20)

        form_sizer.Add(back_to_sign_up, 0, wx.Top | wx.ALIGN_CENTER_HORIZONTAL, 20)

        # center form horizontally
        horizontal_right_sizer.AddStretchSpacer(2)
        horizontal_right_sizer.Add(form, 0, wx.EXPAND)
        horizontal_right_sizer.AddStretchSpacer(2)

        # center form vertically
        right_sizer.AddStretchSpacer()  # push down
        right_sizer.Add(horizontal_right, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 50)  # center horizontally
        right_sizer.AddStretchSpacer()  # push up

        # add both left and self.right panels to the screen
        ucademy_icon = wx.Bitmap("assets\\ucademy_log_in_logo_with_Text.png")
        self.left = theme_background_panel.ThemeBackgroundPanel(self, ucademy_icon)
        two_sides.Add(self.left, 1, wx.EXPAND)
        two_sides.Add(self.right, 1, wx.EXPAND)

        # handles logic response to log in
        pub.subscribe(self.on_email_verification_ans, "email_verification_ans")

        # handles key press
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)
        # handle background disappearance
        self.Bind(wx.EVT_SIZE, self.on_resize)

        self.Hide()

    def on_resize(self, event):
        if self.GetSize()[0] - self.right.GetSize()[0] == 1:
            self.left.Hide()
        else:
            self.left.Show()
        event.Skip()

    def on_key(self, event):
        """checks for keys pressed, exists on Escape, log in on Enter"""
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:
            exit()
        elif keycode == wx.WXK_RETURN:
            self.on_email_verification(None)

        event.Skip()

    def on_back_to_sign_up(self, event):
        print("back to sign up")
        self.frame.switch_panel(self.frame.signup_panel, self)

    def on_verification_code_resend(self, event):
        print("sending verification code again using frame.comm")

    def on_email_verification(self, event):
        print("entered ver code")
        if event:
            event.Skip()

    def on_email_verification_ans(self, status):
        print("email ver status:", status)

    def on_resend_code(self, event):
        print("resending code")
        pass
