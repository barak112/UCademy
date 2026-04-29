import wx


class TopicsGrid(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        topics = ["Python", "Music", "Math", "Art", "Science", "History"]

        grid = wx.GridSizer(rows=2, cols=3, vgap=10, hgap=10)

        btn = wx.ToggleButton(self, label="aaaa")
        # btn.SetMinSize((500, 50))
        for topic in topics:
            grid.Add(btn, 0, wx.EXPAND)
            btn = wx.ToggleButton(self, label=topic)
            # btn.SetMinSize((10, 60))

        outer = wx.BoxSizer(wx.VERTICAL)
        outer.Add(grid, 0, wx.ALL, 10)
        self.SetSizer(outer)


class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Topics Grid Demo", size=(600, 250))

        panel = TopicsGrid(self)

        self.Show()


if __name__ == "__main__":
    app = wx.App()
    MainFrame()
    app.MainLoop()
