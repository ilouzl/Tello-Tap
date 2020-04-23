import numpy as np
from collections import deque

FS = 200.0
TS = 1.0/FS
LSB2G = 128.0

previous_accl = np.zeros(15)

accl_q = deque(maxlen=int(1*FS))

state = {
    "joystick":(0,0),
    "palm_state":"down",
    "thumb_state":"down"
    }


def joystick_emulation(accl):
    m = accl[-int(FS*0.3):].mean(axis=0)[3:].reshape(-1,3).mean(axis=0)

    phi = np.rad2deg(np.arctan2(m[1],np.sqrt(m[0]**2 + m[2]**2)))
    theta = np.rad2deg(np.arctan2(m[0],np.sqrt(m[1]**2 + m[2]**2)))

    state["joystick"] = (10*int(phi*10/90),10*int(theta*10/90))


def palm_state(accl):
    m = accl.mean(axis=0)[3:].reshape(-1,3).mean(axis=0)
    n_m = np.linalg.norm(m)
    if LSB2G*1.2 > n_m > LSB2G*0.8:
        m_norm = m/n_m
        if m[0] > LSB2G*0.85:
            state["palm_state"] = "fwd"
        elif m[0] < -LSB2G*0.85:
            state["palm_state"] = "bwd"
        if m[1] > LSB2G*0.85:
            state["palm_state"] = "left"
        elif m[1] < -LSB2G*0.85:
            state["palm_state"] = "right"
        if m[2] > LSB2G*0.85:
            state["palm_state"] = "down"
        elif m[2] < -LSB2G*0.85:
            state["palm_state"] = "up"


def thumb_state(accl):
    m = accl.mean(axis=0)[:3]
    n_m = np.linalg.norm(m)
    if LSB2G*1.2 > n_m > LSB2G*0.8:
        m_norm = m/n_m
        if m[0] > LSB2G*0.7:
            state["thumb_state"] = "fwd"
        elif m[0] < -LSB2G*0.85:
            state["thumb_state"] = "bwd"
        if m[1] > LSB2G*0.85:
            state["thumb_state"] = "left"
        elif m[1] < -LSB2G*0.85:
            state["thumb_state"] = "right"
        if m[2] > LSB2G*0.85:
            state["thumb_state"] = "down"
        elif m[2] < -LSB2G*0.85:
            state["thumb_state"] = "up"
        


def insert_accelerometer_data(accl):
    accl_q.append(accl)
    a = np.array(accl_q)
    joystick_emulation(a)
    palm_state(a)
    thumb_state(a)

