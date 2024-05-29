import dht
import time
import machine
from machine import Pin
from time import sleep

from actuator import Actuation
from sensor import Temperature
temperature = Temperature()


class PID:
    def __init__(self, Kp, Ki, Kd, T_set,threshold,actuation):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.last_time = time.time()
        self.T_set = T_set
        self.last_error = 0.0
        self.integral = 0
        self.derivative=0
        self.output=0
        self.threshold=threshold
        self.actuation=actuation
        actuation.heating_set(0)
        actuation.fan_set(0)
        
    def actuate(self, T_in, T_out):
        error = 0
        if T_in < (self.T_set - self.threshold):
            error = (self.T_set - self.threshold) - T_in
        elif T_in > (self.T_set + self.threshold):
            error = (self.T_set + self.threshold) - T_in
        
        current_time = time.time()
        delta_time = current_time - self.last_time
        delta_error = error - self.last_error
        
        if error < 0.5:
            self.integral += error * delta_time
        
        if delta_time > 0:
            self.derivative = delta_error / delta_time
        
        self.output = (self.Kp * error) + (self.Ki * self.integral) + (self.Kd * self.derivative)
        
        if self.output > 0:
            self.actuation.heating_set(self.output * 100)
            self.actuation.fan_set(0)
        elif self.output < 0 and T_in > T_out:
            self.actuation.heating_set(0)
            self.actuation.fan_set(self.output * -100)
        else:
            self.actuation.heating_off()
            self.actuation.fan_off()
        
        self.last_time = current_time
        self.last_error = error
        
    def off(self):
        self.actuation.heating_off()
        self.actuation.fan_off()
        
    def set_values(self,Kp,Ki,Kd,T_set,threshold):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.T_set = T_set
        self.threshold=threshold
        
        

class on_off:
    
    def __init__(self,setpoint,threshold,actuation):
        self.setpoint=setpoint
        self.threshold=threshold
        self.actuation = actuation
        actuation.heating_set(0)
        actuation.fan_set(0)

    def actuate(self,T_in,T_out):
        #T_in, H_in, T_out, H_out,timestamp = temperature.read_all_sensors()
        
        if T_in < self.setpoint-self.threshold:
            self.actuation.heating_set(100)
            self.actuation.fan_set(0)
        elif T_in > self.setpoint+self.threshold and T_in>T_out:
            self.actuation.heating_set(0)
            self.actuation.fan_set(100)
        
    def off(self):
        self.actuation.heating_off()
        self.actuation.fan_off()
        
    def set_values(self, setpoint, treshold):
        self.setpoint = setpoint
        self.threshold = treshold