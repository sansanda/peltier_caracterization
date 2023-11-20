# Script para verificar el buen funcionamiento del driver de la fuente de alimentacion
# TTi QL564P sn: 331871
import time

from serial_controllers import TtiQL1ChPsu
from tti_psus_testing.tti_psus import TtiQL564P

psu = TtiQL564P('COM8')

psu.initialize()

psu.set_output(1, voltage=1.2, current=0.1)

psu.enableOutput(1, True)
time.sleep(2)
psu.enableOutput(1, False)
