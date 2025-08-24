import argparse
import time
import numpy as np
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module='brainflow.board_shim')

from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels
from brainflow.data_filter import DataFilter
from brainflow.ml_model import MLModel, BrainFlowMetrics, BrainFlowClassifiers, BrainFlowModelParams


class BrainFlowAPISetup: 

    def __init__(self, comPort: str | None = None, mac: str | None = None):
        self.board = None
        self.master_board_id = None
        self.guiSampleRate = None
        self.readingCount = 0
        self.motorState = False
        self.guiCOM = comPort
        self.guiMAC = mac

    def setup(self):
        BoardShim.enable_board_logger()
        DataFilter.enable_data_logger()
        MLModel.enable_ml_logger()

        # Arguments and defenitions 
        #-----------------------------------------#
        parser = argparse.ArgumentParser()
        # This section I am mostly using 3 arguments.
        # Serial port (I need this for the bluetooth dongle I have)
        # MAC Address for bluetooth connection without the dongle
        # Board that I am using from Open BCI GANGLION_BOARD=1
        parser.add_argument('--timeout', type=int, help='timeout for device discovery or connection', required=False,
                            default=0)
        parser.add_argument('--ip-port', type=int, help='ip port', required=False, default=0)
        parser.add_argument('--ip-protocol', type=int, help='ip protocol, check IpProtocolType enum', required=False,
                            default=0)
        parser.add_argument('--ip-address', type=str, help='ip address', required=False, default='')
        parser.add_argument('--serial-port', type=str, help='serial port', required=False, default=self.guiCOM)
        parser.add_argument('--mac-address', type=str, help='mac address', required=False, default=self.guiMAC)
        parser.add_argument('--other-info', type=str, help='other info', required=False, default='')
        parser.add_argument('--streamer-params', type=str, help='streamer params', required=False, default='')
        parser.add_argument('--serial-number', type=str, help='serial number', required=False, default='')
        parser.add_argument('--board-id', type=int, help='board id, check docs to get a list of supported boards',
                            required=False, default=1)
        parser.add_argument('--file', type=str, help='file', required=False, default='')
        args = parser.parse_args()

        params = BrainFlowInputParams()
        params.ip_port = args.ip_port
        params.serial_port = args.serial_port
        params.mac_address = args.mac_address
        params.other_info = args.other_info
        params.serial_number = args.serial_number
        params.ip_address = args.ip_address
        params.ip_protocol = args.ip_protocol
        params.timeout = args.timeout
        params.file = args.file

        self.board  = BoardShim(args.board_id, params)
        self.master_board_id = self.board.get_board_id()
        self.sampling_rate = BoardShim.get_sampling_rate(self.master_board_id)
        self.board.prepare_session()
        self.board.start_stream(45000, args.streamer_params)
        # End Arguments and Defenitions
        #------------------------------------------#




    def activereading(self, onChange=None):
    
        mindfulGoal = 0.5
        restfulGoal = 0.5

        # Preparing for streaming of brain mindfulness. 
        mindfulness_params = BrainFlowModelParams(BrainFlowMetrics.MINDFULNESS.value,
                                                  BrainFlowClassifiers.DEFAULT_CLASSIFIER.value)
        mindfulness = MLModel(mindfulness_params)
        mindfulness.prepare()

        restfulness_params = BrainFlowModelParams(BrainFlowMetrics.RESTFULNESS.value,
                                                  BrainFlowClassifiers.DEFAULT_CLASSIFIER.value)
        restfulness = MLModel(restfulness_params)
        restfulness.prepare()

        eeg_all = BoardShim.get_eeg_channels(self.master_board_id)
        eeg_channels = eeg_all[:2]   # use only first two EEG channels


        # Streaming loop this is used to get the real-time data from the board
        try:
            print("Starting real-time stream. Press Ctrl+C to stop.")
            while True:
                time.sleep(1)  # wait for 1 second of data
                data = self.board.get_board_data()
                if data.shape[1] < self.sampling_rate:
                    # not enough data collected yet, skip
                    continue
                latest_data = data[:, -self.sampling_rate:]  # last 1 second data
                latest_data = np.ascontiguousarray(latest_data)

                bands = DataFilter.get_avg_band_powers(latest_data, eeg_channels, self.sampling_rate, True)
                feature_vector = bands[0]
                    
                mindful_val = mindfulness.predict(feature_vector)
                restful_val = restfulness.predict(feature_vector)

                print(f"Avtivity: {mindful_val[0]:.4f}, Restfulness: {restful_val[0]:.4f}")

                # Check if the motor should be activated based on mindfulness and restfulness values
                if not self.motorState:
                    if float(restful_val[0]) > restfulGoal:
                        self.readingCount += 1
                    else:
                        self.readingCount = 0
                        print(f"Reading Count: {self.readingCount}") # Testing Purposes Only

                    if self.readingCount >= 4:
                        self.motorState = True
                        self.readingCount = 0
                        if onChange: onChange(True)
                        print("Motor Activated!") # Testing Purposes Only
                else:
                    if float(mindful_val[0]) > mindfulGoal:
                        self.readingCount += 1
                    else:
                        self.readingCount = 0
                    if self.readingCount >= 4:
                        self.motorState = False
                        self.readingCount = 0
                        if onChange: onChange(False)
                        print("Motor Stopped!") # Testing Purposes Only


                

        except KeyboardInterrupt:
            print("Stopping streaming...")

        # Clean up
        mindfulness.release()
        restfulness.release()
        self.board.stop_stream()

    def calibrationreading(self, sampleSize):
        # Preparing for streaming for calibration. Current is sampleSize is 10 seconds aka 10 readings 

        mindfulSum = 0
        restfulSum = 0
        self.guiSampleRate = sampleSize  # Number of samples to average over

        mindfulness_params = BrainFlowModelParams(BrainFlowMetrics.MINDFULNESS.value,
                                              BrainFlowClassifiers.DEFAULT_CLASSIFIER.value)
        mindfulness = MLModel(mindfulness_params)
        mindfulness.prepare()

        restfulness_params = BrainFlowModelParams(BrainFlowMetrics.RESTFULNESS.value,
                                                  BrainFlowClassifiers.DEFAULT_CLASSIFIER.value)
        restfulness = MLModel(restfulness_params)
        restfulness.prepare()

        eeg_all = BoardShim.get_eeg_channels(self.master_board_id)
        eeg_channels = eeg_all[:2]   # use only first two EEG channels
        sampling_rate = BoardShim.get_sampling_rate(int(self.master_board_id))

        print("Please wait getting your averages. ")

        print(f"Sample Rate:  {self.guiSampleRate}")

        for i in range(self.guiSampleRate):
            BoardShim.log_message(LogLevels.LEVEL_INFO.value, f'Collecting sample {i+1}/{self.guiSampleRate}')
            time.sleep(1)  # wait 1 second for new data

            data = self.board.get_board_data()
            if data.shape[1] < sampling_rate:
                # Not enough data yet, skip this sample
                continue
            latest_data = data[:, -sampling_rate:]  # last 1 second
            latest_data = np.ascontiguousarray(latest_data)

            bands = DataFilter.get_avg_band_powers(latest_data, eeg_channels, sampling_rate, True)
            feature_vector = bands[0]

            mindful_val = mindfulness.predict(feature_vector)[0]
            restful_val = restfulness.predict(feature_vector)[0]

            mindfulSum += mindful_val
            restfulSum += restful_val

        mindful_avg = mindfulSum / self.guiSampleRate
        restful_avg = restfulSum / self.guiSampleRate

        print(f"Mindfulness average: {mindful_avg:.4f}")
        print(f"Restfulness average: {restful_avg:.4f}")

        # Clean up
        mindfulness.release()
        restfulness.release()
        self.board.stop_stream()

    def endsession(self):
        self.board.release_session()