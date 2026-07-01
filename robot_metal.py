from servo_iv import Pca
from servo_iv import Robot_pca
import time


robot = Robot_pca()
robot.define_servo()
robot.calibrate()
robot.stand()
robot.close()
