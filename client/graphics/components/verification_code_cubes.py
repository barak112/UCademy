import wx


class VerificationCodeCubes(wx.Panel):


    def __init__(self, parent):
        super().__init__(parent)



        self.Bind(wx.EVT_SIZE, self.on_resize)
        self.Bind(wx.EVT_PAINT, self.on_paint)





    def on_resize(self, event):
        self.Refresh()
        event.Skip()


    def on_paint(self, event):
        #todo implement
        pass
