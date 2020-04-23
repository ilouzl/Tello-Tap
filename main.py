import asyncio
import os

import numpy as np

from drone import MyTello
from raw_gestures import insert_accelerometer_data
from raw_gestures import state as hand_state
from tapsdk import TapInputMode, TapSDK

my_drone = MyTello(tello_ip="127.0.0.1", debug=False)


def OnRawData(identifier, packets):
    for m in packets:
        if m["type"] == "imu":
            pass
        if m["type"] == "accl":
            insert_accelerometer_data(m["payload"])

def drone_is_idle():
    return False

drone_state = "off"

def state_machine():
    global drone_state
    if drone_state == "off":
        if hand_state["palm_state"] == "fwd":
            print("Liftoff")
            drone_state = "liftoff"
    elif drone_state == "liftoff":
        drone_state = "idle"
    elif drone_state == "idle":
        if hand_state["palm_state"] == "down":
            print("Joynstic cmd")

    if hand_state["palm_state"] == "bwd":
        print("Land")
        drone_state = "land"
    if drone_is_idle():
        drone_state = "idle"

async def systick():
    while True:
        print(hand_state["palm_state"])
        # print(my_drone.stats)
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
