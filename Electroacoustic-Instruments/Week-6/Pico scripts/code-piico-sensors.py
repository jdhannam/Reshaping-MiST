'''
# 1. check board
import sys
import board
import busio
import adafruit_lis3dh

print(sys.implementation)
print(dir(board))
print(board.board_id)

'''


'''
# 2. check you can see the sensors address
import board
import busio

i2c = busio.I2C(board.GP9, board.GP8) # Pico attached to expansion board
while not i2c.try_lock():
    pass

print([hex(x) for x in i2c.scan()])
i2c.unlock()
'''



'''
# using the piicodev LIS3DH sensor ['0x19']
import board
import busio
import adafruit_lis3dh
import time

i2c = busio.I2C(board.GP9, board.GP8)
lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x19)

while True:
    print(lis3dh.acceleration)
    time.sleep(0.1)
'''



'''
# using the piicodev VEML6040 sensor ['0x10']
import board
import busio
from piicodev_veml6040_circuitpython import VEML6040

i2c = busio.I2C(board.GP9, board.GP8)
sensor = VEML6040(i2c)

while True:
    rgb = sensor.read_rgb()

    print(
        rgb["red"],
        rgb["green"],
        rgb["blue"],
        rgb["white"]
    )

    print("Lux:", rgb["als"])
    print("CCT:", rgb["cct"])

    print(sensor.read_hsv())
    print(sensor.classify_hue())

    print()
'''


'''
# using the piicodev cap1203 sensor ['0x28']
import board
import busio
import time
from piicodev_cap1203_circuitpython import CAP1203

i2c = busio.I2C(board.GP9, board.GP8)

sensor = CAP1203(
    i2c,
    touchmode="multi",
    sensitivity=6
)

print("Sensitivity =", sensor.sensitivity)

while True:

    print("Touch:", sensor.read())
    print("Delta:", sensor.read_delta_counts())
    print()
    time.sleep(0.1)
'''


'''
# using the piicodev Ultrasonic sensor ['0x35']
import board
import busio
import time

from piicodev_ultrasonic_circuitpython import (
    PiicoDevUltrasonic
)

i2c = busio.I2C(
    board.GP9,
    board.GP8
)

sensor = PiicoDevUltrasonic(i2c)

print("Device ID:", sensor.whoami)
print("Firmware:", sensor.firmware)

while True:
    print(sensor.distance_mm, "mm")
    time.sleep(0.1)
'''


'''
# this piicodev mpu6050 board is no longer sold (accel,gyro,temp)
import board
import busio
import adafruit_mpu6050
import time

i2c = busio.I2C(board.GP9, board.GP8)
mpu = adafruit_mpu6050.MPU6050(i2c)

while True:
    print("Accel:", mpu.acceleration)
    print("Gyro :", mpu.gyro)
    print("Temp :", mpu.temperature)
    time.sleep(0.1)
'''


'''
# this piicodev QMC6310 board is no longer sold (magnotometer) ['0x1c']
# piicodev_qmc610_circuitpython
import board
import busio
import time

from piicodev_qmc610_circuitpython import QMC6310

# PiicoDev Expansion Board I2C
i2c = busio.I2C(board.GP9, board.GP8)

# Initialise sensor
compass = QMC6310(
    i2c,
    range=3000,    # ±3000 uT
    odr=3,         # highest output data rate
)
compass.set_declination(11.8) # Melbourne

while True:

    xyz = compass.read()

    print(
        "X={:.1f}uT  Y={:.1f}uT  Z={:.1f}uT".format(
            xyz["x"],
            xyz["y"],
            xyz["z"]
        )
    )

    print("Heading = {:.1f}°".format(compass.read_heading()))
    print("Magnitude = {:.1f}uT".format(compass.read_magnitude()))
    print()
    time.sleep(0.2)
'''


'''
# this for the piicodev BME280 board ['0x77']
import board
import busio
from adafruit_bme280 import basic as adafruit_bme280

# PiicoDev Expansion Board
i2c = busio.I2C(board.GP9, board.GP8)
bme = adafruit_bme280.Adafruit_BME280_I2C(i2c,address=0x77)

while True:

    print("Temperature:",bme.temperature,"°C")
    print("Pressure:",bme.pressure,"hPa")
    print("Humidity:",bme.relative_humidity,"%")
    print("Altitude:",bme.altitude,"m")
    print()
'''


'''
# this for the piicodev Buzzer board ['0x5C']
import board
import busio
import time

from piicodev_buzzer_circuitpython import PiicoDevBuzzer

i2c = busio.I2C(
    board.GP9,
    board.GP8
)

buzzer = PiicoDevBuzzer(i2c)

print("Firmware:", buzzer.firmware)
print("Device ID:", hex(buzzer.read_id()))

# A4
buzzer.tone(440, 500)
time.sleep(1)

# C5
buzzer.tone(523, 500)
time.sleep(1)

# E5
buzzer.tone(659, 500)
time.sleep(1)

buzzer.no_tone()
'''


