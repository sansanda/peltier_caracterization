import time

from center_309_testing.Center309 import Center309

thermometer = Center309("COM6", 9600, 1)
print(thermometer.identify())
counter = 0
max_counter = 25
while True:
    print(thermometer.read_temperature(1))
    time.sleep(0.2)
    counter = counter + 1
    if counter > max_counter:
        break