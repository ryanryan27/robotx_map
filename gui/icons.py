import time
from PIL import Image

class Icon:

    def __init__(self, type="wamv", name="unknown", lat = None, lon = None, time=time.time()):
        self.type = type
        self.id = None
        self.textid = None
        self.lat = lat
        self.lon = lon
        self.name=name
        self.colour = "grey"
        self.timestamp = time

        if(type != None):
            self.filename = str("./assets/"+type+"_"+self.colour+".png")
            im = Image.open(self.filename)
            self.width, self.height = im.size
            im.close()
            
        else:
            self.width = 20
            self.height = 20


    def setPosition(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def setState(self, state):
        if(state == 3):
            self.colour = "red"
        elif(state == 1):
            self.colour = "yellow"
        elif(state == 2):
            self.colour = "green"
        elif(state == 0):
            self.colour = "grey"
        self.filename = "./assets/"+self.type+"_"+self.colour+".png"

    def setTimestamp(self, time):
        self.timestamp = time
    

