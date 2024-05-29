from machine import Pin
import time,random

from PicoDHT22 import PicoDHT22



class Temperature:
    def __init__(self, internal_pin = 13, external_pin = 1):
        self.internal_sensor = PicoDHT22(Pin(internal_pin,Pin.IN,Pin.PULL_UP))
        self.external_sensor = PicoDHT22(Pin(external_pin,Pin.IN,Pin.PULL_UP))
    
    def acquire_temperature(self, which="INTERNAL"):
        timestamp = time.time()
        if which == "INTERNAL":
            T, H = self.internal_sensor.read()
            return timestamp, T, H
        else:
            T, H = self.external_sensor.read()
            return timestamp, T, H

    def read_all_sensors(self):
      timestamp, T_in, H_in = self.acquire_temperature("INTERNAL")
      timestamp, T_out, H_out = self.acquire_temperature("EXTERNAL")
      return T_in, H_in, T_out, H_out,timestamp