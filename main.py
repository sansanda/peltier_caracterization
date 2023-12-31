# This is a sample Python script.
# Press Mayús+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# Press the green button in the gutter to run the script.

import datetime
import time
from owon_psus_testing.owon_psus import OwonSPE6103
from center_309_testing.Center309 import Center309
from tti_psus_testing.tti_psus import TtiQL564P
from utils.lists_utils import list_range

import logging

FORMAT = '%(asctime)s:%(funcName)s:%(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO, datefmt='%m/%d/%Y %I:%M:%S %p')


def caracterize_single_peltier(psu: OwonSPE6103,
                               thermometer: Center309,
                               psu_voltage_limit,
                               p1_currents,
                               p1_step_up_current,
                               p1_step_up_with_ramp,
                               p1_step_up_delay,
                               p1_step_down_current,
                               p1_step_down_delay,
                               p1_reference,
                               t_amb,
                               output_data_file_name):
    # Experiment data#########################################
    experiment_date = datetime.datetime.now()
    peltier1_psu_model = psu.read_identity()
    thermometer_model = 'Center 309'  # thermometer.identify()
    ##########################################################

    # config file to write the test###########################
    index = 0
    separator = ","
    header = "Single Peltier Caracterization.\n"
    header += "Peltier1_applied currents: " + str(p1_currents) + "Amps.\n"
    header += "Experiment date: " + str(experiment_date) + "\n"
    header += "TAmb: " + str(t_amb) + " celsius.\n"
    header += "P1 reference: " + p1_reference + ".\n"
    header += "P1 PSU model: " + peltier1_psu_model + ".\n"
    header += "Thermometer model: " + thermometer_model + ".\n"
    subheader = "P1_I (Amps)" + separator + "P1_V (Volts)" + separator + "T1(ºC)" + "\n"
    ##########################################################

    # psu: OwonPSU
    psu.set_output(True)
    psu.set_voltage_limit(psu_voltage_limit)
    output_data_file_name = output_data_file_name + ".txt"

    # psu.current_ramp_down(p1_step_down_current,
    #                          0.0,
    #                          psu_voltage_limit,
    #                          p1_step_down_delay,
    #                          False)
    #

    with open(output_data_file_name, 'w') as file:

        file.writelines("*" * 30 + "\n")
        file.writelines(header)
        file.writelines("*" * 30 + "\n")
        file.writelines(subheader)

        for p1_c in p1_currents:
            if p1_step_up_with_ramp:
                current = psu.measure_current()
                # divider = int((abs(current-p1_step_up_current)/0.1)*5)
                # si fraccionamos en 5 un delta de 0,1. Para un delta dado fraccionaremos (delta/0.1)*5
                divider = 10
                psu.current_ramp_up(None, p1_c, p1_step_up_current / divider, psu_voltage_limit,
                                    1.0)
            else:
                psu.set_current(p1_c)
            logging.info("MAIN: WAITING FOR psu CURRENT STEP SEETING UP....")
            time.sleep(p1_step_up_delay)
            # time to read values
            logging.info("MAIN: MEASURING EXPERIMENT DATA....")
            p1_current, p1_voltage = psu.measure_current_voltage(1)
            p1_temp = thermometer.read_temperature(2)
            line = str(p1_current) + separator + str(p1_voltage) + separator + str(p1_temp) + "\n"
            logging.info("MAIN: WRITING TO FILE THE MEASURED EXPERIMENT DATA LINE  ....")
            logging.info("Line = %s", line)
            file.writelines(line)
        psu.current_ramp_down(p1_step_down_current,
                              0.0,
                              psu_voltage_limit,
                              p1_step_down_delay,
                              False)


