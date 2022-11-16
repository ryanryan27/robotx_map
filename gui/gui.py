import PySimpleGUI as psg
import pyproj
import numpy as np
import threading
import time
import random
from icons import Icon
from PIL import Image

class GUI:

    def __init__(self):
        self.loadSettings()
        self.projection = pyproj.Proj(self.settings["projection"])
        self.datum_x, self.datum_y = self.projection(float(self.settings['pointAlon']), float(self.settings['pointAlat'])) 
        self.calculateTransform()
        self.icons = []

    def loadSettings(self):
        self.settings = dict()
        file_ = open("config.cfg", "r")
        for line in file_:
            setting = line.strip().split(": ", 1)
            self.settings[setting[0]] = setting[1]

    def calculateTransform(self):
        pAx = float(self.settings['pointAx'])
        pAy = float(self.settings['pointAy'])
        pBx = float(self.settings['pointBx'])
        pBy = float(self.settings['pointBy'])
        pCx = float(self.settings['pointCx'])
        pCy = float(self.settings['pointCy'])

        self.transform_b = np.array([pAx, pAy])
        Bx, By = self.latlong_to_offset_UTM(float(self.settings['pointBlat']), float(self.settings['pointBlon']))
        Cx, Cy = self.latlong_to_offset_UTM(float(self.settings['pointClat']), float(self.settings['pointClon']))
        A = np.array([[Bx, By, 0, 0], [0, 0, Bx, By], [Cx, Cy, 0, 0], [0, 0, Cx, Cy]])
        b = np.array([pBx - pAx, pBy - pAy, pCx - pAx, pCy - pAy])
        A_vals = np.linalg.solve(A, b)
        self.transform_A = np.reshape(A_vals, (2, 2))
        
        
    def latlong_to_xy(self, lat, lon):
        xy = np.array(self.latlong_to_offset_UTM(lat, lon))
        xy = np.matmul(self.transform_A, xy)
        xy = np.add(xy, self.transform_b)

        return xy.item(0), xy.item(1)

    def latlong_to_offset_UTM(self, lat, lon):

        x,y = self.projection(lon, lat)
        x -= self.datum_x
        y -= self.datum_y
        return x,y

    def updateFromMessage(self, team, lat, lon, state, time):

        found = False

        for icon in self.icons:
            if icon.name == team:
                found = True
                icon.setPosition(lat, lon)
                icon.setState(state) 
                icon.setTimestamp(time)

        if not found:
            newIcon = Icon(name=team, lat=lat, lon=lon,time=time)
            newIcon.setState(state)
            self.icons.append(newIcon)


def drawIcons(gui, window):
    for icon in gui.icons:
        x,y = gui.latlong_to_xy(icon.lat, icon.lon)
        
        if time.time() - icon.timestamp > int(gui.settings["timeout"]):
            icon.setState(0)
        

        offsetx = icon.width/2
        offsety = icon.height/2

        if icon.id == None:
            icon.id = window['bg'].draw_image(icon.filename, location=(x-offsetx,y-offsety))
        else:
            newid = window['bg'].draw_image(icon.filename, location=(x-offsetx,y-offsety))
            window['bg'].delete_figure(icon.id)
            icon.id = newid


def async_updates(gui, window):
    offset = 0
    while True:

        drawIcons(gui, window)            

        time.sleep(1.0/30)

def test_heartbeats(gui):
    while True:

        time.sleep(1)
        
        gui.updateFromMessage("flnd", -33.720777, 150.672182, random.randint(1,3), time.time())    


def start_gui():
    gui=GUI()

    # Load in the background map image to get its size
    map_filename = "./assets/"+gui.settings['image']
    im = Image.open(map_filename)
    canvas_size = im.size
    im.close()

    # Create the graph that will be used as the coordinate system for image drawing
    frame = psg.Graph(canvas_size, graph_bottom_left=[0,canvas_size[1]], graph_top_right=[canvas_size[0],0],  key='bg')
    


    layout = [[frame]]

    # Create the window
    window = psg.Window("RobotX2022 Viewer", layout, finalize=True)

    window['bg'].draw_image(map_filename, location=(0,0))

    
    threading.Thread(target=test_heartbeats, args=(gui,),name="test_thread", daemon=True).start()
    threading.Thread(target=async_updates, args=(gui,window),name="update_thread", daemon=True).start()

    # Create an event loop
    while True:

        event, values = window.read()
        # End program if user closes window or
        # presses the OK button
        if event == "OK" or event == psg.WIN_CLOSED:
            break

    window.close()


if __name__ == "__main__":
    start_gui()
    
