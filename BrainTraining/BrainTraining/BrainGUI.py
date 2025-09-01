from ast import Lambda
from tkinter import *
from tkinter import ttk
from BrainFlowAPISetup import BrainFlowAPISetup
import serial
import threading, queue, time, math, random
from collections import deque
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


# Text color for the GUI is #aa58fc
# Background color for the GUI is black

class BrainGUI:

    

    def __init__(self):
        self.api = BrainFlowAPISetup()
        self.connectionLabel = None
        self.arduino = None

    def startupGUI(self):
        # Define color constants
        PURPLE = "#8A5BE2"
        BG = "#0B0B0C"  
    
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

        style.configure("Purple.TButton",
        background="#A97BFF",     # normal background
        foreground="white",    # text color
        font=("Arial", 16, "bold"),
        padding=10
)

        self.btn = ttk.Button(self.brainStartup, 
                              text="Connect", 
                              command=self.connectClicked,
                              style="Purple.TButton")
        self.btn.place(relx=0.5, y=350, width=160, height=44, anchor="n")

        # Start the event loop
        self.brainStartup.mainloop()

    def connectionSelected(self, event=None):

        PURPLE = "#A97BFF"
        BG = "#0B0B0C"  

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
        #print("Arduino COM Port selected:", comPort) # Debugging print statement
        self.arduino = serial.Serial(port=comPort, baudrate=9600, timeout=.1) 

        # Close the startup window 
        self.brainStartup.destroy()
        self.openMainScreen()

    def openMainScreen(self):
        # Define color constants
        PURPLE = "#A97BFF"
        BG = "#0B0B0C"  

        # Open a new screen
        self.mainScreen = Tk()
        self.mainScreen.geometry("550x450")
        self.mainScreen.title("Brain Training - Main")
        self.mainScreen.configure(bg=BG)

        welcome = Label(
            self.mainScreen,
            text="Connected! Please make a choice",
            font=("Arial", 24),
            bg=BG,
            fg="#aa58fc"
        )
        welcome.place(relx=0.5, y=36, anchor="n")

        # Style for buttons
        style = ttk.Style(self.mainScreen)
        style.theme_use("clam")
        style.configure(
            "Purple.TButton",
            background=PURPLE,
            foreground="white",
            font=("Arial", 14, "bold"),
            padding=10
        )

        self.calibrationButton = ttk.Button(
            self.mainScreen, 
            text="Calibration",
            style="Purple.TButton", 
            command=self.calibrate)
        self.calibrationButton.place(relx=0.25, rely=0.5, width=200, height=44, anchor="n")

        self.calibrationButton = ttk.Button(
            self.mainScreen, 
            text="Training",
            style="Purple.TButton", 
            command=self.training)
        self.calibrationButton.place(relx=0.75, rely=0.5, width=200, height=44, anchor="n")

        self.exitButton = ttk.Button(
            self.mainScreen,
            text="Exit",
            style="Purple.TButton",
            command=lambda:(self.api.endsession(), self.mainScreen.destroy())
        )
        self.exitButton.place(relx=0.5, rely=0.75, width=120, height=44, anchor="n")

        self.mainScreen.mainloop()


    def calibrate(self):
        print("Starting Calibration Screen...")
        self.mainScreen.destroy()

        # Define color constants
        PURPLE = "#A97BFF"
        BG = "#0B0B0C"  

        # Open a new screen
        self.calibrateScreen = Tk()
        self.calibrateScreen.geometry("550x450")
        self.calibrateScreen.title("Brain Training - Calibration")
        self.calibrateScreen.configure(bg=BG)

        # Title
        welcome = Label(
            self.calibrateScreen,
            text="Let's find your baseline",
            font=("Arial", 24, "bold"),
            bg=BG,
            fg=PURPLE
        )
        welcome.place(relx=0.5, y=36, anchor="n")

        # Sample rate label
        sampleLabel = Label(
            self.calibrateScreen, 
            text="Select a sample rate", 
            font=("Arial", 16),
            bg=BG,
            fg=PURPLE
        )
        sampleLabel.place(relx=0.5, y=90, anchor="n")

        # Sample rate dropdown
        sampleRate = [int(i) for i in range(1, 51)]
        self.samplePick = ttk.Combobox(
            self.calibrateScreen, 
            values=sampleRate, 
            state="readonly", 
            width=22
        )
        self.samplePick.place(relx=0.5, y=120, anchor="n")
        self.samplePick.set(sampleRate[0])  

        # Style for buttons
        style = ttk.Style(self.calibrateScreen)
        style.theme_use("clam")
        style.configure(
            "Purple.TButton",
            background=PURPLE,
            foreground="white",
            font=("Arial", 14, "bold"),
            padding=10
        )

        # Start calibration button
        self.calibrationButton = ttk.Button(
            self.calibrateScreen,
            text="Start",
            style="Purple.TButton",
            command=lambda: (self.calibrationButton.place_forget(), self.startCalibration(int(self.samplePick.get())))
        )
        self.calibrationButton.place(relx=0.5, rely=0.5, width=120, height=44, anchor="n")

        # Exit + Back buttons 
        self.exitButton = ttk.Button(
            self.calibrateScreen,
            text="Exit",
            style="Purple.TButton",
            command=lambda:(self.api.endsession(), self.calibrateScreen.destroy())
        )
        self.exitButton.place(relx=0.3, rely=0.75, width=120, height=44, anchor="n")

        self.backButton = ttk.Button(
            self.calibrateScreen,
            text="Back",
            style="Purple.TButton",
            command=lambda: (self.calibrateScreen.destroy(), self.openMainScreen())
        )
        self.backButton.place(relx=0.7, rely=0.75, width=120, height=44, anchor="n")

        self.calibrateScreen.mainloop()


    def startCalibration(self, sampleSize):
        # Define color constants
        PURPLE = "#A97BFF"
        BG = "#0B0B0C"  

        self.pleaseWait = Label(
            self.calibrateScreen, 
            text="Please wait...", 
            font=("Arial", 16),
            bg=BG,
            fg=PURPLE
        )
        self.pleaseWait.place(relx=0.5, rely=0.5, anchor="n")

        def ui_done(m, r):
        # hop to UI thread
            self.calibrateScreen.after(0, lambda: (
                self.pleaseWait.config(text=f"Mindful: {m:.3f}  |  Restful: {r:.3f}"),
                self.calibrationButton.config(state="normal")
        ))

        # Start calibration in a new thread to avoid blocking the GUI
        threading.Thread(
        target=self.api.calibrationreading,
        kwargs={"sampleSize": int(self.samplePick.get()), "onResult": ui_done},
        daemon=True
        ).start()

    def training(self):
        print("Starting Training Screen...")
        self.mainScreen.destroy()

        # Define color constants
        PURPLE = "#A97BFF"
        BG = "#0B0B0C"  

        # Open a new screen
        self.trainingScreen = Tk()
        self.trainingScreen.geometry("550x450")
        self.trainingScreen.title("Brain Training - Training")
        self.trainingScreen.configure(bg=BG)
        
        if self.api.boardActive is False:
            self.connectClicked(self)
        

        # Title
        welcome = Label(
            self.trainingScreen,
            text="Time to train.",
            font=("Arial", 24, "bold"),
            bg=BG,
            fg=PURPLE
        )
        welcome.place(relx=0.5, y=36, anchor="n")

        # Restfulness goal label
        restfulLabel = Label(
            self.trainingScreen, 
            text="Set Restfulness Goal", 
            font=("Arial", 16),
            bg=BG,
            fg=PURPLE
        )
        restfulLabel.place(relx=0.5, rely=.15, anchor="n")

        # Entry field for restfulness goal
        self.restValue = Entry(self.trainingScreen, width=10)
        self.restValue.place(relx=0.5, rely=.23, anchor="n")
        self.restValue.insert(0, "0.500") 

        # Style for buttons
        style = ttk.Style(self.trainingScreen)
        style.theme_use("clam")
        style.configure(
            "Purple.TButton",
            background=PURPLE,
            foreground="white",
            font=("Arial", 16, "bold"),
            padding=1
        )

        # Start calibration button
        self.start = ttk.Button(
            self.trainingScreen,
            text="Start",
            style="Purple.TButton",
            command=lambda: (self.start.place_forget(), self.startTraining())
        )
        self.start.place(relx=0.5, rely=.30, anchor="n")

        # Exit buttons 
        self.exitButton = ttk.Button(
            self.trainingScreen,
            text="Exit",
            style="Purple.TButton",
            command=lambda:(self.api.endsession(), self.trainingScreen.destroy(), 
                            self.arduino.write(b"0"))
        )
        self.exitButton.place(relx=0.5, rely=0.75, width=120, height=44, anchor="n")


        self.trainingScreen.mainloop()

    def startTraining(self):
        # Define color constants
        PURPLE = "#A97BFF"
        BG = "#0B0B0C"  
        
        self.restingNumber = Label(
            self.trainingScreen,
            text="",
            font=("Arial", 24, "bold"),
            bg=BG,
            fg=PURPLE
        )
        self.restingNumber.place(relx=0.5, rely=0.4, anchor="n")

        self.motorState = Label(
            self.trainingScreen,
            text="Motor: OFF",
            font=("Arial", 24, "bold"),
            bg=BG,
            fg=PURPLE
        )
        self.motorState.place(relx=0.5, rely=0.6, anchor="n")

        def ui_done(r):
            self.trainingScreen.after(0,lambda: 
                                      self.restingNumber.config(text=f"Restful: {float(r):.3f}"))

        def startMotor(s: bool):
           # print("Motor State:", s) # Debugging print statement
            self.arduino.write(b"100" if s else b"0")

            self.trainingScreen.after(0, lambda:
                self.motorState.config(text=f"Motor: {'ON' if s else 'OFF'}")
            )

        # Get the restfulness goal as a float value. 
        resfulasFloat = float(self.restValue.get())

        # Start calibration in a new thread to avoid blocking the GUI
        threading.Thread(
            target=self.api.activereading,
            args=(resfulasFloat,),
            kwargs={
                "onChange": startMotor, 
                "onResult": ui_done},
            daemon=True
        ).start()
