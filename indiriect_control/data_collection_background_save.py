# import the necessary packages
from pickletools import uint8
from picamera.array import PiRGBArray
from picamera import PiCamera
import pickle
import numpy as np
import time
import cv2
import time
from pwm_pin import PWMPin
import RPi.GPIO as GPIO
import os
from system_monitor import monitor_system
from data_saver import save_data
from multiprocessing import Pipe, Process

LINE_UP = "\033[1A"
LINE_CLEAR = "\x1b[2K"
RES = (320, 240)
VIDEO_LENGTH = 60
FRAMERATE = 10
TOTAL_FRAMES = VIDEO_LENGTH * FRAMERATE

motor_input = PWMPin(10)
servo_input = PWMPin(3)

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(38, GPIO.OUT)
GPIO.setup(40, GPIO.OUT)
motor_output = GPIO.PWM(38, 57)
servo_output = GPIO.PWM(40, 57)
motor_output.start(8)
servo_output.start(8)

camera = PiCamera()
camera.vflip = True
camera.resolution = RES
camera.framerate = FRAMERATE
rawCapture = PiRGBArray(camera, size=RES)

camera.start_preview()

mon_parent, mon_child = Pipe()
monitor = Process(target=monitor_system, args=(mon_child, os.getpid()), daemon=True)
monitor.start()
lines = 0

save_parent, save_child = Pipe()
saver = Process(target=save_data, args=(save_child,), daemon=True)
saver.start()
saves_in_progress = 0

points_taken = 0
print("Running")
time.sleep(2)

low_storage = False
print("Recording Started")
video = np.empty(shape=(TOTAL_FRAMES, RES[1], RES[0], 3), dtype="uint8")
f_time = time.time_ns()
try:
    while True:
        for fnum, frame in enumerate(
            camera.capture_continuous(rawCapture, format="bgr", use_video_port=True)
        ):
            # motor_input.collect_data_point()
            motor_output.ChangeDutyCycle(motor_input.collect_data_point() * 100)
            servo_output.ChangeDutyCycle(servo_input.collect_data_point() * 100)
            video[fnum] = frame.array.astype("uint8")
            rawCapture.truncate(0)
            new_time = time.time_ns()

            if mon_parent.poll():
                for i in range(lines):
                    print(LINE_UP, end=LINE_CLEAR)
                lines = 0

                if save_parent.poll():
                    st = save_parent.recv()
                    saves_in_progress -= 1
                    print(st[0])

                # motor_output.ChangeDutyCycle(motor_input.collect_data_point() * 100)
                # servo_output.ChangeDutyCycle(servo_input.collect_data_point() * 100)
                print(f"motor: {motor_input.data[-1]}")
                print(f"servo: {servo_input.data[-1]}")

                print(f"current video progress: {fnum}/{TOTAL_FRAMES}")
                print(
                    "Period: "
                    + str((new_time - f_time) / 10**9)
                    + " expected: "
                    + str(1 / FRAMERATE)
                )
                lines += 4
                vitals = mon_parent.recv()
                mem_perc = vitals[0]
                storage = vitals[1]
                print(
                    f"storage: {round(storage/1048576, 2)}MB \npercent memory used: {round(mem_perc,2)}"
                )
                lines += 2
                if storage < 2000000000:
                    print("Warning, low storage. finish last run")
                    lines += 1
                    if storage < 1158782464:
                        print("storage too low")
                        camera.close()
                        exit()
            f_time = new_time
            if fnum >= TOTAL_FRAMES - 1:
                save_parent.send(
                    (video, motor_input.get_data(), servo_input.get_data())
                )
                motor_input.clear_data()
                servo_input.clear_data()
                saves_in_progress += 1
                video = np.empty(shape=(TOTAL_FRAMES, RES[1], RES[0], 3), dtype="uint8")
                if storage < 2000000000:
                    print("Storage low, datacollection stopped")
                    while True:
                        print(f"Saving {saves_in_progress} datasets to memory")
                        time.sleep(1)
                        if save_parent.poll():
                            save_parent.recv()
                            saves_in_progress -= 1
                        if saves_in_progress == 0:
                            break
                        print(LINE_UP, end=LINE_CLEAR)
                    camera.close()
                    exit()
                break
except KeyboardInterrupt:
    print("Exiting")
    motor_output.stop()
    servo_output.stop()
    while True:
        print(f"Saving {saves_in_progress} datasets to memory")
        time.sleep(1)
        if save_parent.poll():
            save_parent.recv()
            saves_in_progress -= 1
        if saves_in_progress == 0:
            break
        print(LINE_UP, end=LINE_CLEAR)
    camera.close()
    exit()
