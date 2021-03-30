import wx
from threading import Thread
import RPi.GPIO as GPIO
import googleAssistantBackend
import configparser

info = {"tabName": "Google Assistant", "name": "Google Assistant", "info": "This is the Google Assistant", "depends": None}

# Initialise configparser
config = configparser.ConfigParser()

try:
    print("Reading Config...")
    config.read('/home/pi/Universal-IoT-Control-Panel/config.ini')
    assistantModelID = config["assistant"]["modelID"]
    assistantProjectID = config["assistant"]["projectID"]
except Exception as e:
    print("Config read failed...")

class assistantThread(Thread):
    """Test Worker Thread Class."""
    
    def __init__(self, panel):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self.panel = panel
        self.sentinel = True
        self.start()    # start the thread

    def run(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        inputA = False
        print("Assistant Ready.")
        while True:
            inputA = GPIO.input(16)
            if (inputA != True):
                while inputA != True:
                    inputA = GPIO.input(16)
                    pass
                googleAssistantBackend.main(once = True, device_model_id = assistantModelID, project_id = assistantProjectID)

class main(wx.Panel): 
   def __init__(self, parent): 
      super(main, self).__init__(parent) 
      text = wx.TextCtrl(self, style = wx.TE_MULTILINE, size = (250,150))
      self.thread = None
      self.thread = assistantThread(self)
