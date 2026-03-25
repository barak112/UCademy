import wx
from pubsub import pub
from feed import Feed
from log_in import LoginPanel
from pick_topics import PickTopicsPanel
from sign_up import SignupPanel


# ----------------------------
# Main Frame (Controller)
# ----------------------------
class MainFrame(wx.Frame):
    def __init__(self, comm):
        super().__init__(None, title="Movie App", size=(1280, 720))
        # super().Maximize()

        self.comm = comm
        self.video_comm = None
        self.user = None
        # 1. Create the status bar
        self.CreateStatusBar()

        # 2. Set initial text in the status bar
        self.SetStatusText("Welcome to my wxPython application!", 0)

        self.container = wx.Panel(self)

        self.login_panel = LoginPanel(self, self.container)
        self.signup_panel = SignupPanel(self, self.container)
        self.pick_topics_panel = PickTopicsPanel(self, self.container)
        self.feed_panel = Feed(self, self.container)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.sizer.Add(self.login_panel, 1, wx.EXPAND)
        self.sizer.Add(self.signup_panel, 1, wx.EXPAND)
        self.sizer.Add(self.feed_panel, 1, wx.EXPAND)

        self.container.SetSizer(self.sizer)

        self.login_panel.Show()
        # self.signup_panel.Show()
    # ----------------------------
    # Navigation Methods
    # ----------------------------

    def switch_panel(self, new_panel, old_panel):
        old_panel.Hide()
        new_panel.Show()
        self.Layout()
        self.Refresh()
        self.sizer.Layout()
        new_panel.Refresh()

    def change_text_status(self, text):
        """Event handler to update the status bar text."""
        self.SetStatusText(text, 0)




# ----------------------------
# App Entry Point
# ----------------------------
if __name__ == "__main__":
    app = wx.App()
    frame = MainFrame(None)
    frame.Show()
    app.MainLoop()
