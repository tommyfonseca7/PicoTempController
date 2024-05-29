from machine import Pin, PWM


class Actuation:
    def __init__(self, heating_pin = 16, heating_freq = 1000, fan_pin = 15, fan_freq = 1000):
        # Define PWM output for PIN Corresponding to the heating element
        self.heating = PWM(Pin(heating_pin, Pin.OUT))
        self.heating.freq(heating_freq)
        # Define PWM output for PIN Corresponding to the fan
        self.fan = PWM(Pin(fan_pin, Pin.OUT))
        self.fan.freq(fan_freq)
        # Make sure components are off when initializing actuation component
        self.fan_off()
        self.heating_off()

    def heating_off(self):
        self.heating.duty_u16(0)
        self.heat_state = 0
    
    def fan_off(self):
        self.fan.duty_u16(0)
        self.fan_state = 0
    
    def heating_set(self, percentage):
        target = int((65535 * percentage) / 100) # range de 64700-65000
        self.heating.duty_u16(target)
        self.heat_state = percentage
        self._heat_duty = target
    
    def fan_set(self, percentage):
        target = int((65535 * percentage) / 100) # range de 64700-65000
        self.fan.duty_u16(target)
        self.fan_state = percentage
        self._fan_duty = target

    def fan_percentage(self):
        if self.fan_state > 100:
            return 100
        else:
            return self.fan_state

    def heater_percentage(self):
        if self.heat_state > 100:
            return 100

        else:
            return self.heat_state
     