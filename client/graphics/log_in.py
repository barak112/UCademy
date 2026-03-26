from pubsub import pub

import clientProtocol
import wx

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

        # distributes the screen to left and right
        two_sides = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(two_sides)

        #left side is an image background and the Ucademy logo
        self.left = wx.Panel(self)

        #left side's background image
        self.background_bitmap = wx.Bitmap("assets\\blue_bg.png", wx.BITMAP_TYPE_PNG)
        self.left.SetMaxSize(self.background_bitmap.GetSize())
        self.left.Bind(wx.EVT_PAINT, self.on_paint)
        self.left.Bind(wx.EVT_SIZE, self.on_resize)

        # left side's Ucademy logo
        self.icon_with_text = wx.Bitmap(wx.Image("assets\\ucademy_log_in_logo_with_Text.png"))


        # the right panel - including the log-in form
        right = wx.Panel(self)

        min_size = (630, 680)
        frame.SetMinSize(min_size)

        #right background color -> off-white
        right.SetBackgroundColour(wx.Colour(self.RIGHT_COLOR))

        #right side sizer -> contains stretchers and horizontal_right which contains form
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        right.SetSizer(right_sizer)

        #horizontal_right -> contains form and stretchers, keeps form horizontally centered inside right
        horizontal_right = wx.Panel(right)
        horizontal_right_sizer = wx.BoxSizer(wx.HORIZONTAL)
        horizontal_right.SetSizer(horizontal_right_sizer)

        # form -> contains all the credentials fields and buttons
        form = wx.Panel(horizontal_right)
        form.SetBackgroundColour(wx.Colour(self.RIGHT_COLOR))

        # form sizer
        form_sizer = wx.BoxSizer(wx.VERTICAL)
        form.SetSizer(form_sizer)

        # --- form widgets ---

        #title
        title = wx.StaticText(form, label="Welcome Back              ")
        font = title.GetFont()
        font = font.Bold().Scale(4)
        title.SetFont(font)


        #subtitle
        subtitle = wx.StaticText(form, label="Log in to continue learning")
        font = subtitle.GetFont()
        font = font.Scale(1.5)
        subtitle.SetForegroundColour(wx.Colour(self.SUBTITLE_COLOR))
        subtitle.SetFont(font)

        # username and password fields

        # field icons
        username_icon = wx.Bitmap("assets\\username_icon.png", wx.BITMAP_TYPE_PNG)
        password_icon = wx.Bitmap("assets\\password_icon.png", wx.BITMAP_TYPE_PNG)

        # field sizers containing labels, borders and ctrltext
        user_sizer, self.username_input_obj = self.labeled_input("Username", form, "Enter your username or email",
                                                                 username_icon)
        password_sizer, self.password_input_obj = self.labeled_input("Password", form, "Enter your password",
                                                                     password_icon, True)

        # whenever one of the fields is being written to, make status message disappear
        self.username_input_obj.get_text_visible().Bind(wx.EVT_KEY_DOWN, self.entering_text)

        self.password_input_obj.get_text_visible().Bind(wx.EVT_KEY_DOWN, self.entering_text)
        self.password_input_obj.get_text_hidden().Bind(wx.EVT_KEY_DOWN, self.entering_text)

        # status message
        self.status_message = wx.StaticText(form)
        font = self.status_message.GetFont()
        font = font.Scale(1.5)
        self.status_message.SetForegroundColour(wx.Colour(self.SUBTITLE_COLOR))
        self.status_message.SetFont(font)
        self.status_message.SetForegroundColour(wx.RED)


        # login button
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

        # add all form widgets to form_sizer
        form_sizer.Add(title, 0, wx.BOTTOM, 10)

        form_sizer.Add(subtitle, 0, wx.BOTTOM, 30)

        form_sizer.Add(user_sizer, 0, wx.EXPAND | wx.BOTTOM | wx.TOP, 50)

        form_sizer.Add(password_sizer, 0, wx.EXPAND)

        form_sizer.Add(self.status_message, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP | wx.BOTTOM, 40)

        form_sizer.Add(login_button, 0, wx.EXPAND)

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
        two_sides.Add(self.left, 1, wx.EXPAND)
        two_sides.Add(right, 1, wx.EXPAND)

        # handles logic response to log in
        pub.subscribe(self.on_login_response, "login_ans")

        #handles key press
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)

        self.Hide()

    def entering_text(self, event):
        """whenever one of the credentials fields is being written to, deletes status message"""
        self.status_message.SetLabel("")
        event.Skip()

    def on_resize(self, event):
        """redraws the screen whenever the screen resizes, used to redraw the background image"""
        self.Refresh()  # trigger repaint
        event.Skip()

    def on_paint(self, event):
        """draws the background image on the left side of the screen"""
        dc = wx.BufferedPaintDC(self.left)
        dc.DrawBitmap(self.background_bitmap, 0, 0)

        left_width, left_height, = self.left.GetSize()

        icon_width, icon_height = self.icon_with_text.GetSize()
        x = (left_width - icon_width) // 2
        y = (left_height - icon_height) // 2

        dc.DrawBitmap(self.icon_with_text, x, y, True)

    @staticmethod
    def labeled_input(label_text, parent, placeholder, field_icon_bitmap, is_password = False):
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

        text_box = rounded_input_field.RoundedInputField(parent, placeholder, field_icon_bitmap, is_password)

        sizer.Add(label)
        sizer.Add(text_box, 0, wx.EXPAND)
        return sizer, text_box


    def on_key(self, event):
        """checks for keys pressed, exists on Escape, log in on Enter"""
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:
            exit()
        elif keycode == wx.WXK_RETURN:
            self.on_login(None)

        event.Skip()

    def on_login(self, event):
        """triggered on log in, takes input from username and password box objects
         checks that both arent empty, if they are then it sets status message accordingly.
        if they arent, sends credentials to the server"""
        username = self.username_input_obj.get_value()
        password = self.password_input_obj.get_value()

        print("credentials at login", username, password)

        if username and password:
            msg2send = clientProtocol.build_sign_in(username, password)
            self.frame.comm.send_msg(msg2send)
        else:
            self.status_message.SetLabel("you must enter both username and password to log in")
            self.Layout()

    def on_login_response(self, status, video_comm=None, user=None):
        """
            triggered on response from server about log in, if status = 1, log in is successful and the screen changes
            else, an appropriate status message is set.
        :param status: 0/1, indicates whether the log in was successful
        :param video_comm: video comm object
        :param user: user object
        """
        if status:
            self.frame.video = video_comm
            self.frame.user = user
            self.frame.switch_panel(self.frame.feed_panel, self)

            print("in login resp,", self.frame.user)

        else:
            self.status_message.SetLabel("username or password incorrect")
            self.Layout()

    def on_move_to_sign_up(self, event):
        """triggered on sign up button, changes screen to sign up"""
        self.frame.switch_panel(self.frame.signup_panel, self)
