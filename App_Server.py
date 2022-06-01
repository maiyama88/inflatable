from __future__ import absolute_import, division, print_function, \
                                                    unicode_literals

import sys
import time
import datetime
import cmd
from gpiozero import LED
from struct import *
import server
import RPi.GPIO as GPIO

try:
    from ADCDACPi import ADCDACPi
except ImportError:
    print("Failed to import ADCDACPi from python system path")
    print("Importing from parent folder instead")
    try:
        import sys
        sys.path.append('..')
        from ADCDACPi import ADCDACPi
    except ImportError:
        raise ImportError(
            "Failed to import library from parent folder")

LED_PIN = 22
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN,0)
LED_PIN_ON = 0

tlm_time_start = int(time.time())
time_count = 0

print("IP Address: {0}".format(server.get_ip()))

adcdac = ADCDACPi(1)
adcdac.set_adc_refvoltage(3.3)

PRESSURE_LIMIT1 = 3.13
PRESSURE_LIMIT2 = 3.2

def my_hex(a):
    if a < 0x10 and a >= 0x00:
        tmp_str = hex(a)
        ret = "0" + tmp_str[2]
    else:
        tmp_str = hex(a)
        ret = tmp_str[2] + tmp_str[3]
    return  ret

if __name__ == '__main__':
        print("Start Application")
        ret = 0

        server.server_init()
        cmd.cmd_init()

        while True:
            server.server_loop()
            server_cmd = server.server_recv()
            if server_cmd != '':
                print("CMD:",server_cmd)
                ret = cmd.cmd_analyze(server_cmd,server)


            # PACKET SEND
            time_count += 1
            #if (time_count % 5000) == 0:
            if (time_count % 5000) == 0:
                # Pressure Check
                sensor_val1 = adcdac.read_adc_voltage(1, 0)
                sensor_val2 = adcdac.read_adc_voltage(2, 0)
                if sensor_val2 > PRESSURE_LIMIT1 and cmd.Mode == 2:
                    cmd.idle_mode()
                    #if sensor_val2 > PRESSURE_LIMIT2 :
                    #cmd.vent_mode()

                tlm_time = int(time.time()) - tlm_time_start

                mes_byte = bytearray(b'TM')
                tmp_bytes = pack(">i", tlm_time)
                mes_byte.append(tmp_bytes[3])
                tmp_bytes = pack(">i",cmd.cmd_count)
                mes_byte.append(tmp_bytes[3])
                tmp_bytes = pack(">i",cmd.cmd_code)
                mes_byte.append(tmp_bytes[3])

                # ADC IF
                sensor_val1_int = int(sensor_val1 * 1000)
                sensor_val2_int = int(sensor_val2 * 1000)
                tmp_bytes = pack(">i",sensor_val1_int)
                mes_byte.append(tmp_bytes[2])
                mes_byte.append(tmp_bytes[3])
                print("CH1:",sensor_val1, sensor_val1_int, hex(tmp_bytes[0]), hex(tmp_bytes[1]), hex(tmp_bytes[2]), hex(tmp_bytes[3]))
                tmp_bytes = pack(">i",sensor_val2_int)
                mes_byte.append(tmp_bytes[2])
                mes_byte.append(tmp_bytes[3])
                print("CH2:",sensor_val2, sensor_val2_int, hex(tmp_bytes[0]), hex(tmp_bytes[1]), hex(tmp_bytes[2]), hex(tmp_bytes[3]))

                tmp_bytes = pack(">i", cmd.Mode)
                mes_byte.append(tmp_bytes[3])

                mes_byte.extend(b'\r\n')
                server.server_send(mes_byte)

                mes = "TM {0:04X} ".format(tlm_time)
                for i in range(0,len(mes_byte)):
                    mes += my_hex(mes_byte[i])
                    mes += " "

                print(mes)

                if(LED_PIN_ON == 0):
                    GPIO.setup(LED_PIN, GPIO.OUT)
                    GPIO.output(LED_PIN,1)
                    LED_PIN_ON = 1
                else:
                    GPIO.setup(LED_PIN, GPIO.OUT)
                    GPIO.output(LED_PIN,0)
                    LED_PIN_ON = 0
