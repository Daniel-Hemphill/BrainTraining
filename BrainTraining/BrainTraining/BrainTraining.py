import os, pathlib
import sys

# Prime BrainFlow DLL path FIRST
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

from BrainFlowAPISetup import BrainFlowAPISetup
from brainflow.board_shim import BoardShim

def main():
    api = BrainFlowAPISetup()
    api.setup()
    # api.calibrationreading()
    api.activereading()
    

if __name__ == "__main__":
    main()