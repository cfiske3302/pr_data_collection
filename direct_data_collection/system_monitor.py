import os
import psutil
from multiprocessing import Pipe
import time


# monitors system memory and storage
def monitor_system(pipe, process_id, timeout=3600):
    start = time.time()
    process = psutil.Process(process_id)
    BLOCKSIZE = os.statvfs(".").f_bsize
    storage_available = os.statvfs(".").f_bavail * BLOCKSIZE
    memory_percent = process.memory_percent()
    pipe.send((memory_percent, storage_available))

    # every 1 second, send the amount of memory used and the storage available
    while True:
        if time.time() - start > timeout:
            pipe.close()
            break
        time.sleep(1)
        storage_available = os.statvfs(".").f_bavail * BLOCKSIZE
        memory_percent = process.memory_percent()
        pipe.send((memory_percent, storage_available))
