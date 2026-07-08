from .robot_pca9685 import Robot_pca
from .web import Site
from .commands import Commands

robot = Robot_pca()
site = Site()

commands = Commands(robot, site)

robot.class_start()