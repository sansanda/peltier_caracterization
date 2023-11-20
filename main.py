# This is a sample Python script.

# Press Mayús+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# Press the green button in the gutter to run the script.
import datetime
import time

from owon_psu import OwonPSU

from owon_psus_testing.owon_psus import OwonSPE6103
from serial_controllers import TtiQL1ChPsu
from center_309_testing.Center309 import Center309
from tti_psus_testing.tti_psus import TtiQL564P


def list_range(start, stop, step_value):
    l = []
    if start >= stop:
        l.append(round(start, 2))
        return l
    while True:
        if len(l) == 0:
            l.append(round(start, 2))
        l.append(round(l[-1] + step_value, 2))
        if l[-1] >= stop:
            break
    return l


def caracterize_peltier(p1_psu: TtiQL564P,
                        p2_psu: OwonSPE6103,
                        thermometer: Center309,
                        p1_psu_voltage_limit,
                        p2_psu_voltage_limit,
                        p1_currents,
                        p2_currents,
                        p1_step_up_delay,
                        p2_step_up_delay,
                        p1_step_down_current,
                        p2_step_down_current,
                        p1_step_down_delay,
                        p2_step_down_delay,
                        p1_reference,
                        p2_reference,
                        t_amb):
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
    p1_psu.enableOutput(True)
    p2_psu.set_output(True)
    p2_psu.set_voltage_limit(p2_psu_voltage_limit)

    for p1_c in p1_currents:
        output_data_file_name = "peltier_test_p1@current=" + str(p1_c)
        with open(output_data_file_name, 'w') as file:
            file.writelines("*" * 30 + "\n")
            file.writelines(header)
            file.writelines("*" * 30 + "\n")
            file.writelines(subheader)
            p1_psu.set_output(p1_psu_voltage_limit, p1_c)
            time.sleep(p1_step_up_delay)
            for p2_c in p2_currents:
                p2_psu.set_current(p2_c)
                time.sleep(p2_step_up_delay)
                # time to read values
                p1_voltage = p1_psu.measure_voltage()
                p1_current = p1_psu.measure_current()
                p2_voltage = p2_psu.measure_voltage()
                p2_current = p2_psu.measure_current()
                p1_temp = thermometer.read_temperature(1)
                p2_temp = thermometer.read_temperature(2)
                line = str(p1_current) + separator + str(p1_voltage) + separator + str(p2_current) \
                       + separator + str(p2_voltage) + separator + str(p1_temp) + separator \
                       + str(p2_temp) + "\n"
                print(line)
                file.writelines(line)
            p2_psu.current_ramp_down(p2_step_down_current,
                                     p2_step_down_delay,
                                     p2_psu_voltage_limit,
                                     False)

    p1_psu.current_ramp_down(p1_step_down_current,
                             p1_step_down_delay,
                             p1_psu_voltage_limit,
                             False)


    # k2400.write(":OUTPut ON")
    # # Adjust voltage at gate##################################
    # adjust_voltage_at_dut_gate(k2400, daq6510, 101, 35)
    # ##########################################################
    # # Configure graph#########################################
    # plt.autoscale(enable=True, axis='y')
    # plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    # plt.title("Mosfet leakage test over time")
    # plt.ylabel("Leakage Current in Amps")
    # plt.xlabel("Seconds")
    # ##########################################################
    # # MEASURE LOOP############################################
    # n_measure = 1
    # while True:
    #     separator = ","
    #     sleep(delay_between_measure_series)
    #     for index, voltmeter_channel in enumerate(voltmeter_channels):
    #         voltmeter_channel_str = '(@' + str(voltmeter_channel) + ')'
    #         sleep(delay_between_measure_devices)
    #         daq6510.write(':ROUTe:CHANnel:CLOSe ' + voltmeter_channel_str)
    #         sleep(delay_after_close_channel)
    #         voltage_at_shunt = float(daq6510.query("READ?"))  # read measurement
    #         current_at_shunt = voltage_at_shunt / r_shunts[index]
    #         with open(output_data_file_name, 'a') as file:
    #             if index == 0:
    #                 file.writelines(str(n_measure) + separator)
    #             if index == (len(voltmeter_channels) - 1):
    #                 separator = "\n"
    #             file.writelines(str(current_at_shunt) + separator)
    #         current_at_shunts_evolution[index].append(current_at_shunt)
    #         sleep(delay_between_measure_devices)
    #         # daq6510.write(':ROUTe:CHANnel:OPEN ' + voltmeter_channel_str)
    #     n_measure_series.append(n_measure)
    #     n_measure = n_measure + 1
    #
    #     # Update graph########################################
    #     for i_color, currents in enumerate(current_at_shunts_evolution):
    #         plt.plot(n_measure_series, currents, color=plot_colors[i_color])
    #     plt.show(block=False)
    #     plt.pause(0.1)
    #     ######################################################
    # ##########################################################


if __name__ == '__main__':
    import numpy as np

    p1_start_current = 0.0
    p1_stop_current = 3.6
    p1_step_up_current = 0.2
    p1_step_down_current = 0.05

    p2_start_current = 0.0
    p2_stop_current = 0.4
    p2_step_up_current = 0.2
    p2_step_down_current = 0.05

    p1_currents = list_range(p1_start_current, p1_stop_current, p1_step_up_current)
    p2_currents = list_range(p2_start_current, p2_stop_current, p2_step_up_current)

    p1_psu_range = 0  # 25V, 4A
    p1_psu_voltage_limit = 4  # Volts
    p1_psu_current_limit = 4  # Amps
    p2_psu_voltage_limit = 4  # Volts
    p2_psu_current_limit = 4  # Amps

    p1_step_up_delay = 1  # seconds
    p2_step_up_delay = 1  # seconds
    p1_step_down_delay = 0.5  # seconds
    p2_step_down_delay = 0.5  # seconds
    p1_reference = "UEPT-130-071-100M200"
    p2_reference = "UEPT-130-071-100M200"
    t_amb = 25  # celsius

    p1_psu = TtiQL564P('COM8')
    p1_psu.initialize()
    p1_psu.enableOutput(False)
    p1_psu.set_output(p1_psu_voltage_limit, 0.0)
    p1_psu.set_range(p1_psu_range)
    p1_psu.set_over_current_protection(p1_psu_current_limit)

    p2_psu = OwonSPE6103('COM9')
    p2_psu.open()
    p2_psu.set_output(False)
    p2_psu.set_voltage_limit(p2_psu_voltage_limit)
    p2_psu.set_current_limit(p2_psu_current_limit)
    p2_psu.set_current(0)
    p2_psu.set_voltage(p2_psu_voltage_limit)

    thermometer = Center309("COM6", 9600, 1)

    caracterize_peltier(p1_psu, p2_psu, thermometer, p1_psu_voltage_limit, p2_psu_voltage_limit,
                        p1_currents, p2_currents, p1_step_up_delay, p2_step_up_delay,
                        p1_step_down_current, p2_step_down_current, p1_step_down_delay,
                        p2_step_down_delay, p1_reference, p2_reference, t_amb)

    p2_psu.current_ramp_down(0.05, 5, 10, False)
    p1_psu.current_ramp_down(0.05, 5, 10, False)
