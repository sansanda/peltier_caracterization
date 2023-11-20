# Script para verificar el buen funcionamiento del driver de la fuente de alimentacion
# Owon SPE6103 con sn: SPE610322380172
import time
from math import isclose
from owon_psu import OwonPSU


def _truncate_float(number, n):
    md = 10**n
    return int(number * md) / md


class OwonSPE6103(OwonPSU):
    """
    OwonSPE6103 1 channel PSU basic controller
    """

    def __init__(self, port, default_timeout=0.5):
        super().__init__(port, default_timeout)

    def current_ramp_down(self, step, _delay, _voltage_limit, output_off=True):
        if step < 0.001:
            raise 'step too low!!!'
        self.set_voltage_limit(_voltage_limit)
        actual_current = self.measure_current()
        while not isclose(actual_current, step, abs_tol=0.01):
            next_current = _truncate_float(actual_current - step, 3)
            if next_current <= 0.0:
                break
            self.set_current(next_current)
            # we could have measured the cuurent at the instrument output but is too
            # problem?
            # We will not be aware if we will reach the zero suddenly (ex disconnect the load)
            actual_current = next_current
            time.sleep(_delay)
        if output_off:
            self.set_output(False)

    def current_ramp_up(self, start, stop, step, _delay, _voltage_limit, output_on=True):
        if step < 0.001:
            raise 'step too low!!!'
        self.set_voltage_limit(_voltage_limit)
        self.current_ramp_down(step, _delay, _voltage_limit, False)
        self.set_output(output_on)
        self.set_current(start)
        actual_current = self.measure_current()
        while True:
            next_current = _truncate_float(actual_current + step, 3)
            if next_current > stop:
                break
            self.set_current(next_current)
            # we could have measured the current at the instrument output but is too slow
            # problem? We will not be aware if we will reach the limits
            actual_current = next_current
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

