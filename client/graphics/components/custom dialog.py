import wx


class ReportDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Report Video", size=(420, 320))

        panel = wx.Panel(self)

        # --- IMAGE (change path if needed) ---
        # Put a file called "warning.png" in the same folder as this script
        try:
            img = wx.Image("D:\\UCademy\client\\assets\\add_video.png", wx.BITMAP_TYPE_PNG)
            img = img.Scale(64, 64)
            bitmap = wx.StaticBitmap(panel, bitmap=wx.Bitmap(img))
        except:
            bitmap = wx.StaticText(panel, label="⚠️")

        # --- TEXT ---
        text = wx.StaticText(
            panel,
            label=(
                "Are you sure you want to report this video?\n\n"
                "Only report if the content is harmful or not educational."
            )
        )

        font = text.GetFont()
        font.SetPointSize(12)
        text.SetFont(font)

        # --- BUTTONS ---
        yes_btn = wx.Button(panel, wx.ID_YES, "Yes")
        no_btn = wx.Button(panel, wx.ID_NO, "No")

        yes_btn.Bind(wx.EVT_BUTTON, self.on_yes)
        no_btn.Bind(wx.EVT_BUTTON, self.on_no)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(yes_btn, 1, wx.ALL, 5)
        btn_sizer.Add(no_btn, 1, wx.ALL, 5)

        # --- LAYOUT ---
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(bitmap, 0, wx.ALL | wx.CENTER, 10)
        main_sizer.Add(text, 0, wx.ALL | wx.CENTER, 10)
        main_sizer.Add(btn_sizer, 0, wx.ALL | wx.CENTER, 10)

        panel.SetSizer(main_sizer)
        self.SetSize((450, 300))
        self.SetMinSize((450, 300))

    def on_yes(self, event):
        print("User clicked YES")
        self.EndModal(wx.ID_YES)

    def on_no(self, event):
        print("User clicked NO")
        self.EndModal(wx.ID_NO)
#todo use this to make the report dialogs better

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="wx Dialog Test", size=(400, 300))

        btn = wx.Button(self, label="Report Video")
        btn.Bind(wx.EVT_BUTTON, self.open_dialog)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddStretchSpacer()
        sizer.Add(btn, 0, wx.CENTER)
        sizer.AddStretchSpacer()

        self.SetSizer(sizer)
        self.Centre()

    def open_dialog(self, event):
        dlg = ReportDialog(self)
        dlg.SetMinSize((400,300))
        result = dlg.ShowModal()

        if result == wx.ID_YES:
            wx.MessageBox("Reported!", "Result", wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox("Cancelled", "Result", wx.OK | wx.ICON_INFORMATION)

        dlg.Destroy()


class App(wx.App):
    def OnInit(self):
        frame = MainFrame()
        frame.Show()
        return True


if __name__ == "__main__":
    app = App()
    app.MainLoop()
