from servo_iv import Robot_pca


robot = Robot_pca()
robot.define_servo()
robot.calibrate()
robot.close()