'''
# this for the piicodev RGB LED board ['0x8']
# piicodev_RGBLED_circuitpython
import board
import busio
import time
from piicodev_RGBLED_circuitpython import PiicoDevRGB, wheel

# PiicoDev Expansion Board I2C
i2c = busio.I2C(board.GP9, board.GP8)

# RGB module
rgb = PiicoDevRGB(i2c,brightness=50)

# --------------------------------------------------
# Example 1 - Individual LEDs
# --------------------------------------------------

print("Example 1: RGB LEDs")

rgb.set_pixel(0, (255, 0, 0))
rgb.set_pixel(1, (0, 255, 0))
rgb.set_pixel(2, (0, 0, 255))
rgb.show()

time.sleep(3)

# --------------------------------------------------
# Example 2 - Fill all LEDs
# --------------------------------------------------

print("Example 2: Fill Yellow")
rgb.fill((255, 255, 0))
time.sleep(3)

# --------------------------------------------------
# Example 3 - Rainbow Animation
# --------------------------------------------------

print("Example 3: Rainbow")
h = 0
for _ in range(200):
    rgb.fill(wheel(h))
    h += 0.01
    if h >= 1:
        h = 0

    time.sleep(0.02)

# --------------------------------------------------
# Example 4 - Chase Pattern
# --------------------------------------------------

print("Example 4: Chase")

while True:
    for i in range(3):
        rgb.clear()
        rgb.set_pixel(i,(255, 0, 0))
        rgb.show()
        time.sleep(0.1)
'''



'''
# this for the piicodev VL53L1X Laser Distance board ['0x29']
# adafruit_vl53l1x.mpy

import board
import busio
import time
import adafruit_vl53l1x

# PiicoDev Expansion Board I2C
i2c = busio.I2C(board.GP9, board.GP8)
tof = adafruit_vl53l1x.VL53L1X(i2c)
tof.start_ranging()

while True:
    if tof.data_ready:
        print("Distance:",tof.distance,"cm")
        tof.clear_interrupt()

    time.sleep(0.1)
'''



'''
# this for the piicodev 128x2 I2C LCD
import board
import busio
import adafruit_ssd1306

i2c = busio.I2C(board.GP9, board.GP8)
display = adafruit_ssd1306.SSD1306_I2C(128,64,i2c,addr=0x3C)

display.fill(0)
display.text(
    "Hello PiicoDev!",
    0,
    0,
    1
)

display.show()
'''


'''
# this for the piicodev RFID board
import board
import busio
import time
from piicodev_rfid_circuitpython import PiicoDev_RFID

i2c = busio.I2C(board.GP9,board.GP8)
rfid = PiicoDev_RFID(i2c)

while True:

    if rfid.tagPresent():
        uid = rfid.readID()

        if uid:
            print("UID:", uid)
            value = int(uid.replace(":", ""), 16)
            badge_id = value % 10000
            print("badge_id:", badge_id)
        time.sleep(1)
        
    time.sleep(0.05)
'''



'''
# Simple test of the MPR121 capacitive touch sensor librar
import time
import board
import busio
import adafruit_mpr121


i2c = busio.I2C(board.GP9, board.GP8)
mpr121 = adafruit_mpr121.MPR121(i2c)

# Note you can optionally change the address of the device:
# mpr121 = adafruit_mpr121.MPR121(i2c, address=0x91)

while True:
    # Loop through all 12 inputs (0-11).
    for i in range(12):
        if mpr121[i].value:
            print(f"Input {i} touched!")
    time.sleep(0.25)  # Small delay to keep from spamming output messages.
'''



'''
# this is audio code for waveshare and MAX98357A amp board
import board
import audiobusio
import audiomixer
import synthio
import array
import math
import time

audio = audiobusio.I2SOut(
    bit_clock=board.GP27,       # BCLK MAX98357A
    word_select=board.GP28,     # LRC MAX98357A
    data=board.GP26,            # DIN MAX98357A
)

mixer = audiomixer.Mixer(
    voice_count=1,
    sample_rate=22050,
    channel_count=1,
    bits_per_sample=16,
    samples_signed=True,
)

audio.play(mixer)

synth = synthio.Synthesizer(sample_rate=22050,channel_count=1,)
mixer.voice[0].play(synth)

wave = array.array("h",[int(32767 * math.sin(2 * math.pi * i / 256))
     for i in range(256)]
)

note = synthio.Note(
    frequency=440,
    amplitude=0.25,
    waveform=wave
)

print("Playing A4...")

synth.press(note)

while True:
    time.sleep(1)
'''



'''
# this for the piicodev MMC5603 Magnotometer board
# compass calculation

import board
import time

from piicodev_mmc5603_circuitpython import MMC5603

i2c = board.I2C()

compass = MMC5603(i2c)

compass.set_declination(11.8)

while True:

    xyz = compass.read()

    print(
        "X={:.1f}uT Y={:.1f}uT Z={:.1f}uT".format(
            xyz["x"],
            xyz["y"],
            xyz["z"]
        )
    )

    print(
        "Heading:",
        compass.read_heading()
    )

    time.sleep(0.2)
'''


'''
# this for the piicodev MMC5603 Magnotometer board
# Magnet detction calculation

import board
import time

from piicodev_mmc5603_circuitpython import MMC5603

i2c = board.I2C()

compass = MMC5603(i2c)

print("Calibrating baseline...")
time.sleep(2)

baseline = compass.read_magnitude()

print("Baseline =", baseline)

while True:

    strength = compass.read_magnitude()

    delta = abs(strength - baseline)

    print(
        "Strength = {:.1f}uT".format(strength),
        "Change = {:.1f}uT".format(delta)
    )

    if delta > 50:
        print("MAGNET DETECTED!")

    time.sleep(0.2)
'''