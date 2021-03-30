# Import stuff
import wx
import sys
import importlib
import configparser

# Edit path to include the "Modules" folder and the "Assistants" folder (allow importing from those folders)
sys.path.append("/home/pi/Universal-IoT-Control-Panel/Modules")
sys.path.append("/home/pi/Universal-IoT-Control-Panel/Assistants")

# Initialise configparser
config = configparser.ConfigParser()

try:
    print("Reading Config...")
    config.read('/home/pi/Universal-IoT-Control-Panel/config.ini')
    debug = bool(int(config["config"]["debug"]))
    assistant = importlib.import_module(config["assistant"]["assistant"])
except Exception as e:
    print("Config read failed... Using default values")
    print("Error:\n" + str(e))

debugMode = True

# Root frame, where everything is
class mainFrame(wx.Frame):
    def __init__(self, assistant, debug = False, tabs = []):
        # Make Window
        super().__init__(parent=None, title='Universal Control Panel Frontend', size=wx.Size(480, 320),
                     style = wx.DEFAULT_FRAME_STYLE)

        self.debug = debug
        self.tabs = tabs
        self.assistant = assistant

        self.mainUI()

    def mainUI(self):
        
        # Define notebook (for tabs)
        wxNotebook = wx.Notebook(self)

        wxNotebook.AddPage(self.assistant.main(wxNotebook), self.assistant.info["tabName"])
        
        # Add tabs
        for tab in self.tabs:
            wxNotebook.AddPage(tab.main(wxNotebook), tab.info["tabName"])

        # Centre the window just in case and laso for debugging
        self.Centre()

        # Show window and make fullscreen if debug disabled
        self.ShowFullScreen(not self.debug)
        self.Show()


# Parse config file
moduleConfig = open("/home/pi/Universal-IoT-Control-Panel/Modules/modules.cfg", "r")

# Split by line
moduleConfig = moduleConfig.read().split("\n")

# Make list to store module names
modules = []

# Filter lines
for line in moduleConfig:
    # Check if line is valid
    if (line[0:2] == "//" or line == "" or line.isspace()):
        # Line not valid, do nothing
        pass
    else:
        # Line valid, add to list of module names
        modules.append(line)


# Make list to store modules
tabs = []

# Add modules (as objects) to list
for module in modules:
    # Import module
    tabs.append(importlib.import_module(module))


# Initialise wxPython
app = wx.App()

# Make main frame
frame = mainFrame(assistant = assistant, debug = debug, tabs = tabs)

# Run MainLoop
app.MainLoop()
