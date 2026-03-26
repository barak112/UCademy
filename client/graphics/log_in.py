from pubsub import pub

import clientProtocol
import wx

import main_frame
import rounded_button
import rounded_input_field
import settings


class LoginPanel(wx.Panel):
    LEFT_COLOR = settings.THEME_COLOR
    RIGHT_COLOR = settings.OFF_WHITE
    TEXT_BOX_BORDER_COLOR = (220, 220, 220)
    SUBTITLE_COLOR = (125, 120, 124)

    def __init__(self, frame, parent):
        super().__init__(parent)

        self.frame = frame
        self.parent = parent

        two_sides = wx.BoxSizer(wx.HORIZONTAL)

        left = wx.Panel(self)

        self.left = left

        self.background_bitmap = wx.Bitmap("assets\\blue_bg.png", wx.BITMAP_TYPE_PNG)
        left.SetMaxSize(self.background_bitmap.GetSize())
        left.Bind(wx.EVT_PAINT, self.on_paint)
        left.Bind(wx.EVT_SIZE, self.on_resize)

        icon_with_text = wx.Image("assets\\ucademy_log_in_logo_with_Text.png")
        icon_with_text = wx.Bitmap(icon_with_text)
        self.icon_with_text = icon_with_text


        # right panel (gray)
        right = wx.Panel(self)
        min_size = (630, 680)

        # right.SetMinSize(min_size)
        frame.SetMinSize(min_size)

        right.SetBackgroundColour(wx.Colour(self.RIGHT_COLOR))
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        right.SetSizer(right_sizer)

        horizontal_right = wx.Panel(right)
        horizontal_right_sizer = wx.BoxSizer(wx.HORIZONTAL)
        horizontal_right.SetSizer(horizontal_right_sizer)

        #centered form inside the big rect
        form = wx.Panel(horizontal_right)
        form.SetBackgroundColour(wx.Colour(self.RIGHT_COLOR))
        form_sizer = wx.BoxSizer(wx.VERTICAL)
        form.SetSizer(form_sizer)

        #title
        title = wx.StaticText(form, label="Welcome Back              ")
        font = title.GetFont()
        font = font.Bold().Scale(4)
        title.SetFont(font)
        form_sizer.Add(title, 0, wx.BOTTOM, 10)


        #subtitle
        subtitle = wx.StaticText(form, label="Log in to continue learning")
        font = subtitle.GetFont()
        font = font.Scale(1.5)
        subtitle.SetForegroundColour(wx.Colour(self.SUBTITLE_COLOR))
        subtitle.SetFont(font)
        form_sizer.Add(subtitle, 0, wx.BOTTOM, 30)


        # status message
        self.status_message = wx.StaticText(form)
        font = self.status_message.GetFont()
        font = font.Scale(1.5)
        self.status_message.SetForegroundColour(wx.Colour(self.SUBTITLE_COLOR))
        self.status_message.SetFont(font)
        self.status_message.SetForegroundColour(wx.RED)


        #login button
        login_button = rounded_button.RoundedButton(form, "Log In", self.LEFT_COLOR)
        login_button.SetMinSize((0, 50))
        login_button.Bind(wx.EVT_LEFT_DOWN, self.on_login)

        # move to sign up label

        no_account_label = wx.StaticText(form, label="Dont have an account?")
        sign_up = wx.StaticText(form, label = "sign up")
        sign_up.SetForegroundColour(wx.BLUE)
        sign_up.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        sign_up.Bind(wx.EVT_LEFT_DOWN, self.on_move_to_sign_up)

        sign_up_container = wx.BoxSizer(wx.HORIZONTAL)
        sign_up_container.Add(no_account_label)
        sign_up_container.Add(sign_up)

        username_icon_img = wx.Image("assets\\username_icon.png", wx.BITMAP_TYPE_PNG)
        password_icon_img = wx.Image("assets\\password_icon.png", wx.BITMAP_TYPE_PNG)

        username_icon = wx.Bitmap(username_icon_img)
        password_icon = wx.Bitmap(password_icon_img)

        user_sizer, self.username_input_obj = self.labeled_input("Username", form, "Enter your username or email", username_icon)
        pass_sizer, self.password_input_obj = self.labeled_input("Password", form, "Enter your password", password_icon, True)

        self.username_input_obj.get_text_visible().Bind(wx.EVT_KEY_DOWN, self.entering_text)

        self.password_input_obj.get_text_visible().Bind(wx.EVT_KEY_DOWN, self.entering_text)
        self.password_input_obj.get_text_hidden().Bind(wx.EVT_KEY_DOWN, self.entering_text)


        form_sizer.Add(user_sizer, 0, wx.EXPAND | wx.BOTTOM | wx.TOP, 30)

        form_sizer.Add(pass_sizer, 0, wx.EXPAND | wx.BOTTOM, 35)

        form_sizer.Add(self.status_message, 0, wx.ALIGN_CENTER_HORIZONTAL)

        form_sizer.Add(login_button, 0, wx.EXPAND | wx.TOP, 40)


        form_sizer.Add(sign_up_container, 0, wx.TOP | wx.ALIGN_CENTER_HORIZONTAL, 20)

        horizontal_right_sizer.AddStretchSpacer(2)
        horizontal_right_sizer.Add(form, 0, wx.EXPAND)
        horizontal_right_sizer.AddStretchSpacer(2)

        right_sizer.AddStretchSpacer()  # push down
        right_sizer.Add(horizontal_right, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 50)  # center horizontally
        right_sizer.AddStretchSpacer()  # push up

        # add to panels to screen
        two_sides.Add(left, 1, wx.EXPAND)

        two_sides.Add(right, 1, wx.EXPAND)
        self.SetSizer(two_sides)
        self.Hide()

        pub.subscribe(self.on_login_response, "login_ans")

        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)

    def entering_text(self, event):
        print("entering text")
        self.status_message.SetLabel("")
        event.Skip()

    def on_resize(self, event):
        self.Refresh()  # trigger repaint
        event.Skip()

    def on_paint(self, event):
        dc = wx.BufferedPaintDC(self.left)
        dc.DrawBitmap(self.background_bitmap, 0, 0)

        left_width, left_height, = self.left.GetSize()

        icon_width, icon_height = self.icon_with_text.GetSize()
        x = (left_width - icon_width) // 2
        y = (left_height - icon_height) // 2

        dc.DrawBitmap(self.icon_with_text, x, y, True)

    @staticmethod
    def labeled_input(label_text, parent, placeholder, image_bitmap, is_password = False):
        sizer = wx.BoxSizer(wx.VERTICAL)
        # label above box
        label = wx.StaticText(parent, label=label_text)
        font = label.GetFont()
        font = font.Scale(1.5)
        label.SetFont(font)

        text_box = rounded_input_field.RoundedInputField(parent, placeholder, image_bitmap, is_password)

        sizer.Add(label)
        sizer.Add(text_box, 0, wx.EXPAND)
        return sizer, text_box


    def on_key(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:
            exit()
        elif keycode == wx.WXK_RETURN:
            self.on_login(None)

        event.Skip()

    def on_login(self, event):
        # Assume validation is done elsewhere
        username = self.username_input_obj.get_value()
        password = self.password_input_obj.get_value()

        print("credentials at login", username, password)

        if username and password:
            msg2send = clientProtocol.build_sign_in(username, password)
            self.frame.comm.send_msg(msg2send)
        else:
            self.status_message.SetLabel("you must enter both username and password to log in")
            self.Layout()

    def on_login_response(self, status, video=None, user=None):
        if status:
            self.frame.video = video
            self.frame.user = user
            self.frame.switch_panel(self.frame.feed_panel, self)

            print("in login resp,", self.frame.user)

        else:
            self.status_message.SetLabel("username or password incorrect")
            self.Layout()

    def on_move_to_sign_up(self, event):
        self.frame.switch_panel(self.frame.signup_panel, self)
