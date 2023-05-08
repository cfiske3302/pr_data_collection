import os
import psutil
from multiprocessing import Pipe
import time
import sys
import numpy as np


def save_data(pipe, address="data"):
    while True:
        time.sleep(3)
        # if new data has been given
        if pipe.poll():
            data = pipe.recv()
            video = data[0]
            motor = data[1]
            servo = data[2]
            # get the path appropriate pathname for each of the arrays
            if len(sys.argv) == 1:
                name = "/driving_data_1"
                while os.path.exists(address + name):
                    num = name.split("_")
                    name = name[: -1 * len(num[-1])] + str(int(num[-1]) + 1)
            else:
                name = f"/{sys.argv[1]}"
                while os.path.exists(address + name):
                    try:
                        num = name.split("_")
                        name = name[: -1 * len(num[-1])] + str(int(num[-1]) + 1)
                    except:
                        name = name + "_1"

            ## save the data as a zipfile. This was found to not be necessary for storage and takes much longer
            # np.savez_compressed(name+"/zipped_data", video=video, motor=motor.get_data(), servo=servo.get_data())

            # save the data in a directory
            os.mkdir(address + name)
            np.save(address + name + "/video", video)
            np.save(address + name + "/motor", motor)
            np.save(address + name + "/servo", servo)
            pipe.send([f"datapoint taken : saved to {name}.npy"])
            # print(f"datapoint taken : saved to {name}.npy")
            del video
