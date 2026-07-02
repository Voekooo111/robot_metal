from servo_iv import robot, Site
import signal
import sys

def signal_handler(sig, frame):
    """Перехват сигнала Ctrl+C"""
    print('Программа успешно завершена')
    robot.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
site = Site()
site.run()
