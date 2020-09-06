import asyncio
import os
import signal
import sys
import time

import numpy as np
from tapsdk import TapInputMode, TapSDK

from drone import MyTello
from raw_gestures import insert_accelerometer_data
from raw_gestures import state as hand_state


def abort_handler(sig=None, frame=None):
    print('Aborting...')
    [goto_landing() for i in range(5)]
    sys.exit(0)
signal.signal(signal.SIGINT, abort_handler)


my_drone = MyTello(tello_ip="127.0.0.1", debug=False)
# my_drone = MyTello(debug=False)
strap_heart_beat = 0
dry_run = True


def OnRawData(identifier, packets):
    global strap_heart_beat
    for m in packets:
        if m["type"] == "imu":
            pass
        if m["type"] == "accl":
            insert_accelerometer_data(m["payload"])
            strap_heart_beat = time.time()
            

def takeoff_finished():
    if 0 < my_drone.get_stat_height() < 80 and not dry_run:
        return False
    return True

def landing_finished():
    if my_drone.get_stat_height() > 10 and not dry_run:
        return False
    return True

def do_joystick_cmd(a=None, b=None, c=None, d=None):
    # a = right/left
    # b = fwd/bwd
    # c = up/down
    # d = yaw r/l
    if a is None and b is None and c is None and d is None:
        a = 0
        b = 0
        c = 0
        d = 0
        if hand_state["thumb_palm_parallel"] == True:
            a = hand_state["joystick"][1]
            b = hand_state["joystick"][0]
        else:
            c = hand_state["joystick"][0]
            d = hand_state["joystick"][1]

    clip_value = 30
    values = [a,b,c,d]
    for i,v in enumerate(values):
        values[i] = max(-clip_value,min(clip_value,v))
    a,b,c,d = values
    if not dry_run:
        my_drone.rc_control(a,b,c,d)
    print("sent command: rc ", a, b, c, d)


drone_state = "off"


def goto_landing():
    global drone_state
    drone_state = "landing"
    if not dry_run:
        my_drone.land()
    print("sent command: land")


def goto_takeoff():
    global drone_state
    drone_state = "takeoff"
    if not dry_run:
        my_drone.takeoff()
    print("sent command: takeoff")

def goto_idle():
    global drone_state
    drone_state = "idle"
    do_joystick_cmd(0,0,0,0)

def goto_off():
    global drone_state
    drone_state = "off"
    do_joystick_cmd(0,0,0,0)



def state_machine():
    global drone_state
    if drone_state == "off":
        if hand_state["palm_state"] == "fwd":
            goto_takeoff()
    elif drone_state == "takeoff":
        if takeoff_finished():
            goto_idle()
    elif drone_state == "idle":
        if hand_state["palm_state"] == "down":
            do_joystick_cmd()
    elif drone_state == "landing":
        if landing_finished():
            goto_off()

    if hand_state["palm_state"] == "bwd":
        goto_landing()
    
    if drone_state != "off" and strap_heart_beat + 2 < time.time():
        print("Missing Tap heart beat")
        goto_landing()

async def systick():
    while True:
        print(hand_state["palm_state"])
        print(hand_state["thumb_palm_parallel"])
        print(my_drone.stats)
        print(drone_state)
        state_machine()
        await asyncio.sleep(0.5)
systick.task = []

def stop_systick():
    systick.task.cancel()

    
async def drone_stats_loop():
    while True:
        my_drone.read_stats()
        await asyncio.sleep(0.2)
drone_stats_loop.task = []

def stop_drone_stats_loop():
    drone_stats_loop.task.cancel()


def wrap_up():
    stop_systick()
    stop_drone_stats_loop()


async def run(loop):  
    client = TapSDK(loop)
    x = await client.manager.connect_retrieved()

    await client.register_raw_data_events(OnRawData)
    await client.set_input_mode(TapInputMode("raw", sensitivity=[2,2,2]))

    await asyncio.sleep(500.0, loop=loop)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    systick.task = loop.create_task(systick())
    drone_stats_loop.task = loop.create_task(drone_stats_loop())
    loop.run_until_complete(run(loop))
