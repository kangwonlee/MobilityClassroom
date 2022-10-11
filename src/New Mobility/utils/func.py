import numpy as np
import math
import time
import cv2
import os
import configparser

# Perception
from Percep.Det import Lane, StopLine
from Percep.Camera import Camera

# Planning Control
from Plan.Planning import Error
from Plan.Controller import Controller

# Pwm
from Motor.motor import Motor

# utils
from utils.params import Car, Info
import utils.params as params
from utils.keyPoller import KeyPoller


from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt


def rgb_message():
    print("\n\n\n")
    print("###################################")
    print("press 'r' for capture red img and get red's rgb range \n")
    print("press 'g' for capture green img and get red's rgb range \n")
    print("press 'b' for capture blue img and get red's rgb range \n")
    print("press 's' for saving rgb range to .txt file \n")
    print("press 'e' for end \n")
    print("###################################")


def help_message():
    print("\n\n\n")
    print("###################################")
    print("Press 'h', if you want to check which functions you can use \n")
    print("Press 'c', capture! \n")
    print("Press 'r', if your camera doesn't work or apply new rbg range \n")
    print("Press 's', make RC car Start. recommend do it after calibrating rgb range, and checking your camera \n")
    print("Press 'e', Stop RC car \n")
    print("Press 'q' if you want to quit this program \n")
    print("###################################")


def read_rgb_range(filepath="./resource/rgb_range_init.txt"):
    config = configparser.ConfigParser()
    config.read(filepath)
    rgb_range = config["range"]

    r1 = rgb_range.get("r1", "235 100 110").split(' ')
    r1 = [int(s) for s in r1]
    r2 = rgb_range.get("r2", "255 180 255").split(' ')
    r2 = [int(i) for i in r2]

    g1 = rgb_range.get("g1", "0 200 180").split(' ')
    g1 = [int(i) for i in g1]
    g2 = rgb_range.get("g2", "100 255 255").split(' ')
    g2 = [int(i) for i in g2]

    b1 = rgb_range.get("b1", "0 140 230").split(' ')
    b1 = [int(i) for i in b1]
    b2 = rgb_range.get("b2", "100 200 255").split(' ')
    b2 = [int(i) for i in b2]

    show_range(r1, r2, g1, g2, b1, b2)

    return r1, r2, g1, g2, b1, b2

def show_range(r1, r2, g1, g2, b1, b2):
    print('\n\n\n')
    print("#" * 60)
    print("red_lower: ", r1, '\n')
    print("red_upper: ", r2, '\n')
    print("green_lower: ", g1, '\n')
    print("green_upper: ", g2, '\n')
    print("blue_lower: ", b1, '\n')
    print("blue_upper: ", b2, '\n')
    print("#" * 60)


def read_cfg(filepath = os.path.join(".", "resource", "gain_init.txt")):
    config = configparser.ConfigParser()
    config.read(filepath)
    param = config["parameter"]
    ky  = float(param.get("ky", 1.0))
    ka  = float(param.get("ka", 1.0))
    kcv = float(param.get("kcv", 1.0))
    kcl = float(param.get("kcl", 1.0))
    Vmax = float(param.get("Vmax", 1.0))
    Aymax = float(param.get("Aymax", 1.0))

    show_params(ky, ka, kcv, kcl, Vmax, Aymax)

    return ky, ka, kcv, kcl, Vmax, Aymax


def show_params(ky, ka, kcv, kcl, Vmax, Aymax):
    print('\n\n\n')
    print("#" * 60)
    print("ky: ", ky, '\n')
    print("ka: ", ka, '\n')
    print("kcv: ", kcv, '\n')
    print("kcl: ", kcl, '\n')
    print("Vmax: ", Vmax, '\n')
    print("Aymax: ", Aymax, '\n')
    print("#" * 60)

def init(ismotor, left_lower=(0, 200, 180), left_upper=(100, 255, 255),
         right_lower=(235, 100, 110), right_upper=(255, 180, 255), lower_rgb=(0, 140, 230), upper_rgb=(100, 200, 255)):
    ky, ka, kcv, kcl, Vmax, Aymax = read_cfg(filepath = '/resource/gain.txt')

    try:
        left_lower = np.array(left_lower, dtype=np.uint8)
        left_upper = np.array(left_upper, dtype=np.uint8)
        right_lower = np.array(right_lower, dtype=np.uint8)
        right_upper = np.array(right_upper, dtype=np.uint8)
        lower_rgb = np.array(lower_rgb, dtype=np.uint8)
        upper_rgb = np.array(upper_rgb, dtype=np.uint8)
    except:
        pass

    car = Car()  # Car state info

    lane = Lane(params.H, w=0.5, left_lower=left_lower, left_upper=left_upper,
                right_lower=right_lower, right_upper=right_upper)  # Detected Lane info
    stopline = StopLine(params.H, pre_clearance=2, alpha_c=0.9,
                        lower_rgb=lower_rgb, upper_rgb=upper_rgb)  # Detected Stopline info

    error = Error(alpha_ey=0.9, alpha_ea=0.9)  # Error module
    controller = Controller(steer_angle_max=30, Vx_max=Vmax, c_min=0.1, tau=1.4, Ay_max=Aymax,
                            k_y=ky, k_a=ka, k_cv=kcv, k_cl=kcl)  # Controller module

    info = Info(size=100000)  # Save driving record

    motor = None
    if ismotor:  # motor flag on
        motor = Motor(vel_max=Vmax, dt=0.01)  # set motor

    dt = 0.1  # time interval

    return [ky, ka, kcv, kcl, Vmax, Aymax], car, lane, stopline, error, controller, info, motor, dt


def state_print(start_time, lane, error, car, stopline):
    print("    1/K :      ", round(1 / (lane.max_K), 2))
    print("    e_y :      ", round(error.e_y, 2))
    print("    e_a :      ", round(error.e_a * 180 / math.pi, 2))
    print("    Steering : ", round(car.u * 180 / math.pi, 2))
    print("    Vx       : ", round(car.Vx, 2))
    print("    Ax       : ", round(car.Ax, 2))
    if stopline.clearance is not None:
        print("    clearance: ", round(stopline.clearance, 2))
    print("\n\n\n")
    print("running time : ", round(time.time() - start_time, 4))


def backup(start_time, Vx_des, info, lane, stopline, car, error):
    info.get_info(time.time() - start_time, error.e_y, error.e_a * 180.0 / math.pi, car.Ax,
                  -car.Vx ** 2 / 0.16 * math.tan(car.u),
                  car.u * 180.0 / math.pi, car.Vx, Vx_des, lane.detected_lane_counts, lane.max_K)
    lane.backup()
    stopline.backup()
    car.backup()
    error.backup()


if  __name__ == "__main__":
    read_rgb(filepath="./resource/rgb_range.txt")
    read_cfg(filepath="./resource/gain.txt")
