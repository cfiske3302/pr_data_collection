import os
import psutil
from multiprocessing import Pipe
import time
import sys
import numpy as np

def save_data(pipe, address="data"):
    time.sleep(3)
    while True:
        if pipe.poll():
            data = pipe.recv()
            video = data[0]
            motor = data[1]
            servo = data[2]
            if(len(sys.argv) == 1):
                name = "/driving_data_1"
                while os.path.exists(address+name):
                    num = name.split('_')
                    name = name[:-1*len(num[-1])]+str(int(num[-1])+1)
            else:
                name = f"/{sys.argv[1]}"
                while os.path.exists(address+name):
                    try:
                        num = name.split('_')
                        name = name[:-1*len(num[-1])]+str(int(num[-1])+1)
                    except:
                        name = name + "_1"
            os.mkdir(address+name)
            # np.savez_compressed(name+"/zipped_data", video=video, motor=motor.get_data(), servo=servo.get_data())
            np.save(address+name+"/video", video)
            np.save(address+name+"/motor", motor)
            np.save(address+name+"/servo", servo)
            pipe.send([f"datapoint taken : saved to {name}.npy"])
            # print(f"datapoint taken : saved to {name}.npy")
            del video