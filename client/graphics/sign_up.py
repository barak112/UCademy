from pubsub import pub

import clientProtocol
import wx

import rounded_button
import rounded_input_field
import settings
import theme_background_panel


class SignupPanel(wx.Panel):
    LEFT_COLOR = settings.THEME_COLOR
    RIGHT_COLOR = settings.OFF_WHITE
    SUBTITLE_COLOR = settings.SUBTITLE_COLOR

    #todo change subtitle color

    def __init__(self, frame, parent):
        """Sign up screen initialization"""
        super().__init__(parent)

        self.frame = frame
        self.parent = parent

        self.temp_username = ""
        self.temp_email = ""
        self.temp_password = ""

        # distributes the screen to left and right
        two_sides = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(two_sides)

        # the right panel - including the sign-up form
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

        # title
        title = wx.StaticText(form, label="Create Account             ")
        font = title.GetFont()
        font = font.Bold().Scale(4)
        title.SetFont(font)

        # subtitle
        subtitle = wx.StaticText(form, label="Sign up to get started")
        font = subtitle.GetFont()
        font = font.Scale(1.5)
        subtitle.SetForegroundColour(wx.Colour(self.SUBTITLE_COLOR))
        subtitle.SetFont(font)

        # username and password fields

        # field icons
        username_icon = wx.Bitmap("assets\\username_icon.png", wx.BITMAP_TYPE_PNG)
        email_icon = wx.Bitmap("assets\\email_icon.png", wx.BITMAP_TYPE_PNG)
        password_icon = wx.Bitmap("assets\\password_icon.png", wx.BITMAP_TYPE_PNG)

        # field sizers containing labels, borders and ctrltext
        user_sizer, self.username_input_obj = self.labeled_input("Username", form, "Enter your username or email",
                                                                 username_icon)
        email_sizer, self.email_input_obj = self.labeled_input("Email", form, "Enter your email", email_icon)

        password_sizer, self.password_input_obj = self.labeled_input("Password", form, "Enter your password",
                                                                     password_icon, True)
        self.filled_fields = {"Username":0, "Email":0, "Password":0}

        # whenever one of the fields is being written to, make status message disappear
        self.username_input_obj.get_text_visible().Bind(wx.EVT_KEY_DOWN, self.entering_text)
        self.email_input_obj.get_text_visible().Bind(wx.EVT_KEY_DOWN, self.entering_text)

        self.password_input_obj.get_text_visible().Bind(wx.EVT_KEY_DOWN, self.entering_text)
        self.password_input_obj.get_text_hidden().Bind(wx.EVT_KEY_DOWN, self.entering_text)

        # status message
        self.status_message = wx.StaticText(form)
        font = self.status_message.GetFont()
        font = font.Scale(1.5)
        self.status_message.SetForegroundColour(wx.Colour(self.SUBTITLE_COLOR))
        self.status_message.SetFont(font)
        self.status_message.SetForegroundColour(wx.RED)

        # signup button
        self.signup_button = rounded_button.RoundedButton(form, "Sign up", settings.UNACTIVE_BUTTON)
        self.signup_button.Bind(wx.EVT_LEFT_UP, self.on_signup)

        # move to log in label
        already_have_an_account = wx.StaticText(form, label="Already have an account?")
        sign_up = wx.StaticText(form, label="Log in")
        sign_up.SetForegroundColour(wx.BLUE)
        sign_up.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        sign_up.Bind(wx.EVT_LEFT_UP, self.on_move_to_log_in)

        sign_up_container = wx.BoxSizer(wx.HORIZONTAL)
        sign_up_container.Add(already_have_an_account)
        sign_up_container.Add(sign_up)

        # add all form widgets to form_sizer
        form_sizer.Add(title, 0, wx.BOTTOM, 10)

        form_sizer.Add(subtitle, 0, wx.BOTTOM, 30)

        form_sizer.Add(user_sizer, 0, wx.EXPAND)
        form_sizer.Add(email_sizer, 0, wx.EXPAND | wx.BOTTOM | wx.TOP, 30)
        form_sizer.Add(password_sizer, 0, wx.EXPAND)

        form_sizer.Add(self.status_message, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP | wx.BOTTOM, 20)

        form_sizer.Add(self.signup_button, 0, wx.EXPAND)

        form_sizer.Add(sign_up_container, 0, wx.TOP | wx.ALIGN_CENTER_HORIZONTAL, 20)

        # center form horizontally
        horizontal_right_sizer.AddStretchSpacer(2)
        horizontal_right_sizer.Add(form, 0, wx.EXPAND)
        horizontal_right_sizer.AddStretchSpacer(2)

        # center form vertically
        right_sizer.AddStretchSpacer()  # push down
        right_sizer.Add(horizontal_right, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 50)  # center horizontally
        right_sizer.AddStretchSpacer()  # push up

        # add both left and right panels to the screen
        ucademy_icon = wx.Bitmap(wx.Image("assets\\ucademy_sign_up_logo_with_Text.png"))
        self.left = theme_background_panel.ThemeBackgroundPanel(self, ucademy_icon)
        two_sides.Add(self.left, 1, wx.EXPAND)
        two_sides.Add(self.right, 1, wx.EXPAND)

        # handles logic response to sign up
        pub.subscribe(self.on_signup_response, "signup_ans")

        # handles key press
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)
        # handle background disappearance
        self.Bind(wx.EVT_SIZE, self.on_resize)

        self.Hide()

    def set_fields(self, username, password, email = None):
        self.username_input_obj.set_value(username)
        self.password_input_obj.set_value(password)
        if email:
            self.email_input_obj.set_value(email)

    def field_is_filled(self, field_name):
        self.filled_fields[field_name] = 1
        if all(self.filled_fields.values()):
            self.signup_button.set_active(True)
        self.signup_button.Refresh()

    def field_is_unfilled(self, field_name):
        self.filled_fields[field_name] = 0
        self.signup_button.set_active(False)
        self.signup_button.Refresh()

    def entering_text(self, event):
        """whenever one of the credentials fields is being written to, deletes status message"""
        if not any((self.temp_username, self.temp_email, self.temp_password)):
            self.status_message.SetLabel("")
        event.Skip()

    def on_resize(self, event):
        if self.GetSize()[0] - self.right.GetSize()[0] == 1:
            self.left.Hide()
        else:
            self.left.Show()
        event.Skip()


    def labeled_input(self, label_text, parent, placeholder, field_icon_bitmap, is_password=False):
        """
            creates a credentials field with a textctrl with a placeholder, a label, a rounded border around him, and an icon representing him
        :param label_text: the field label
        :param parent: parent to add this field to (form)
        :param placeholder: placeholder for the textctrl
        :param field_icon_bitmap: bitmap of the image of the icon that represents the field
        :param is_password: whether the field is a password
        :return: the sizer containing the label and the field, the text box containing the field, its border and its icon
        """
        sizer = wx.BoxSizer(wx.VERTICAL)
        # label above box
        label = wx.StaticText(parent, label=label_text)
        font = label.GetFont()
        font = font.Scale(1.5)
        label.SetFont(font)

        text_box = rounded_input_field.RoundedInputField(self,parent, label_text,placeholder, field_icon_bitmap, is_password)

        sizer.Add(label)
        sizer.Add(text_box, 0, wx.EXPAND)
        return sizer, text_box

    def on_key(self, event):
        """checks for keys pressed, exists on Escape, sign up on Enter"""
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:
            exit()
        elif keycode == wx.WXK_RETURN:
            self.on_signup(None)

        event.Skip()

    def on_signup(self, event):
        """checks that all credentials are inputted and sends them to the server"""
        # either event = None (enter pressed) or the mouse was inside the button once released
        if not event or self.signup_button.GetClientRect().Contains(event.GetPosition()):
            username = self.username_input_obj.get_value()
            email = self.email_input_obj.get_value()
            password = self.password_input_obj.get_value()

            print("credentials at signup", username, password, email)

            if all((username, email, password)):
                # if temp credentials are already set, it means that the client is waiting for a response from the server
                if not any((self.temp_username, self.temp_email, self.temp_password)):
                    msg2send = clientProtocol.build_sign_up(username, password, email)
                    self.frame.comm.send_msg(msg2send)
                    self.status_message.SetLabel("sending credentials to the server...")

                    self.temp_username = username
                    self.temp_email = email
                    self.temp_password = password
            else:
                self.status_message.SetLabel("you must enter all credentials to sign up")

        self.Layout()

        if event:
            event.Skip()

    def on_signup_response(self, status):
        """handles response to sign up from the server, either moves to the email verification panel or shows an error message"""
        if not any(status):
            if self.frame.email_verification_panel.IsShown():
                self.frame.email_verification_panel.status_message.SetLabel("A new email verification code has been sent to your email account")
            else:
                # set fields to the temporary credentials set at the sign up, those are the credentials that were actually sent to the server
                self.set_fields(self.temp_username, self.temp_password, self.temp_email)
                self.frame.switch_panel(self.frame.email_verification_panel, self) # move to email verification panel
                self.frame.email_verification_panel.set_email(self.temp_email)
        else:
            if self.frame.email_verification_panel.IsShown(): # if an error response from a resent code
                self.frame.switch_panel(self, self.frame.email_verification_panel) # return to sign up panel

            username_status, password_status, email_status = status
            if username_status:
                self.status_message.SetLabel("username error: "+ settings.USERNAME_ERRORS[username_status])
            if password_status:
                self.status_message.SetLabel(f"password error: "+ settings.PASSWORD_ERRORS[password_status])
            if email_status:
                self.status_message.SetLabel("email error: " + settings.EMAIL_ERRORS[email_status])

        # delete temporary credentials set at the sign up
        self.temp_username = ""
        self.temp_email = ""
        self.temp_password = ""
        self.Layout()

    def on_move_to_log_in(self, event):
        self.frame.switch_panel(self.frame.login_panel, self)
        self.frame.login_panel.set_fields(self.username_input_obj.get_value(), self.password_input_obj.get_value())
