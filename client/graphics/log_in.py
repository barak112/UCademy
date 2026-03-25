from pubsub import pub

import clientProtocol
import wx

import rounded_button
import rounded_text_box
import settings


class LoginPanel(wx.Panel):
    LEFT_COLOR = settings.THEME_COLOR
    RIGHT_COLOR = (249, 250, 251)
    TEXT_BOX_BORDER_COLOR = (220, 220, 220)
    SUBTITLE_COLOR = (125, 120, 124)

    def __init__(self, frame, parent):
        super().__init__(parent)

        self.frame = frame
        self.parent = parent

        two_sides = wx.BoxSizer(wx.HORIZONTAL)

        left = wx.Panel(self)

        self.left = left

        background_img = wx.Image("assets\\blue_background_960x1080.png")
        self.background_bitmap = wx.Bitmap(background_img)
        left.Bind(wx.EVT_PAINT, self.on_paint)
        left.Bind(wx.EVT_SIZE, self.on_resize)

        icon_with_text = wx.Image("assets\\icon_with_text.png")
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
        form_sizer.Add(subtitle, 0, wx.BOTTOM, 60)

        #login button

        login_button = rounded_button.RoundedButton(form, "Log In", self.LEFT_COLOR)
        login_button.SetMinSize((0, 50))

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

        user_sizer, self.username = self.labeled_input("Username", form, "Enter your username or email", username_icon)
        pass_sizer, self.password = self.labeled_input("Password", form, "Enter your password", password_icon)

        form_sizer.Add(user_sizer, 0, wx.EXPAND | wx.BOTTOM | wx.TOP, 15)

        form_sizer.Add(pass_sizer, 0, wx.EXPAND | wx.BOTTOM | wx.TOP, 15)

        form_sizer.Add(login_button, 0, wx.EXPAND | wx.TOP, 60)
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


    # def labeled_input(self, label_text, parent, placeholder, image_bitmap):
    #     sizer = wx.BoxSizer(wx.VERTICAL)
    #     # label above box
    #     label = wx.StaticText(parent, label=label_text)
    #     font = label.GetFont()
    #     font = font.Scale(1.5)
    #     label.SetFont(font)
    #
    #     text_box = rounded_text_box.RoundedTextBox(parent, placeholder, image_bitmap)
    #     input_text = text_box.get_text_ctrl()
    #
    #     sizer.Add(label)
    #     sizer.Add(text_box)
    #
    #     return sizer, input_text

    def labeled_input(self, label_text, parent, placeholder, image_bitmap):
        sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(parent, label=label_text)
        font = label.GetFont()
        font = font.Scale(1.5)
        label.SetFont(font)

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
        sizer.Add(box, 0, wx.EXPAND | wx.BOTTOM, 20)

        return sizer, text

    def on_key(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:
            exit()
        elif keycode == wx.WXK_RETURN:
            self.on_login(None)

        event.Skip()

    def on_login(self, event):
        # Assume validation is done elsewhere
        username = self.username.GetValue()
        password = self.password.GetValue()

        print("credentials at login", username, password)

        if username and password:
            msg2send = clientProtocol.build_sign_in(username, password)
            self.frame.comm.send_msg(msg2send)
        else:
            self.frame.change_text_status("you must enter both username and password to log in")


    def on_login_response(self, status, video=None, user=None):
        if status:
            self.frame.video = video
            self.frame.user = user
            self.frame.switch_panel(self.frame.feed_panel, self)

            print("in login resp,", self.frame.user)

        else:
            self.frame.change_text_status("username or password incorrect")

    def on_move_to_sign_up(self, event):
        self.frame.switch_panel(self.frame.signup_panel, self)
