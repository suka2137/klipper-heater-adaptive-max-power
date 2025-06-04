# Based on Heater/sensor verification code
#
# Copyright (C) 2018  Kevin O'Connor <kevin@koconnor.net>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging

class HeaterAdapt:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.gcode = config.get_printer().lookup_object('gcode')
        self.printer.register_event_handler("klippy:connect",
                                            self.handle_connect)
        self.printer.register_event_handler("klippy:shutdown",
                                            self.handle_shutdown)
        self.heater_name = config.get_name().split()[1]
        self.heater = None
        self.temp_sensor = config.get('temp_sensor', default=None)

        self.temp_points = sorted(config.getlists('temp_points', seps=(',', '\n',), count=2),
                                  key=lambda k : float(k[0]))
        self.temp_points = list(map(lambda c : (float(c[0]), float(c[1])), self.temp_points))
        logging.info(self.temp_points)

        self.goal_systime = self.printer.get_reactor().NEVER
        self.check_timer = None
    def handle_connect(self):
        pheaters = self.printer.lookup_object('heaters')
        self.heater = pheaters.lookup_heater(self.heater_name)
        if self.temp_sensor == None:
            self.temp_sensor = self.heater
        else:
            self.temp_sensor = self.printer.lookup_object(f"temperature_sensor {self.temp_sensor}")
        reactor = self.printer.get_reactor()
        self.check_timer = reactor.register_timer(self.check_event, reactor.NOW)
    def handle_shutdown(self):
        if self.check_timer is not None:
            reactor = self.printer.get_reactor()
            reactor.update_timer(self.check_timer, reactor.NEVER)
    def temp_to_power(self, temp: float):
        low = tuple(self.temp_points[0])
        high = low
        for point_temp, point_power in self.temp_points:
            if point_temp <= temp:
                low = (point_temp, point_power)
                high = low
            else:
                high = (point_temp, point_power)
                break
        tempSpan = high[0] - low[0]
        pwrSpan = high[1] - low[1]
        scale = (temp - low[0]) / tempSpan if tempSpan else 1.0
        target_max_power = low[1] + (scale * pwrSpan)
        return min(max(0.0, target_max_power), 1.0)
    def check_event(self, eventtime):
        temp, temp_target = self.temp_sensor.get_temp(eventtime)
        target_max_power = self.temp_to_power(temp)
        #logging.info("temp: %.2f power: %.2f" % (temp, target_max_power))
        self.heater.max_power = target_max_power
        self.heater.control.heater_max_power = target_max_power
        try:
            if self.heater.control.Ki:
                self.heater.control.temp_integ_max = target_max_power / self.heater.control.Ki
        except:
            pass
        return eventtime + 1.

def load_config_prefix(config):
    return HeaterAdapt(config)
