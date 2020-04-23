from tapsdk.backends.macos.TapSDK import TapMacSDK as TapSDK
from tapsdk.backends.macos.inputmodes import TapInputMode
from tapsdk.models import AirGestures

import os
os.environ["PYTHONASYNCIODEBUG"] = str(1)
import asyncio
import platform
import logging
from bleak import _logger as logger

import time
import numpy as np

from raw_gestures import insert_accelerometer_data
from raw_gestures import state as hand_state

from drone import MyTello

my_drone = MyTello(tello_ip="127.0.0.1", debug=False)


def notification_handler(sender, data):
    """Simple notification handler which prints the data received."""
    print("{0}: {1}".format(sender, data))


def OnMouseModeChange(identifier, mouse_mode):
    print(identifier + " changed to mode " + str(mouse_mode))


def OnTapped(identifier, tapcode):
    print(identifier + " tapped " + str(tapcode))


def OnGesture(identifier, gesture):
    print(identifier + " gesture " + str(AirGestures(gesture)))

def OnRawData(identifier, packets):
    for m in packets:
        if m["type"] == "imu":
            pass
        if m["type"] == "accl":
            insert_accelerometer_data(m["payload"])


async def systick():
    while True:
        print(hand_state)
        print(my_drone.stats)
        await asyncio.sleep(1)
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

async def run(loop, debug=False):
    if debug:
        import sys

        # loop.set_debug(True)
        l = logging.getLogger("asyncio")
        l.setLevel(logging.DEBUG)
        h = logging.StreamHandler(sys.stdout)
        h.setLevel(logging.INFO)
        l.addHandler(h)
        logger.addHandler(h)
    
    client = TapSDK(loop)
    x = await client.manager.connect_retrieved()
    x = await client.manager.is_connected()
    logger.info("Connected: {0}".format(x))


    # await client.register_air_gesture_events(OnGesture)
    # await client.register_tap_events(OnTapped)
    # await client.register_air_gesture_state_events(OnMouseModeChange)

    await client.register_raw_data_events(OnRawData)
    await client.set_input_mode(TapInputMode("raw", sensitivity=[2,2,2]))
    # await client.set_input_mode(TapInputMode("controller"))

    await asyncio.sleep(500.0, loop=loop)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    systick.task = loop.create_task(systick())
    drone_stats_loop.task = loop.create_task(drone_stats_loop())
    # loop.call_later(5, stop_periodic)
    loop.run_until_complete(run(loop, True))

