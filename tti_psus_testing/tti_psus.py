import time
from serial_controllers import TtiQL1ChPsu
from utils.numbers_utils import truncate_float

import logging
FORMAT = '%(asctime)s:%(levelname)s:%(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO, datefmt='%m/%d/%Y %I:%M:%S %p')


class TtiQL564P(TtiQL1ChPsu):
    """
    TTI QL564P / QL355P 1 channel PSU basic controller
    """

    def enable_output(self, enable):
        self._write(f'OP{str(1)} {str(1 if enable else 0)}')

    def set_current(self, _current, _voltage_limit):
        logging.info(self.__class__.__name__ + ": Setting current to %s", _current)
        super().set_output(1, _voltage_limit, _current)

    def set_over_current_protection(self, _current):
        logging.info(self.__class__.__name__ + ": Setting current protection to %s", _current)
        self._write(f'OCP{str(1)} {str(_current)}')

    def set_range(self, _range):
        """
        QL355 Models: 0=15V(5A), 1=35V(3A), 2=35V(500mA)
        QL564 Models: 0=25V(4A), 1=56V(2A), 2=56V(500mA)
        :param _range: 0, 1 or 2
        :return: None
        """
        logging.info("setting range to %s", _range)
        self._write(f'RANGE{str(1)} {str(_range)}')

    def measure_voltage(self):
        response = super(TtiQL1ChPsu, self).get_input(1)
        logging.info(self.__class__.__name__ + ": Measuring voltage... response_data = %s", response)
        voltage = float(response[0])
        logging.info(self.__class__.__name__ + ": Measuring voltage... voltage = %s", voltage)
        return voltage

    def measure_current(self):
        response = super(TtiQL1ChPsu, self).get_input(1)
        logging.info(self.__class__.__name__ + ": Measuring current... response_data = %s", response)
        current = float(response[2])
        logging.info(self.__class__.__name__ + ": Measuring current... current = %s", current)
        return current

    def current_ramp_down(self, _step, _stop, _voltage_limit, _delay, output_off=True):
        logging.info(self.__class__.__name__ + ": Ramping current down to %s...", _stop)

        if _step < 0.001:
            raise Exception('step too low!!!')
        if _stop < 0.0:
            raise Exception('Value for stop current cannot be less than zero!!!')

        actual_current = self.measure_current()
        logging.info(self.__class__.__name__ + ": Ramping current down to zero from... %s to %s.",
                     actual_current, _stop)

        while True:
            next_current = truncate_float(actual_current - _step, 4)
            logging.debug("actual current = %s, step = %s, next current = %s",
                          actual_current, _step, next_current)
            if next_current < _stop:
                self.set_current(_stop, _voltage_limit)
                break
            self.set_current(next_current, _voltage_limit)
            # we could have measured the current at the instrument output but is too slow
            # problem? We will not be aware if we will reach the limits
            actual_current = next_current
            time.sleep(_delay)

        self.enable_output(not output_off)
        logging.info(self.__class__.__name__ + ": Ramping current down to %s DONE!", _stop)

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
            raise Exception('step too low!!!')
        # self.current_ramp_down(_step, _voltage_limit, _delay, False)
        self.enable_output(output_on)
        if _start:
            self.set_current(_start, _voltage_limit)
            time.sleep(1)
        actual_current = self.measure_current()
        logging.info(self.__class__.__name__ + ": Ramping current up from... %s to %s.", actual_current, _stop)
        while True:
            next_current = truncate_float(actual_current + _step, 4)
            logging.debug("actual current = %s, step = %s, next current = %s",
                          actual_current, _step, next_current)
            if next_current > _stop:
                self.set_current(_stop, _voltage_limit)
                break
            self.set_current(next_current, _voltage_limit)
            # we could have measured the current at the instrument output but is too slow
            # problem? We will not be aware if we will reach the limits
            actual_current = next_current
            time.sleep(_delay)
        logging.info(self.__class__.__name__ + ": Ramping current up DONE!")


if __name__ == "__main__":

    psu = TtiQL564P('COM6')
    psu.initialize()

    stopI = 2.0
    startI = 0.0
    stepI = 0.1
    stepUpDelay = 0.5
    stepDownDelay = 0.25
    voltage_limit = 4.0

    psu.measure_current()
    psu.measure_voltage()

    # while True:
    #     psu.current_ramp_up(startI, stopI, stepI, voltage_limit, stepUpDelay, True)
    #     time.sleep(5)
    #     psu.current_ramp_down(stepI, voltage_limit, stepDownDelay, False)
