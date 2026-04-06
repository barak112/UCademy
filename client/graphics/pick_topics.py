import math

import wx
import clientProtocol
import rounded_button
import settings
import topic_widget


class PickTopicsPanel(wx.ScrolledWindow):
    TITLE = "What are you interested in?"
    SUBTITLE = "Choose topics to personalise your experience. Select at least 3 topics."
    def __init__(self, frame, parent):
        super().__init__(parent)
        #todo add a custom scrollbar
        self.frame = frame
        self.parent = parent

        # scroll attributes
        self.SetScrollRate(0, 50)
        # self.SetVirtualSize(1000, 1000)

        self.background_bitmap = wx.Bitmap("assets\\topic_pick_background.png")
        self.grid_start_pos = 0

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.SetSizer(vbox)

        self.topic_spacers = {} # [topic_name] = (hspacer1, hspacer2, vspacer1, vspacer2)
        self.selected_topics = [] # [topic1, topic2]
        self.topics = {}  # [topic_name] = topic widget object

        self.grid_columns = 4
        self.grid_rows = math.ceil(len(settings.TOPICS)/self.grid_columns)


        self.grid = wx.GridSizer(self.grid_rows, self.grid_columns, 5, 5)
        for topic_name in settings.TOPICS:
            topic = topic_widget.TopicWidget(self, topic_name)
            self.topics[topic_name] = topic
            topic_hbox = wx.BoxSizer(wx.HORIZONTAL)
            topic_vbox = wx.BoxSizer(wx.VERTICAL)

            self.topic_spacers[topic_name] = []

            self.topic_spacers[topic_name].append(topic_hbox.Add((settings.TOPIC_WIDGET_GROWTH, settings.TOPIC_WIDGET_GROWTH)))
            topic_hbox.Add(topic, 1, wx.EXPAND)
            self.topic_spacers[topic_name].append(topic_hbox.Add((settings.TOPIC_WIDGET_GROWTH, settings.TOPIC_WIDGET_GROWTH)))

            self.topic_spacers[topic_name].append(topic_vbox.Add((settings.TOPIC_WIDGET_GROWTH, settings.TOPIC_WIDGET_GROWTH)))
            topic_vbox.Add(topic_hbox, 1, wx.EXPAND)
            self.topic_spacers[topic_name].append(topic_vbox.Add((settings.TOPIC_WIDGET_GROWTH, settings.TOPIC_WIDGET_GROWTH)))

            self.grid.Add(topic_vbox, 1, wx.EXPAND)

        self.spacer = vbox.Add((0, 100))
        vbox.Add(self.grid, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.continue_btn = rounded_button.RoundedButton(self, "Continue", settings.BRIGHT_UNACTIVE_BUTTON, (204, 223, 252), 25, 13)
        self.continue_btn.SetMinSize((140, 60))
        vbox.Add(self.continue_btn, 0, wx.ALIGN_CENTER_HORIZONTAL)

        # handles key press
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key)
        # handle background disappearance
        self.Bind(wx.EVT_SIZE, self.on_resize)

        self.Bind(wx.EVT_PAINT, self.on_paint)

        self.Layout()
        self.FitInside()  # calculates virtual size

        self.Hide()

    def topic_selected(self, topic_name):
        spacers = self.topic_spacers[topic_name]
        if topic_name in self.selected_topics:
            self.selected_topics.remove(topic_name)
            for i in range(1, settings.TOPIC_WIDGET_GROWTH + 1):
                for spacer in spacers:
                    spacer.SetMinSize((i, i))
                    self.Layout()
        else:
            self.selected_topics.append(topic_name)
            for i in range(1, settings.TOPIC_WIDGET_GROWTH + 1):
                for spacer in spacers:
                    spacer.SetMinSize((settings.TOPIC_WIDGET_GROWTH - i, settings.TOPIC_WIDGET_GROWTH - i))
                    self.Layout()

        self.continue_btn.set_active(len(self.selected_topics) >= settings.MIN_TOPICS)

    def on_resize(self, event):
        self.Refresh()
        event.Skip()

    def on_paint(self, event):
        dc = wx.BufferedPaintDC(self)
        self.DoPrepareDC(dc)
        dc.DrawBitmap(self.background_bitmap, 0, 0)

        gc = wx.GraphicsContext.Create(dc)
        if gc:
            w, h = self.GetClientSize()
            # draw title
            gc.SetFont(
                wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD),
                wx.BLACK)
            tw, th = gc.GetTextExtent(self.TITLE)
            gc.DrawText(self.TITLE, (w - tw) / 2, 10)

            #draw subtitle
            gc.SetFont(
                wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD),wx.BLACK
            )

            tw2, th2 = gc.GetTextExtent(self.SUBTITLE)
            gc.DrawText(self.SUBTITLE, (w - tw2) / 2, th+20)
            if not self.grid_start_pos:
                self.grid_start_pos = int(th2+th+ 60)
                self.spacer.SetMinSize((0, self.grid_start_pos))
                self.Layout()

            gc.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL), wx.BLACK)
            topics_selected_text = f"{len(self.selected_topics)} topics selected"
            tw, th = gc.GetTextExtent(topics_selected_text)
            gc.DrawText(topics_selected_text, (w - tw) / 2, self.grid_start_pos+self.grid.GetSize().GetHeight()+10)

    def on_key(self, event):
        """checks for keys pressed, exists on Escape, log in on Enter"""
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:
            exit()
        elif keycode == wx.WXK_RETURN:
            self.on_login(None)

        event.Skip()
