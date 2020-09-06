import asyncio
import os
import time

import numpy as np

from drone import MyTello
from raw_gestures import insert_accelerometer_data
from raw_gestures import state as hand_state
from tapsdk import TapInputMode, TapSDK

# my_drone = MyTello(tello_ip="127.0.0.1", debug=False)
my_drone = MyTello(debug=False)
strap_heart_beat = 0


def OnRawData(identifier, packets):
    global strap_heart_beat
    for m in packets:
        if m["type"] == "imu":
            pass
        if m["type"] == "accl":
            insert_accelerometer_data(m["payload"])
            strap_heart_beat = time.time()
            

def takeoff_finished():
    # if height > 0.8:
    #     return True
    # return False
    return True

def landing_finished():
    # if height < 0.1:
    #     return True
    # else:
    #     return False
    return True

def do_joystick_cmd():
    a = 0 # right/left
    b = 0 # fwd/bwd
    c = 0 # up/down
    d = 0 # yaw r/l

    if hand_state["thumb_palm_parallel"] == True:
        a = hand_state["joystick"][1]
        b = hand_state["joystick"][0]
    else:
        c = hand_state["joystick"][0]
        d = hand_state["joystick"][1]
    print("RC:", a, b, c, d)
    # my_drone.rc_control(a,b,c,d)


drone_state = "off"


def goto_landing():
    global drone_state
    drone_state = "landing"
    # my_drone.land()


def goto_takeoff():
    global drone_state
    drone_state = "takeoff"
    # my_drone.takeoff()



def state_machine():
    global drone_state
    if drone_state == "off":
        if hand_state["palm_state"] == "fwd":
            goto_takeoff()
    elif drone_state == "takeoff":
        if takeoff_finished():
            drone_state = "idle"
    elif drone_state == "idle":
        if hand_state["palm_state"] == "down":
            do_joystick_cmd()
    elif drone_state == "landing":
        if landing_finished():
            drone_state = "off"

    if hand_state["palm_state"] == "bwd":
        goto_landing()
    
    if drone_state != "off" and strap_heart_beat + 2 < time.time():
        goto_landing()

async def systick():
    while True:
        # print(hand_state["palm_state"])
        # print(hand_state["thumb_palm_parallel"])een
        print(my_drone.stats)
        print(drone_state)
        state_machine()
        await asyncio.sleep(0.1)
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
    # loop.call_later(5, stop_periodic)
    loop.run_until_complete(run(loop))