def caracterize_double_stack_peltiers(p1_psu: TtiQL564P,
                                      p2_psu: OwonSPE6103,
                                      thermometer: Center309,
                                      p1_psu_voltage_limit,
                                      p2_psu_voltage_limit,
                                      p1_currents,
                                      p2_currents,
                                      p1_step_up_current,
                                      p2_step_up_current,
                                      p1_step_up_with_ramp,
                                      p2_step_up_with_ramp,
                                      p1_step_up_delay,
                                      p2_step_up_delay,
                                      p1_step_down_current,
                                      p2_step_down_current,
                                      p1_step_down_delay,
                                      p2_step_down_delay,
                                      p1_reference,
                                      p2_reference,
                                      t_amb,
                                      output_data_file_name):
    # Experiment data#########################################
    experiment_date = datetime.datetime.now()
    peltier1_psu_model = p1_psu.idn()
    peltier2_psu_model = p2_psu.read_identity()
    thermometer_model = 'Center 309'  # thermometer.identify()
    ##########################################################

    # config file to write the test###########################
    index = 0
    separator = ","
    header = "Stack2 Peltier caracterization.\n"
    header += "Peltier1_applied currents: " + str(p1_currents) + "Amps.\n"
    header += "Peltier2_applied currents: " + str(p2_currents) + "Amps.\n"
    header += "Peltier 1 is the closest to the heatsink.\n"
    header += "Experiment date: " + str(experiment_date) + "\n"
    header += "TAmb: " + str(t_amb) + " celsius.\n"
    header += "P1 reference: " + p1_reference + ".\n"
    header += "P2 reference: " + p2_reference + ".\n"
    header += "P1 PSU model: " + peltier1_psu_model + ".\n"
    header += "P2 PSU model: " + peltier2_psu_model + ".\n"
    header += "Thermometer model: " + thermometer_model + ".\n"
    subheader = "P1_I (Amps)" + separator + "P1_V (Volts)" \
                + separator + "P2_I (Amps)" + separator + "P2_V (Volts)" \
                + separator + "T1(ºC)" + separator + "T2(ºC)" + "\n"
    ##########################################################

    # p1_psu: TtiQL564P
    # p2_psu: OwonPSU
    p1_psu.enable_output(True)
    p2_psu.set_output(True)
    p2_psu.set_voltage_limit(p2_psu_voltage_limit)

    # p2_psu.current_ramp_down(p2_step_down_current,
    #                          0.0,
    #                          p2_psu_voltage_limit,
    #                          p2_step_down_delay,
    #                          False)
    #
    # p1_psu.current_ramp_down(p1_step_down_current,
    #                          0.0,
    #                          p1_psu_voltage_limit,
    #                          p1_step_down_delay,
    #                          False)

    for p1_c in p1_currents:
        output_data_file_name = output_data_file_name + "@p1_current=" + str(p1_c) + ".txt"
        with open(output_data_file_name, 'w') as file:
            file.writelines("*" * 30 + "\n")
            file.writelines(header)
            file.writelines("*" * 30 + "\n")
            file.writelines(subheader)
            if p1_step_up_with_ramp:
                p1_psu.current_ramp_up(None, p1_c, p1_step_up_current / 10, p1_psu_voltage_limit,
                                       1.0)
            else:
                p1_psu.set_current(p1_c, p1_psu_voltage_limit)
            logging.info("MAIN: WAITING FOR P1_PSU CURRENT STEP SEETING UP....")
            time.sleep(p1_step_up_delay)
            for p2_c in p2_currents:
                if p2_step_up_with_ramp:
                    p2_psu.current_ramp_up(None, p2_c, p2_step_up_current / 10,
                                           p2_psu_voltage_limit, 1.0)
                else:
                    p2_psu.set_current(p2_c)
                logging.info("MAIN: WAITING FOR P2_PSU CURRENT STEP SEETING UP....")
                time.sleep(p2_step_up_delay)
                # time to read values
                logging.info("MAIN: MEASURING EXPERIMENT DATA....")
                p1_current, p1_voltage = p1_psu.measure_current_voltage(2)
                p2_current, p2_voltage = p2_psu.measure_current_voltage(1)
                p1_temp = thermometer.read_temperature(1)
                p2_temp = thermometer.read_temperature(2)
                line = str(p1_current) + separator + str(p1_voltage) + separator + str(p2_current) \
                       + separator + str(p2_voltage) + separator + str(p1_temp) + separator \
                       + str(p2_temp) + "\n"
                logging.info("MAIN: WRITING TO FILE THE MEASURED EXPERIMENT DATA LINE  ....")
                logging.info("Line = %s", line)
                file.writelines(line)
            p2_psu.current_ramp_down(p2_step_down_current,
                                     0.0,
                                     p2_psu_voltage_limit,
                                     p2_step_down_delay,
                                     False)

    p1_psu.current_ramp_down(p1_step_down_current,
                             0.0,
                             p1_psu_voltage_limit,
                             p1_step_down_delay,
                             False)


