from tkinter import *
from tkinter import ttk
import dearpygui.dearpygui as dpg
from BrainFlowAPISetup import BrainFlowAPISetup
import serial

# Text color for the GUI is #aa58fc
# Background color for the GUI is black

class BrainGUI:
    def __init__(self):
        self.api = BrainFlowAPISetup()

    def startupGUI(self):
        # Initialize the main window 
        self.brainStartup = Tk()
        # Set the size and title of the window
        self.brainStartup.geometry("1280x720")
        self.brainStartup.title("Brain Training")
        # Set the icon for the window
        try:
            self.windowIcon = PhotoImage(file='Brain.png')
            self.brainStartup.iconphoto(True, self.windowIcon)
        except Exception as e:
            print("Icon load failed:", e)
        # Set the background color of the window
        self.brainStartup.configure(bg='black')

        # Create a label to display the welcome message
        welcome = Label(
                        self.brainStartup, 
                        text="Welcome to Brain Training", 
                        font=("Arial", 24), 
                        bg='black', 
                        fg='#aa58fc')
        welcome.pack(pady=20)

        ganglion = Label(
                        self.brainStartup, 
                        text="Ganglion connection type", 
                        font=("Arial", 20), 
                        bg='black', 
                        fg='#aa58fc')
        ganglion.place(x=100, y=120)

        arduinoConnection = Label(
                        self.brainStartup, 
                        text="Which COM port", 
                        font=("Arial", 20), 
                        bg='black', 
                        fg='#aa58fc')
        arduinoConnection.place(x=640, y=120)

        arduinoComPort = [f"COM{i}" for i in range(1, 257)]

        connectionType = [
            "Bluetooth Dongle",
            "Native Bluetooth"
        ]

        # Create a combobox for connection type selection
        self.connectionPick = ttk.Combobox(self.brainStartup, values=connectionType, state="readonly", width=22)
        self.connectionPick.place(x=100, y=160)
        self.connectionPick.set(connectionType[0])  # default selection

        # Create a combobox for Arduino COM port selection
        self.aComPicked = ttk.Combobox(self.brainStartup, values=arduinoComPort, state="readonly", width=22)
        self.aComPicked.place(x=640, y=160)
        self.aComPicked.set(arduinoComPort[0])  # default selection

        # Bind the combobox selection event to a function
        self.connectionPick.bind("<<ComboboxSelected>>", self.connectionSelected)
        self.aComPicked.bind("<<ComboboxSelected>>", lambda event: print("Arduino COM selected:", self.aComPicked.get()))

        self.btn = ttk.Button(self.brainStartup, text="Connect", command=self.connectClicked)
        self.btn.place(x=640, y=360)

        # Start the event loop
        self.brainStartup.mainloop()

    def connectionSelected(self, event=None):

        choice = self.connectionPick.get()
        self.comPortPick = None
        self.macEntry = None
        self.btn.config(state="disabled")

        if choice == "Bluetooth Dongle":
            comPort = [f"COM{i}" for i in range(1, 257)]

            comLabel = Label(
                        self.brainStartup,
                        text="Select COM Port      ", # Label text with spaces to hide the Enter MAC Address label that was there before...
                        font=("Arial", 16),
                        bg='black',
                        fg='white')
            comLabel.place(x=100, y=200)

            self.comPortPick = ttk.Combobox(self.brainStartup, values=comPort, state="readonly", width=22)
            self.comPortPick.place(x=100, y=230)
            self.comPortPick.set("COM1")
            self.btn.config(state="normal")

            def comSelected(event=None):
                chosen = self.comPortPick.get()
                print("COM selected:", chosen)

            self.comPortPick.bind("<<ComboboxSelected>>", comSelected)

            def getComPort(self):
                if hasattr(self, "comPortPick"):
                    return self.comPortPick.get()
                return None

        elif choice == "Native Bluetooth":
            # Label for MAC address
            macLabel = Label(
                            self.brainStartup,
                            text="Enter MAC Address",
                            font=("Arial", 16),
                            bg='black',
                            fg='white')
            macLabel.place(x=100, y=200)

            # Entry field for MAC
            self.macEntry = Entry(self.brainStartup, width=25)
            self.macEntry.place(x=100, y=230)
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
        # Open a new screen
        self.mainScreen = Tk()
        self.mainScreen.geometry("1280x720")
        self.mainScreen.title("Brain Training - Main")
        self.mainScreen.configure(bg="black")

        label = Label(
            self.mainScreen,
            text="Connected! Welcome to brain training please make a selection",
            font=("Arial", 24),
            bg="black",
            fg="#aa58fc"
        )
        label.pack(pady=20)

        self.disconnectButton = ttk.Button(self.mainScreen, text="Disconnect", command=self.disconnectClicked)
        self.disconnectButton.place(x=640, y=360)

    def disconnectClicked(self):
        # This function is used to handle the disconnect button click event.
        print("Disconnecting...") # Debugging print statement
        self.api.endsession()





