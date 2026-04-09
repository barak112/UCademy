import math

import wx
from pubsub import pub

import clientProtocol
import rounded_button
import settings
import topic_widget


class PickTopicsPanel(wx.ScrolledWindow):
    TITLE = "What are you interested in?"
    SUBTITLE = "Choose topics to personalise your experience. Select at least 3 topics."
    def __init__(self, frame, parent):
        super().__init__(parent)
        self.frame = frame
        self.parent = parent

        # scroll attributes
        self.SetScrollRate(0, 7)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        self.background_bitmap = wx.Bitmap("assets\\topic_pick_background.png")
        self.grid_start_pos = 0

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.SetSizer(vbox)

        self.selected_topics = [] # [topic1, topic2]
        self.topics = {}  # [topic_name] = topic widget object

        self.grid_columns = 4
        self.grid_rows = math.ceil(len(settings.TOPICS)/self.grid_columns)

        self.grid = wx.GridSizer(self.grid_rows, self.grid_columns, 5, 5)
        for topic_name in settings.TOPICS:
            topic = topic_widget.TopicWidget(self, topic_name)
            self.topics[topic_name] = topic
            self.grid.Add(topic, 1, wx.EXPAND | wx.ALL, 5)

        self.spacer = vbox.Add((0, 100))
        vbox.Add(self.grid, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.continue_btn = rounded_button.RoundedButton(self, "Continue", settings.BRIGHT_UNACTIVE_BUTTON, (204, 223, 252), 25, 13)
        self.continue_btn.SetMinSize((140, 60))
        self.continue_btn.Bind(wx.EVT_LEFT_UP, self.on_set_topics)
        vbox.Add(self.continue_btn, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 40)

        # handles key press
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)
        # handle background disappearance
        self.Bind(wx.EVT_SIZE, self.on_resize)

        self.Bind(wx.EVT_PAINT, self.on_paint)

        self.Bind(wx.EVT_SCROLLWIN, self.on_scroll)
        self.scrolls = 0
        self._scroll_timer = None
        self.a_scroll = False

        self.Layout()
        self.FitInside()  # calculates virtual size

        pub.subscribe(self.on_set_topics_ans, "set_topics_ans")

        self.Hide()

    def on_set_topics(self, event):
        topics = [settings.TOPICS.index(topic) for topic in self.selected_topics]
        print(topics)
        msg = clientProtocol.build_set_topics(topics)
        self.frame.comm.send_msg(msg)
        event.Skip()

    def on_set_topics_ans(self, topics):
        self.frame.user.topics = topics
        self.frame.switch_panel(self.frame.feed_panel, self)
        print("switching to feed panel")

    def topic_selected(self, topic_name):
        if topic_name in self.selected_topics:
            self.selected_topics.remove(topic_name)
            for i in range(1, settings.TOPIC_WIDGET_GROWTH + 1):
                self.grid.GetItem(self.topics[topic_name]).SetBorder(i)
                self.Layout()
        else:
            self.selected_topics.append(topic_name)
            for i in range(1, settings.TOPIC_WIDGET_GROWTH + 1):
                self.grid.GetItem(self.topics[topic_name]).SetBorder(settings.TOPIC_WIDGET_GROWTH - i)
                self.Layout()

        self.Refresh()
        self.continue_btn.set_active(len(self.selected_topics) >= settings.MIN_TOPICS)

    def on_resize(self, event):
        if event.GetSize()[0] < self.grid.GetSize()[0] + 40 and self.grid.GetCols() > 1:
            self.grid_columns = self.grid.GetCols() - 1
            self.grid.SetCols(self.grid_columns)
            self.grid.SetRows(math.ceil(len(settings.TOPICS) / self.grid_columns))
            self.Layout()

        if event.GetSize()[0] > self.grid.GetSize()[0] + settings.TOPIC_WIDGET_WIDTH + 40 and self.grid.GetCols() < 4:
            self.grid_columns = self.grid.GetCols() + 1
            self.grid.SetCols(self.grid_columns)
            self.grid.SetRows(math.ceil(len(settings.TOPICS) / self.grid_columns))
            self.Layout()

        self.Refresh()
        event.Skip()

    def on_scroll(self, event):
        self.scrolls += 1
        if self.scrolls > 20:
            self.a_scroll = True
            self.Refresh()
            self.a_scroll = False
            self.scrolls = 0

        event.Skip()

    def on_paint(self, event):
        dc = wx.BufferedPaintDC(self)
        dc.DrawBitmap(self.background_bitmap, 0, 0, True)
        if not self.a_scroll:
            self.PrepareDC(dc)

            gc = wx.GraphicsContext.Create(dc)
            if gc:
                w, h = self.GetClientSize()
                # draw title
                gc.SetFont(
                    wx.Font(25, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD),
                    wx.BLACK)
                tw, th = gc.GetTextExtent(self.TITLE)
                gc.DrawText(self.TITLE, (w - tw) / 2, 10)

                #draw subtitle
                gc.SetFont(
                    wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL),wx.BLACK
                )

                tw2, th2 = gc.GetTextExtent(self.SUBTITLE)
                gc.DrawText(self.SUBTITLE, (w - tw2) / 2, th+20)
                if not self.grid_start_pos:
                    self.grid_start_pos = int(th2+th+ 40)
                    self.spacer.SetMinSize((0, self.grid_start_pos))
                    self.Layout()

                #topics selected text
                gc.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL), wx.BLACK)
                topics_selected_text = f"{len(self.selected_topics)} topics selected"
                tw, th = gc.GetTextExtent(topics_selected_text)
                gc.DrawText(topics_selected_text, (w - tw) // 2, self.grid_start_pos+self.grid.GetSize().GetHeight()+20)

    def on_key(self, event):
        """checks for keys pressed, exists on Escape, log in on Enter"""
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:
            exit()
        elif keycode == wx.WXK_RETURN:
            self.on_login(None)

        event.Skip()