def single_peltier(output_data_file_name):
    p2_psu_com_port = "COM5"
    thermometer_com_port = "COM4"

    p2_start_current = 0.0
    p2_stop_current = 8.0
    p2_step_up_current = 0.2
    p2_step_down_current = 0.05
    p2_step_up_delay = 60  # seconds 45
    p2_step_down_delay = 0.5  # seconds

    p2_currents = list_range(p2_start_current, p2_stop_current, p2_step_up_current)

    p2_reference = "UEPT-130-071-100M200"
    p2_max_voltage = 9.0
    p2_max_current = 10
    p2_psu_voltage_limit = p2_max_voltage  # Volts
    p2_psu_current_limit = p2_max_current  # Amps

    t_amb = 20  # celsius

    p2_psu = OwonSPE6103(p2_psu_com_port)
    p2_psu.open()
    time.sleep(2)
    # p2_psu.set_output(False)
    p2_psu.set_voltage_limit(p2_psu_voltage_limit)
    p2_psu.set_current_limit(p2_psu_current_limit)
    # p2_psu.set_current(0)
    p2_psu.set_voltage(p2_psu_voltage_limit)

    thermometer = Center309(thermometer_com_port, 9600, 1)

    caracterize_single_peltier(p2_psu,
                               thermometer,
                               p2_psu_voltage_limit,
                               p2_currents,
                               p2_step_up_current,
                               True,
                               p2_step_up_delay,
                               p2_step_down_current,
                               p2_step_down_delay,
                               p2_reference,
                               t_amb,
                               output_data_file_name)

    p2_psu.current_ramp_down(0.05, 0.0, 10, 0.25, False)


def double_stack_peltiers(output_data_file_name):
    p1_psu_com_port = "COM6"
    p2_psu_com_port = "COM5"
    thermometer_com_port = "COM4"

    p1_start_current = 2.6
    p1_stop_current = 3.6
    p1_step_up_current = 0.2
    p1_step_down_current = 0.05
    p1_step_up_delay = 20  # seconds 10
    p1_step_down_delay = 0.5  # seconds

    p2_start_current = 0.0
    p2_stop_current = 3.6
    p2_step_up_current = 0.2
    p2_step_down_current = 0.05
    p2_step_up_delay = 60  # seconds 45
    p2_step_down_delay = 0.5  # seconds

    p1_currents = list_range(p1_start_current, p1_stop_current, p1_step_up_current)
    p2_currents = list_range(p2_start_current, p2_stop_current, p2_step_up_current)

    p1_reference = "UEPT-130-071-100M200"
    p2_reference = "UEPT-130-071-100M200"
    p1_max_voltage = 8.5
    p2_max_voltage = 8.5
    p1_max_current = 10
    p2_max_current = 10

    p1_psu_range = 0  # 25V, 4A
    p1_psu_voltage_limit = p1_max_voltage  # Volts
    p1_psu_current_limit = p1_max_current  # Amps
    p2_psu_voltage_limit = p2_max_voltage  # Volts
    p2_psu_current_limit = p2_max_current  # Amps

    t_amb = 25  # celsius

    p1_psu = TtiQL564P(p1_psu_com_port)
    p1_psu.initialize()
    time.sleep(2)
    p1_psu.enable_output(False)
    p1_psu.set_output(p1_psu_voltage_limit, 0.0)
    p1_psu.set_range(p1_psu_range)
    p1_psu.set_over_current_protection(p1_psu_current_limit)

    p2_psu = OwonSPE6103(p2_psu_com_port)
    p2_psu.open()
    time.sleep(2)
    p2_psu.set_output(False)
    p2_psu.set_voltage_limit(p2_psu_voltage_limit)
    p2_psu.set_current_limit(p2_psu_current_limit)
    p2_psu.set_current(0)
    p2_psu.set_voltage(p2_psu_voltage_limit)

    thermometer = Center309(thermometer_com_port, 9600, 1)

    caracterize_double_stack_peltiers(p1_psu,
                                      p2_psu,
                                      thermometer,
                                      p1_psu_voltage_limit,
                                      p2_psu_voltage_limit,
                                      p1_currents,
                                      p2_currents,
                                      p1_step_up_current,
                                      p2_step_up_current,
                                      True,
                                      True,
                                      p1_step_up_delay,
                                      p2_step_up_delay,
                                      p1_step_down_current,
                                      p2_step_down_current,
                                      p1_step_down_delay,
                                      p2_step_down_delay,
                                      p1_reference,
                                      p2_reference,
                                      t_amb,
                                      output_data_file_name)

    p2_psu.current_ramp_down(0.05, 0.0, 10, 0.25, False)
    p1_psu.current_ramp_down(0.05, 0.0, 10, 0.25, False)


if __name__ == '__main__':
    # output_data_file_name = "peltier_test_p1_p2"
    # double_stack_peltiers(output_data_file_name)
    output_data_file_name = "peltier_test6_p1"
    single_peltier(output_data_file_name)
