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




def notification_handler(sender, data):
    """Simple notification handler which prints the data received."""
    print("{0}: {1}".format(sender, data))


def OnMouseModeChange(identifier, mouse_mode):
    print(identifier + " changed to mode " + str(mouse_mode))


def OnTapped(identifier, tapcode):
    print(identifier + " tapped " + str(tapcode))


def OnGesture(identifier, gesture):
    print(identifier + " gesture " + str(AirGestures(gesture)))


def OnTapConnected(self, identifier, name, fw):
    print(identifier + " Tap: " + str(name), " FW Version: ", fw)


def OnTapDisconnected(self, identifier):
    print(identifier + " Tap: " + identifier + " disconnected")


def OnMoused(identifier, vx, vy, isMouse):
    print(identifier + " mouse movement: %d, %d, %d" %(vx, vy, isMouse))


def OnRawData(identifier, packets):
    # imu_msg = [m for m in packets if m["type"] == "imu"][0]
    # if len(imu_msg) > 0:
    #     OnRawData.cnt += 1
    #     if OnRawData.cnt == 10:
    #         OnRawData.cnt = 0
    #         logger.info(identifier + " raw imu : " + str(imu_msg["ts"]))

    for m in packets:
        if m["type"] == "imu":
            # print("imu")
            OnRawData.imu_cnt += 1
            if OnRawData.imu_cnt == 208:
                OnRawData.imu_cnt = 0
                # print("imu, " + str(time.time()) + ", " + str(m["payload"]))
        if m["type"] == "accl":
            # print("accl")
            insert_accelerometer_data(m["payload"])
            OnRawData.accl_cnt += 1
            accl = np.asanyarray(m["payload"])
            if OnRawData.accl_cnt == 20:
                OnRawData.accl_cnt = 0
                # diff = (accl - OnRawData.prev_accl)[3:].reshape(-1,3).mean(axis=0)
                # if np.abs(diff[2]) > 20:
                #     print(diff)
                # print((OnRawData.prev_accl[3:]).reshape(-1,3).mean(axis=0))
                # OnRawData.prev_accl = accl.copy()
OnRawData.imu_cnt = 0
OnRawData.accl_cnt = 0
OnRawData.cnt = 0



async def periodic():
    while True:
        print(hand_state)
        await asyncio.sleep(0.1)
periodic.task = []

def stop_periodic():
    periodic.task.cancel()

def wrap_up():
    stop_periodic()

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
    periodic.task = loop.create_task(periodic())
    # loop.call_later(5, stop_periodic)
    loop.run_until_complete(run(loop, True))

