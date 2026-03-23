import wx
import clientProtocol


class Feed(wx.Panel):
    def __init__(self, frame, parent):
        super().__init__(parent)

        self.frame = frame
        self.parent = parent

        self.movies = [
            ("Inception", "Great sci-fi movie"),
            ("Titanic", "Classic romance"),
            ("Matrix", "Mind-blowing action"),
        ]

        self.index = 0

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.movie_title = wx.StaticText(self, label="")
        self.comment = wx.StaticText(self, label="")

        next_btn = wx.Button(self, label="Next")

        vbox.Add(self.movie_title, 0, wx.ALL, 10)
        vbox.Add(self.comment, 0, wx.ALL, 10)
        vbox.Add(next_btn, 0, wx.ALL, 10)

        self.SetSizer(vbox)

        next_btn.Bind(wx.EVT_BUTTON, self.on_next)

        self.update_movie()

        self.Hide()

    def update_movie(self):
        title, comment = self.movies[self.index]
        self.movie_title.SetLabel(f"Movie: {title}")
        self.comment.SetLabel(f"Comment: {comment}")

    def on_next(self, event):
        self.index = (self.index + 1) % len(self.movies)
        self.update_movie()
