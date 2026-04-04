import time

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

        self.waiting_for_server_response = False
        self.frame = frame
        self.parent = parent

        self.email = ""

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
        title = wx.StaticText(form, label="     Verify Your Email     ")
        font = title.GetFont()
        font = font.Bold().Scale(4)
        title.SetFont(font)

        # subtitle
        subtitle = wx.StaticText(form, label="We've sent a 6-digit verification code to your email")
        font = subtitle.GetFont()
        font = font.Scale(1.5)
        # subtitle.SetForegroundColour(wx.Colour(self.SUBTITLE_COLOR))
        subtitle.SetFont(font)

        # email code was sent to
        self.email_label = wx.StaticText(form)
        # self.email_label = wx.StaticText(form, label=self.frame.signup_panel.email_input_obj.get_value())
        font = self.email_label.GetFont()
        font = font.Bold().Scale(1.5)
        self.email_label.SetFont(font)

        # verification code label
        enter_ver_code_label = wx.StaticText(form, label="Enter verification code")
        font = enter_ver_code_label.GetFont()
        font = font.Scale(1.5)
        font = font.Bold()
        enter_ver_code_label.SetFont(font)

        # verification code cubes
        self.ver_code_cubes = verification_code_cubes.VerificationCodeCubes(self, form)

        # status message
        self.status_message = wx.StaticText(form)
        font = self.status_message.GetFont()
        font = font.Scale(1.5)
        self.status_message.SetForegroundColour(wx.Colour(self.SUBTITLE_COLOR))
        self.status_message.SetFont(font)
        self.status_message.SetForegroundColour(wx.RED)

        # verify email button
        self.verify_email_button = rounded_button.RoundedButton(form, "Verify Email", wx.Colour(settings.UNACTIVE_BUTTON))
        self.verify_email_button.Bind(wx.EVT_LEFT_UP, self.on_email_verification)

        # didnt recv code label
        didnt_recv_code = wx.StaticText(form, label="Didn't receive the code?")
        resend = wx.StaticText(form, label="resend")
        font = didnt_recv_code.GetFont()
        resend.SetFont(font)
        didnt_recv_code.SetFont(font)
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
        form_sizer.Add(title, 0, wx.BOTTOM | wx.TOP | wx.ALIGN_CENTER_HORIZONTAL, 10)

        form_sizer.Add(subtitle, 0, wx.BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, 10)

        form_sizer.Add(self.email_label, 0, wx.BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, 75)

        form_sizer.Add(enter_ver_code_label, 0, wx.BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, 20)

        form_sizer.Add(self.ver_code_cubes, 0, wx.ALIGN_CENTER_HORIZONTAL)

        form_sizer.Add(self.status_message, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP | wx.BOTTOM, 35)


        form_sizer.Add(self.verify_email_button, 0, wx.EXPAND)

        form_sizer.Add(didnt_recv_code_container, 0, wx.TOP | wx.ALIGN_CENTER_HORIZONTAL, 20)

        form_sizer.Add(back_to_sign_up, 0, wx.TOP | wx.ALIGN_CENTER_HORIZONTAL, 10)

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
        # ucademy_icon = wx.Bitmap("assets\\try1.png")
        #todo get a new icon here.
        # or change it totally to drawing the icon and writing the text instead of displaying a picture featuring both

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

    def verification_code_full(self):
        self.verify_email_button.set_background_color(self.LEFT_COLOR)
        self.verify_email_button.Refresh()


    def verification_code_not_full(self):
        self.verify_email_button.set_background_color(settings.UNACTIVE_BUTTON)
        self.verify_email_button.Refresh()
        if not self.waiting_for_server_response:
            self.status_message.SetLabel("")

    def on_back_to_sign_up(self, event):
        self.frame.switch_panel(self.frame.signup_panel, self)

    def set_email(self, email):
        self.email_label.SetLabel(email)

    def on_email_verification(self, event):
        print("entered ver code")
        self.status_message.SetLabel("Sending verification code...")
        if not self.waiting_for_server_response:
            msg = clientProtocol.build_email_verification_code(self.ver_code_cubes.get_value())
            self.frame.comm.send_msg(msg)
            self.waiting_for_server_response = True
        if event:
            event.Skip()

    def on_email_verification_ans(self, status, video_comm = None, user = None):
        print("email ver status:", status)
        if status == settings.EMAIL_VERIFICATION_SUCCESSFUL:
            print("moving to next screen")
            self.frame.video_comm = video_comm
            self.frame.user = user
            print("videocomm:",video_comm)
            print("user:",user)
            # self.frame.switch_panel(self.frame.pick_topics_panel, self)
        else:
            self.status_message.SetLabel(settings.EMAIL_VERIFICATION_ERRORS[status])
            if status in [settings.EMAIL_VERIFICATION_CODE_EXPIRED, settings.EMAIL_VERIFICATION_CREDENTIALS_TAKEN]:
                time.sleep(2)
                self.frame.switch_panel(self.frame.signup_panel, self)
            self.Layout()
        self.waiting_for_server_response = False

    def on_resend_code(self, event):
        self.status_message.SetLabel("Resending code...")
        self.frame.signup_panel.on_signup(None)
