# import the necessary packages
from picamera.array import PiRGBArray
import numpy as np
import time
import RPi.GPIO as GPIO
import time


# this class lets us read PWM signals and store a history of their values
class PWMPin:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self.data = []

    # collect a datapoint and save how long it was high
    def collect_data_point(self):
        GPIO.wait_for_edge(self.pin, GPIO.RISING)
        start_time = time.time_ns()
        while GPIO.input(self.pin):
            pass
        end_time = time.time_ns()
        self.data.append(end_time - start_time)
        return self.data[-1]

    # as collect_data_point but uses wait_for_edge twice
    def collect_data_point2(self):
        GPIO.wait_for_edge(self.pin, GPIO.RISING)
        start_time = time.time_ns()
        GPIO.wait_for_edge(self.pin, GPIO.FALLING)
        end_time = time.time_ns()
        self.data.append(end_time - start_time)
        return self.data[-1]

    # save to data a tuple of (duty cycle, time_high, period)
    def collect_data_point3(self):
        GPIO.wait_for_edge(self.pin, GPIO.RISING)
        rise_time = time.time_ns()
        while GPIO.input(self.pin):
            pass
        fall_time = time.time_ns()
        while not GPIO.input(self.pin):
            pass
        period_time = time.time_ns()
        self.data.append(
            (
                (fall_time - rise_time) / (period_time - rise_time),
                fall_time - rise_time,
                period_time - rise_time,
            )
        )
        return self.data[-1]

    def get_data(self):
        return np.array(self.data)

    def clear_data(self):
        self.data = []
