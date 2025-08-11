import os, pathlib
import sys
import serial 
from BrainFlowAPISetup import BrainFlowAPISetup
from brainflow.board_shim import BoardShim

# Prime BrainFlow DLL path. I started the project in PyCharm and had some issues setting up
# the BrainFlow DLL path correctly.This is a workaround to ensure the DLLs are found. 
try:
    import brainflow as _bf
    dll_dir = pathlib.Path(_bf.__file__).resolve().parent / "lib"
    if hasattr(os, "add_dll_directory") and dll_dir.exists():
        os.add_dll_directory(str(dll_dir))
        for sub in dll_dir.iterdir():
            if sub.is_dir():
                os.add_dll_directory(str(sub))
except Exception as e:
    print("Warning: could not prime BrainFlow DLL path:", e)



def main():
    api = BrainFlowAPISetup()
    api.setup()
    #api.calibrationreading()
    api.activereading()
    api.endsession()
    

if __name__ == "__main__":
    main()