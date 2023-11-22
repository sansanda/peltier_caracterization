# Script para verificar el buen funcionamiento del driver de la fuente de alimentacion
# Owon SPE6103 con sn: SPE610322380172
import time
from math import isclose
from owon_psu import OwonPSU

import logging
FORMAT = '%(asctime)s:%(funcName)s:%(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG, datefmt='%m/%d/%Y %I:%M:%S %p')


def _truncate_float(number, n):
    md = 10**n
    return int(number * md) / md


class OwonSPE6103(OwonPSU):
    """
    OwonSPE6103 1 channel PSU basic controller
    """

    def __init__(self, port, default_timeout=0.5):
        super().__init__(port, default_timeout)

    def measure_current(self):
        current = super().measure_current()
        logging.info(self.__class__.__name__ + ": Measuring current... current = %s", current)
        return current

    def measure_voltage(self):
        voltage = super().measure_voltage()
        logging.info(self.__class__.__name__ + ": Measuring voltage... voltage = %s", voltage)
        return voltage

    def set_voltage(self, _voltage):
        logging.info(self.__class__.__name__ + ": Setting voltage to = %s", _voltage)
        super().set_voltage(_voltage)

    def set_current(self, _current):
        logging.info(self.__class__.__name__ + ": Setting current to = %s", _current)
        super().set_current(_current)

    def current_ramp_down(self, _step, _voltage_limit, _delay, output_off=True):
        logging.debug(self.__class__.__name__ +
                      ": Call with parameters _step = %s, "
                      "_voltage_limit = %s, "
                      "_delay = %s, "
                      "output_off = %s.",
                      _step,
                      _voltage_limit,
                      _delay,
                      output_off)
        if _step < 0.001:
            raise 'step too low!!!'
        self.set_voltage_limit(_voltage_limit)
        actual_current = self.measure_current()
        while not isclose(actual_current, 0.0, abs_tol=0.001):
            next_current = _truncate_float(actual_current - _step, 3)
            if next_current <= 0.0:
                self.set_current(0.0)
                break
            self.set_current(next_current)
            # we could have measured the cuurent at the instrument output but is too
            # problem?
            # We will not be aware if we will reach the zero suddenly (ex disconnect the load)
            actual_current = next_current
            time.sleep(_delay)
        if output_off:
            self.set_output(False)

    def current_ramp_up(self, _start, _stop, _step, _voltage_limit, _delay, output_on=True):
        logging.debug(self.__class__.__name__ +
                      ": Call with parameters _start = %s, "
                      "_stop = %s, "
                      "_step = %s, "
                      "_voltage_limit = %s, "
                      "_delay = %s, "
                      "output_on = %s.",
                      _start,
                      _stop,
                      _step,
                      _voltage_limit,
                      _delay,
                      output_on)
        if _step < 0.001:
            raise 'step too low!!!'
        self.set_voltage_limit(_voltage_limit)
        # self.current_ramp_down(_step, _delay, _voltage_limit, False)
        self.set_output(output_on)
        if _start:
            self.set_current(_start)
            time.sleep(1)
        actual_current = self.measure_current()
        while True:
            next_current = _truncate_float(actual_current + _step, 4)
            logging.debug(self.__class__.__name__ + " - actual current = %s, step = %s, next current = %s",
                          actual_current, _step, next_current)
            if next_current > _stop:
                self.set_current(_stop)
                break
            self.set_current(next_current)
            # we could have measured the current at the instrument output but is too slow
            # problem? We will not be aware if we will reach the limits
            actual_current = next_current
            logging.debug("OwonSPE6103: delay = %s", _delay)
            time.sleep(_delay)

if __name__ == "__main__":

    with OwonSPE6103("COM9") as opsu:

        voltage_limit = 4.0  # volts
        current_limit = 4.0  # amps

        maxI = 2
        startI = 0
        stepI = 0.05
        stepUpDelay = 0.4
        stepDownDelay = 0.1
        voltage_limit = 4
        while True:
            opsu.current_ramp_up(startI, maxI, stepI, stepUpDelay, voltage_limit, True)
            time.sleep(5)
            opsu.current_ramp_down(stepI, stepDownDelay, voltage_limit, False)

