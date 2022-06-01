import time
import datetime
import re
import shutil
import os
import RPi.GPIO as valve_swtch

cmd_sts = 0
cmd_count = 0
cmd_code = 0
cmd_code_tmp = 0
cmd_param = ""

VALVE1_PORT = 24
VALVE2_PORT = 23
VALVE3_PORT = 17
VALVE4_PORT = 18
valve_swtch.setmode(valve_swtch.BCM)
valve_swtch.setwarnings(False)
valve_swtch.setup(VALVE1_PORT, valve_swtch.OUT)
valve_swtch.setup(VALVE2_PORT, valve_swtch.OUT)
valve_swtch.setup(VALVE3_PORT, valve_swtch.OUT)
valve_swtch.setup(VALVE4_PORT, valve_swtch.OUT)
valve1_val = 0
valve2_val = 0
valve3_val = 0
valve4_val = 0
Mode = 0

def cmd_init():
    idle_mode()

def cmd_analyze(cmd, server):
    global cmd_sts
    global cmd_count
    global cmd_code_tmp
    global cmd_param

    ret = 0

    for i in range(len(cmd)):
        c = cmd[i]
        if cmd_sts == 0:
            if c == ord('c'):
                    cmd_sts = 1
            else:
                    cmd_sts = 0
        elif cmd_sts == 1:
            if c == ord('m'):
                    cmd_sts = 2
            else:
                    cmd_sts = 0
        elif cmd_sts == 2:
            cmd_code_tmp = c
            cmd_param = ""
            cmd_sts = 3
        elif cmd_sts == 3:
            cmd_param += chr(c)
            if(c == 0x0a):
                ret = cmd_action(server)
                cmd_sts = 0
    return ret

def cmd_action(server):
    global cmd_count
    global cmd_code
    global cmd_code_tmp
    global cmd_param
    global valve1_val
    global valve2_val
    global valve3_val
    global valve4_val

    ret = 0
    cmd_count += 1
    if cmd_code_tmp == ord('1'):    ##  Relay1l
        s = re.findall(r'\b\d+\b', cmd_param)
        if (len(s) < 1):
            print("Valve1 Parameter Error",cmd_param)
            return 0
        if(int(s[0]) == 1):
            valve1_val = 1
            valve_swtch.output(VALVE1_PORT,1)
        else:
            valve1_val = 0
            valve_swtch.output(VALVE1_PORT,0)
        print("Valve1 Cmd", valve1_val)
    elif cmd_code_tmp == ord('2'):    ##  Relay2
        s = re.findall(r'\b\d+\b', cmd_param)
        if (len(s) < 1):
            print("Valve2 Parameter Error",cmd_param)
            return 0
        if(int(s[0]) == 1):
            valve2_val = 1
            valve_swtch.output(VALVE2_PORT,1)
        else:
            valve2_val = 0
            valve_swtch.output(VALVE2_PORT,0)
        print("Valve2 Cmd", valve2_val)
    elif cmd_code_tmp == ord('3'):    ##  Relay3
        s = re.findall(r'\b\d+\b', cmd_param)
        if (len(s) < 1):
            print("Valve3 Parameter Error",cmd_param)
            return 0
        if(int(s[0]) == 1):
            valve3_val = 1
            valve_swtch.output(VALVE3_PORT,1)
        else:
            valve3_val = 0
            valve_swtch.output(VALVE3_PORT,0)
        print("Valve3 Cmd", valve3_val)
    elif cmd_code_tmp == ord('4'):    ##  Relay4
        s = re.findall(r'\b\d+\b', cmd_param)
        if (len(s) < 1):
            print("Valve3 Parameter Error",cmd_param)
            return 0
        if(int(s[0]) == 1):
            valve4_val = 1
            valve_swtch.output(VALVE4_PORT,1)
        else:
            valve4_val = 0
            valve_swtch.output(VALVE4_PORT,0)
        print("Valve3 Cmd", valve4_val)
    elif cmd_code_tmp == ord('0'):    ##  Idle Mode
        idle_mode()
        print("Idle Cmd")
    elif cmd_code_tmp == ord('V'):    ##  Idle Mode
        vent_mode()
        print("Vent Cmd")
    elif cmd_code_tmp == ord('I'):    ##  Idle Mode
        inf_mode()
        print("Vent Cmd")
    else:
        print("NA Cmd")

    return ret


def idle_mode():
    global valve1_val
    global valve2_val
    global valve3_val
    global valve4_val
    global Mode
    valve_swtch.output(VALVE1_PORT,0)
    valve_swtch.output(VALVE2_PORT,0)
    valve_swtch.output(VALVE3_PORT,0)
    valve_swtch.output(VALVE4_PORT,0)
    time.sleep(0.1)
    valve_swtch.output(VALVE4_PORT,1)
    time.sleep(0.1)
    valve_swtch.output(VALVE4_PORT,0)
    valve1_val = 0
    valve2_val = 0
    valve3_val = 0
    valve4_val = 0
    Mode = 0

def vent_mode():
    global valve1_val
    global valve2_val
    global valve3_val
    global valve4_val
    global Mode
    valve_swtch.output(VALVE1_PORT,0)
    valve_swtch.output(VALVE2_PORT,1)
    valve_swtch.output(VALVE3_PORT,0)
    valve_swtch.output(VALVE4_PORT,0)
    time.sleep(0.1)
    valve_swtch.output(VALVE3_PORT,1)
    time.sleep(0.1)
    valve_swtch.output(VALVE3_PORT,0)
    valve1_val = 0
    valve2_val = 1
    valve3_val = 1
    valve4_val = 0
    Mode = 1

def inf_mode():
    global valve1_val
    global valve2_val
    global valve3_val
    global valve4_val
    global Mode
    valve_swtch.output(VALVE1_PORT,1)
    valve_swtch.output(VALVE2_PORT,0)
    valve_swtch.output(VALVE3_PORT,0)
    valve_swtch.output(VALVE4_PORT,0)
    time.sleep(0.1)
    valve_swtch.output(VALVE4_PORT,1)
    time.sleep(0.1)
    valve_swtch.output(VALVE4_PORT,0)
    valve1_val = 1
    valve2_val = 0
    valve3_val = 0
    valve4_val = 0
    Mode = 2
