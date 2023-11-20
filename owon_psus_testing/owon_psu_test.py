# Script para verificar el buen funcionamiento del driver de la fuente de alimentacion
# Owon SPE6103 con sn: SPE610322380172
import time

from owon_psu import OwonPSU

with OwonPSU("COM9") as opsu:
    print("Identity:", opsu.read_identity())
    print("Measured Voltage:", opsu.measure_voltage())
    print("Measured Current:", opsu.measure_current())

    print("Set Voltage:", opsu.get_voltage())
    print("Set Current:", opsu.get_current())

    print("Set Voltage Limit:", opsu.get_voltage_limit())
    print("Set Current Limit:", opsu.get_current_limit())

    # opsu.set_voltage(0)
    # opsu.set_current(0)
    # opsu.set_voltage_limit(30)
    # opsu.set_current_limit(3)

    opsu.set_voltage_limit(4)
    opsu.set_current_limit(4)
    time.sleep(2)
    opsu.set_current(0)
    opsu.set_voltage(0)

    print("Output enabled:", opsu.get_output())
    opsu.set_output(True)

    maxI = 1
    actualI = 0
    stepI = 0.1
    while True:
        opsu.set_current(actualI)
        actualI = actualI + stepI
        time.sleep(0.2)
        if actualI > maxI:
            break


