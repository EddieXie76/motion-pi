#!/usr/bin/python
# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO
import time
import urllib.request

Clock = 16
Address = 20
DataOut = 21

Start = 19
Pause = 26
Led = 17

Status = GPIO.HIGH
Brightness = 150
Min = 10
Max = 690

def ADC_Read(channel):
    value = 0;
    for i in range(0,4):
        if((channel >> (3 - i)) & 0x01):
            GPIO.output(Address,GPIO.HIGH)
        else:
            GPIO.output(Address,GPIO.LOW)
        GPIO.output(Clock,GPIO.HIGH)
        GPIO.output(Clock,GPIO.LOW)
    for i in range(0,6):
        GPIO.output(Clock,GPIO.HIGH)
        GPIO.output(Clock,GPIO.LOW)
    time.sleep(0.001)
    for i in range(0,10):
        GPIO.output(Clock,GPIO.HIGH)
        value <<= 1
        if(GPIO.input(DataOut)):
            value |= 0x01
        GPIO.output(Clock,GPIO.LOW)

    return value

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin
    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)
    # Convert the 0-1 range into a value in the right range.
    result = rightMin + (valueScaled * rightSpan)
    result = min(result, rightMax)
    result = max(result, rightMin)
    return result

def changeBrightness():
    print("Brightness %d" %Brightness)
    params = urllib.parse.urlencode({'brightness': Brightness})
    opener.open("http://localhost:8080/0/config/set?%s" % params)
    return

def changeStatus():
    GPIO.output(Led, Status)
    cmd = "pause" if Status==GPIO.LOW else "start"
    print("Detection %s" %cmd)
    opener.open("http://localhost:8080/0/detection/%s" % cmd)
    return

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(Clock,GPIO.OUT)
GPIO.setup(Address,GPIO.OUT)
GPIO.setup(DataOut,GPIO.IN,GPIO.PUD_UP)
GPIO.setup(Start,GPIO.IN)
GPIO.setup(Pause,GPIO.IN)
GPIO.setup(Led,GPIO.OUT)

# create a password manager
password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
password_mgr.add_password(None, "http://localhost:8080", "derbysoft", "derBYs0ft")
handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
opener = urllib.request.build_opener(handler)
urllib.request.install_opener(opener)

try:
    changeBrightness()
    changeStatus()
except:
    pass

while True:
    try:
        NewBrightness = translate(ADC_Read(10), Min, Max, 0, 255)
        if abs(Brightness-NewBrightness) > 5:
            Brightness = NewBrightness
            changeBrightness()
        if GPIO.input(Start) == GPIO.HIGH and Status == GPIO.LOW:
            Status = GPIO.HIGH         
            changeStatus()
        if GPIO.input(Pause) == GPIO.HIGH and Status == GPIO.HIGH:
            Status = GPIO.LOW
            changeStatus()
        time.sleep(0.1)
    except:      
        pass

