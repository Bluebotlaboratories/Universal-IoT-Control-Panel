import wx

info = {"tabName": "Test1", "name": "Test1", "info": "This is test 1", "depends": None}
class main(wx.Panel): 
   def __init__(self, parent): 
      super(main, self).__init__(parent) 
      text = wx.TextCtrl(self, style = wx.TE_MULTILINE, size = (250,150))
