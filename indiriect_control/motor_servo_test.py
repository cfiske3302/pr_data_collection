import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(3, GPIO.OUT)
GPIO.setup(10, GPIO.OUT)

pwm_m = GPIO.PWM(3, 57)
pwm_s = GPIO.PWM(10, 57)

motor, servo = input().split(",")
pwm_m.start(float(motor))
pwm_s.start(float(servo))

try:
    while True:
        motor, servo = input().split(",")
        pwm_m.ChangeDutyCycle(float(motor))
        pwm_s.ChangeDutyCycle(float(servo))
except:
    pass

pwm_m.stop()
GPIO.cleanup()