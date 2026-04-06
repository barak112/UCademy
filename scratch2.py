import wx


class ScrollableGridPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.scroll_pos = 0
        self.max_scroll = 0

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_MOUSEWHEEL, self.on_wheel)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)

        # container for the grid
        self.content_panel = wx.Panel(self)
        self.grid_sizer = wx.GridSizer(rows=30, cols=4, vgap=5, hgap=5)
        for i in range(30 * 4):
            cell = wx.StaticText(self.content_panel, label=f"Item {i}", style=wx.ALIGN_CENTER)
            cell.SetMinSize((100, 40))
            cell.SetBackgroundColour(wx.Colour(200, 200, 255))
            self.grid_sizer.Add(cell, 0, wx.EXPAND)

        self.content_panel.SetSizer(self.grid_sizer)
        self.content_panel.Layout()
        self.max_scroll = max(0, self.grid_sizer.GetMinSize().height - self.GetSize().height)

        # layout content panel
        self.content_panel.SetPosition((0, 0))
        self.content_panel.SetSize(self.grid_sizer.GetMinSize())

    def on_paint(self, event):
        dc = wx.BufferedPaintDC(self)
        w, h = self.GetClientSize()

        # draw background
        dc.SetBrush(wx.Brush(wx.Colour(240, 240, 240)))
        dc.DrawRectangle(0, 0, w, h)

        # draw scrollbar
        dc.SetBrush(wx.Brush(wx.Colour(220, 220, 220)))
        dc.DrawRectangle(w - 20, 0, 20, h)

        thumb_h = max(50, h * h // self.content_panel.GetSize().height)
        thumb_y = int(self.scroll_pos / max(1, self.content_panel.GetSize().height - h) * (h - thumb_h))
        dc.SetBrush(wx.Brush(wx.Colour(100, 100, 100)))
        dc.DrawRectangle(w - 20, thumb_y, 20, thumb_h)

    def on_wheel(self, event):
        h = self.GetSize().height
        max_scroll = max(0, self.content_panel.GetSize().height - h)
        self.scroll_pos -= event.GetWheelRotation() // 2
        self.scroll_pos = max(0, min(self.scroll_pos, max_scroll))
        self.content_panel.SetPosition((0, -self.scroll_pos))
        self.Refresh()


class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="GridSizer Custom Scroll", size=(600, 400))
        panel = ScrollableGridPanel(self)
        self.Show()


if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame()
    app.MainLoop()
