import wx


class CustomScrollPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.scroll_pos = 0
        self.max_scroll = 500

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_MOUSEWHEEL, self.on_wheel)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)  # prevent flicker

        self.dragging = False
        self.thumb_rect = wx.Rect(580, 0, 20, 50)  # initial thumb size and position

    def on_paint(self, event):
        dc = wx.BufferedPaintDC(self)
        w, h = self.GetClientSize()

        # draw background
        dc.SetBrush(wx.Brush(wx.Colour(240, 240, 240)))
        dc.DrawRectangle(0, 0, w, h)

        # draw the grid content offset by scroll_pos
        dc.SetBrush(wx.Brush(wx.Colour(200, 200, 255)))
        cell_h = 40
        rows, cols = 20, 5
        for row in range(rows):
            for col in range(cols):
                x = col * 100
                y = row * cell_h - self.scroll_pos
                if -cell_h < y < h:  # draw only visible
                    dc.DrawRectangle(x, y, 100, cell_h)
                    dc.DrawText(f"{row},{col}", x + 5, y + 5)

        # draw scrollbar background
        dc.SetBrush(wx.Brush(wx.Colour(220, 220, 220)))
        dc.DrawRectangle(w - 20, 0, 20, h)

        # draw thumb
        dc.SetBrush(wx.Brush(wx.Colour(100, 100, 100)))
        thumb_h = max(50, h * h // (h + self.max_scroll))
        thumb_y = int(self.scroll_pos / self.max_scroll * (h - thumb_h))
        self.thumb_rect = wx.Rect(w - 20, thumb_y, 20, thumb_h)
        dc.DrawRectangle(self.thumb_rect)

    def on_wheel(self, event):
        self.scroll_pos -= event.GetWheelRotation() // 2
        self.scroll_pos = max(0, min(self.scroll_pos, self.max_scroll))
        self.Refresh()

    def on_click(self, event):
        if self.thumb_rect.Contains(event.GetPosition()):
            self.dragging = True
            self.drag_offset = event.GetY() - self.thumb_rect.y

    def on_release(self, event):
        self.dragging = False

    def on_motion(self, event):
        if self.dragging:
            y = event.GetY() - self.drag_offset
            h = self.GetClientSize().height
            thumb_h = self.thumb_rect.height
            # convert thumb position to scroll_pos
            self.scroll_pos = int(y / (h - thumb_h) * self.max_scroll)
            self.scroll_pos = max(0, min(self.scroll_pos, self.max_scroll))
            self.Refresh()


class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Custom Scrollbar", size=(600, 400))
        panel = CustomScrollPanel(self)
        self.Show()


if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame()
    app.MainLoop()

#todo find how to integerate it and if it works with a normal grid not a drawn one
