from tkinter import *
from tkinter import ttk
import dearpygui.dearpygui as dpg
from BrainFlowAPISetup import BrainFlowAPISetup
import serial
import time

# Text color for the GUI is #aa58fc
# Background color for the GUI is black

class BrainGUI:

    

    def __init__(self):
        self.api = BrainFlowAPISetup()
        self.connectionLabel = None

    def startupGUI(self):
        # Define color constants
        PURPLE = "#A97BFF"
        BG = "#0B0B0C"  
        MUTED = "#B9B9C3"
    
        # Initialize the main window 
        self.brainStartup = Tk()
        # Set the size and title of the window
        self.brainStartup.geometry("550x450")
        self.brainStartup.title("Brain Training")
        try:
            self.windowIcon = PhotoImage(file='Brain.png')
            self.brainStartup.iconphoto(True, self.windowIcon)
        except Exception as e:
            print("Icon load failed:", e)
        self.brainStartup.configure(bg=BG)

        
        style = ttk.Style(self.brainStartup)
        style.theme_use("clam")

        # Create a label to display the welcome message
        welcome = Label(
            self.brainStartup, 
            text="Welcome to\nBrain Training", 
            font=("Arial", 26, "bold"), 
            bg=BG, 
            fg=PURPLE,
            justify="center")
        welcome.place(relx=0.5, y=36, anchor="n")

        ganglion = Label(
            self.brainStartup, 
            text="Ganglion Connection", 
            font=("Arial", 16), 
            bg=BG, 
            fg=PURPLE)
        ganglion.place(relx=0.25, y=160, anchor="n")

        arduinoConnection = Label(
            self.brainStartup, 
            text="Arduino COM Port", 
            font=("Arial", 16), 
            bg=BG, 
            fg=PURPLE)
        arduinoConnection.place(relx=0.75, y=160, anchor="n")

        arduinoComPort = [f"COM{i}" for i in range(1, 257)]
        connectionType = ["Bluetooth Dongle", "Native Bluetooth"]

        self.connectionPick = ttk.Combobox(self.brainStartup, values=connectionType, state="readonly", width=22)
        self.connectionPick.place(relx=0.25, y=188, anchor="n")
        self.connectionPick.set(connectionType[0])  

        self.aComPicked = ttk.Combobox(self.brainStartup, values=arduinoComPort, state="readonly", width=22)
        self.aComPicked.place(relx=0.75, y=188, anchor="n")
        self.aComPicked.set(arduinoComPort[0])  

        # Bind the combobox selection event to a function
        self.connectionPick.bind("<<ComboboxSelected>>", self.connectionSelected)
        self.aComPicked.bind("<<ComboboxSelected>>", lambda event: print("Arduino COM selected:", self.aComPicked.get()))

        self.btn = ttk.Button(self.brainStartup, text="Connect", command=self.connectClicked)
        self.btn.place(relx=0.5, y=350, width=160, height=44, anchor="n")

        # Start the event loop
        self.brainStartup.mainloop()

    def connectionSelected(self, event=None):

        PURPLE = "#A97BFF"
        BG = "#0B0B0C"  
        MUTED = "#B9B9C3"

        if self.connectionLabel is not None:
            self.connectionLabel.destroy()

        choice = self.connectionPick.get()
        self.comPortPick = None
        self.macEntry = None
        self.btn.config(state="disabled")

        if choice == "Bluetooth Dongle":
            comPort = [f"COM{i}" for i in range(1, 257)]

            self.connectionLabel = Label(
                        self.brainStartup,
                        text="Select COM Port",
                        font=("Arial", 16),
                        bg=BG,
                        fg=PURPLE)
            self.connectionLabel.place(relx=0.25, y=230, anchor="n")

            self.comPortPick = ttk.Combobox(self.brainStartup, values=comPort, state="readonly", width=22)
            self.comPortPick.place(relx=0.25, y=258, anchor="n")
            self.comPortPick.set("COM1")
            self.btn.config(state="normal")

            def comSelected(event=None):
                chosen = self.comPortPick.get()
                print("COM selected:", chosen)

            self.comPortPick.bind("<<ComboboxSelected>>", comSelected)



        elif choice == "Native Bluetooth":

            # Label for MAC address
            self.connectionLabel = Label(
                            self.brainStartup,
                            text="Enter MAC Address",
                            font=("Arial", 16),
                            bg=BG,
                            fg=PURPLE)
            self.connectionLabel.place(relx=0.25, y=230, anchor="n")

            # Entry field for MAC
            self.macEntry = Entry(self.brainStartup, width=25)
            self.macEntry.place(relx=0.25, y=258, anchor="n")
            self.macEntry.insert(0, "00:00:00:00:00:00")
            self.btn.config(state="normal")

    def connectClicked(self):
        # This function is used to handle the connection button click event.
        choice = self.connectionPick.get()

        if choice == "Bluetooth Dongle" and self.comPortPick:
            chosen = self.comPortPick.get()
            print("Connecting via Dongle on", chosen) # Debugging print statement
            self.api = BrainFlowAPISetup(comPort=chosen, mac='')
            self.api.setup()

        elif choice == "Native Bluetooth" and self.macEntry:
            mac = self.macEntry.get()
            print("Connecting via Native Bluetooth, MAC:", mac) # Debugging print statement
            self.api = BrainFlowAPISetup(mac=mac, comPort='')
            self.api.setup()

        comPort = self.aComPicked.get()
        print("Arduino COM Port selected:", comPort) # Debugging print statement
        arduino = serial.Serial(port=comPort, baudrate=9600, timeout=.1) 

        # Close the startup window 
        self.brainStartup.destroy()
        self.openMainScreen()

    def openMainScreen(self):
        # Define color constants
        PURPLE = "#A97BFF"
        BG = "#0B0B0C"  
        MUTED = "#B9B9C3"

        # Open a new screen
        self.mainScreen = Tk()
        self.mainScreen.geometry("1280x720")
        self.mainScreen.title("Brain Training - Main")
        self.mainScreen.configure(bg="black")

        label = Label(
            self.mainScreen,
            text="Connected! Welcome to brain training please make a selection",
            font=("Arial", 24),
            bg=BG,
            fg="#aa58fc"
        )
        label.pack(pady=20)

        self.disconnectButton = ttk.Button(self.mainScreen, text="Disconnect", command=self.disconnectClicked)
        self.disconnectButton.place(x=640, y=360)

    def disconnectClicked(self):
        # This function is used to handle the disconnect button click event.
        print("Disconnecting...") # Debugging print statement
        self.api.endsession()
        self.mainScreen.destroy()