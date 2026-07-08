from .robot_pca9685 import Robot_pca
from .commands import Commands
from .web import Site

commands = Commands()
robot = Robot_pca()
site = Site()
robot.class_start()
