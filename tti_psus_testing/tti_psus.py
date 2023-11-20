import math
import numbers
import time
from math import isclose

from serial_controllers import TtiQL1ChPsu


def _truncate_float(number, n):
    md = 10 ** n
    return int(number * md) / md


class TtiQL564P(TtiQL1ChPsu):
    """
    TTI QL564P / QL355P 1 channel PSU basic controller
    """

    def enableOutput(self, enable):
        self._write(f'OP{str(1)} {str(1 if enable else 0)}')

    def set_output(self, voltage=0.0, current=0.0):
        """
        Set output voltage and current limits at specific channel

        NOTE: be careful when changing voltage and current settings when outputs are engaged. There may also be a time
        delay between setting voltage and current limit that can cause transient state which could be dangerous
        for your DUT.

        Parameters
        ----------
        channel : int
            channel number(s)
        voltage : float
            channel voltage limit in volts
        current : float
            channel current limit in ampere
        Returns
        -------
            None
        """
        super(TtiQL1ChPsu, self).set_output(1, voltage, current)

    def set_over_current_protection(self, current):
        self._write(f'OCP{str(1)} {str(current)}')

    def set_range(self, _range):
        """
        QL355 Models: 0=15V(5A), 1=35V(3A), 2=35V(500mA)
        QL564 Models: 0=25V(4A), 1=56V(2A), 2=56V(500mA)
        :param channel:
        :param _range: 0, 1 or 2
        :return: None
        """

        self._write(f'RANGE{str(1)} {str(_range)}')

    def measure_voltage(self):
        return float(super(TtiQL1ChPsu, self).get_input(1)[0])

    def measure_current(self):
        resp = super(TtiQL1ChPsu, self).get_input(1)
        return float(resp[2])

    def current_ramp_down(self, step, _delay, voltage_limit, output_off=True):
        if step < 0.001:
            raise 'step too low!!!'
        actual_current = self.measure_current()
        while not isclose(actual_current, step, abs_tol=0.01):
            next_current = _truncate_float(actual_current - step, 3)
            if next_current <= 0.0:
                break
            self.set_output(voltage_limit, next_current)
            actual_current = next_current
            time.sleep(_delay)
        self.enableOutput(not output_off)

    def current_ramp_up(self, start, stop, step, _delay, _voltage_limit, output_on=True):
        if step < 0.001:
            raise 'step too low!!!'
        self.current_ramp_down(step, _delay, _voltage_limit, False)
        self.enableOutput(output_on)
        self.set_output(_voltage_limit, start)
        actual_current = start
        while True:
            next_current = _truncate_float(actual_current + step, 3)
            if next_current > stop:
                break
            self.set_output(_voltage_limit, next_current)
            # we could have measured the current at the instrument output but is too slow
            # problem? We will not be aware if we will reach the limits
            actual_current = next_current
            time.sleep(_delay)


if __name__ == "__main__":

    psu = TtiQL564P('COM8')
    psu.initialize()

    maxI = 2.0
    startI = 0.0
    stepI = 0.1
    stepUpDelay = 0.5
    stepDownDelay = 0.25
    voltage_limit = 4.0
    while True:
        psu.current_ramp_up(startI, maxI, stepI, stepUpDelay, voltage_limit, True)
        time.sleep(5)
        psu.current_ramp_down(stepI, stepDownDelay, voltage_limit, False)
