import PySimpleGUI as psg
import pyproj

class GUI:

    def __init__(self):
        self.loadSettings()
        self.projection = pyproj.Proj(self.settings["projection"])
        print(self.settings["projection"])

    def loadSettings(self):
        self.settings = dict()
        file_ = open("config.cfg", "r")
        for line in file_:
            setting = line.split(": ", 1)
            self.settings[setting[0]] = setting[1]
        


    def latlong_to_xy(self, lat, lon):


        return x,y



if __name__ == "__main__":

    gui=GUI()

    layout = [[psg.Text("Hello from PySimpleGUI")], [psg.Button("OK")]]

    # Create the window
    window = psg.Window("Demo", layout)

    # Create an event loop
    while True:
        event, values = window.read()
        # End program if user closes window or
        # presses the OK button
        if event == "OK" or event == psg.WIN_CLOSED:
            break

    window.close()
