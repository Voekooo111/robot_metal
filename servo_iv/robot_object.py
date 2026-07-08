from .robot_pca9685 import Robot_pca
from .commands import Commands
from .web import Site

robot = Robot_pca()

site = Site()

commands = Commands(robot, site)

site.bind(robot, commands)

robot.class_start()
print("Робот готов.")