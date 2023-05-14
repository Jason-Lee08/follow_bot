import threading
from threading import Thread
import time
import ctypes as ct
from functools import reduce
import logging
import sys

import pygame
import serial
from serial import SerialException

from read_data import SerialLines
from optimize import Cart

######### Daemon Options ############
START_FRAME = 0xABCD
TIME_SEND = 0.05
log_interval = 10
#####################################

######### Logger Options ############
logging.basicConfig(filename='client_daemon_log.txt',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s> %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.NOTSET)
logging.info('Starting up')

brecieve = ['cmd1', 'cmd2', 'speedR_meas', 'speedL_meas', 'batVoltage', 'boardTemp']
#####################################


######### Wheel diam ##############
diam = 16.9786493


lines = SerialLines(.95)
threads = [threading.Thread(target=lines.run, args=(i,), daemon=True) for i in range(4)]
any(thread.start() for thread in threads)

cart = Cart(4)

from gui import Visualization
viz = Visualization()

class Wheels(Thread):
    def __init__(self, cart, lines):
        super(Wheels, self).__init__()
        self.data_turn = 0
        self.data_speed = 0
        self.time_log = 0
        self.control_update_msg = str.encode('info update:', 'ascii')
        self.cart = cart
        self.lines = lines

        failed = 1
        while failed:
            try:
                self.tty = serial.Serial('/dev/ttyUSB4', baudrate=115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
                failed = 0
            except SerialException:
                print('serial connection retry in 5s')
                time.sleep(5)
        
        self.data = ''

    def send(self):
        msg = START_FRAME.to_bytes(2, 'little') \
            + self.data_turn.to_bytes(2, 'little', signed=True) \
            + self.data_speed.to_bytes(2, 'little', signed=True) \
            + ct.c_uint16(START_FRAME ^ self.data_turn ^ self.data_speed).value.to_bytes(2, 'little')
        self.tty.write(msg)

    def receive(self):
        if self.tty.in_waiting:
            data = self.tty.read_all()
            if len(data) == 18:
                incoming = [int.from_bytes(data[0:2], 'little', signed=False),
                int.from_bytes(data[2:4], 'little', signed=True),
                int.from_bytes(data[4:6], 'little', signed=True),
                int.from_bytes(data[6:8], 'little', signed=True),
                int.from_bytes(data[8:10], 'little', signed=True),
                int.from_bytes(data[10:12], 'little', signed=True),
                int.from_bytes(data[12:14], 'little', signed=True),
                int.from_bytes(data[14:16], 'little', signed=False)]
                checksum = int.from_bytes(data[16:18], 'little', signed=False)

                if reduce(lambda x, y: x ^ y, incoming) == checksum:
                    if incoming[5] == 30:
                        logging.getLogger('daemon').info('Low Battery Exit')
                        sys.exit()
                    if self.time_log < (now := time.time()):
                        self.time_log = now + log_interval
                        logging.getLogger('daemon').info(
                            ' '.join([i + ': ' + str(j) for i, j in zip(brecieve, incoming[1:])])
                        )
                        self.data = data
        
    def set_speed(self, speed, alpha=0.2):
        self.data_speed = int(self.data_speed * (1 - alpha) + alpha * speed)

    def set_turn(self, turn, alpha=0.2):
        self.data_turn = int(self.data_turn * (1 - alpha) + alpha * turn)

    def run(self):
        try:
            itime_send = 0
            while True:
                now = time.time()
                self.receive()

                if itime_send < now:
                    itime_send = now + TIME_SEND
                    cart.distances = lines.moving_averages
                    cart.fxy()
                    if abs(cart.y1) < 1:
                        self.set_speed(0)
                    elif abs(cart.y1) < 3:
                        self.set_speed(100 * cart.y1)
                    else:
                        self.set_speed(300)

                    if abs(cart.x1) < .8:
                        self.set_turn(0)
                    elif abs(cart.x1) < 3:
                        self.set_turn(120 * cart.x1)
                    else:
                        self.set_turn(360)
                    
                    self.send()
        except:
            logging.getLogger('daemon').exception('Exit due to:')
            sys.exit()

wheels = Wheels(cart, lines)
wheels.start()

fps_clock = pygame.time.Clock()
while True:
    texts = [
        'Inputs',
        ', '.join(f'{i}'.rjust(6) for i in ['speed', 'turn']),
        ', '.join(f'{i}'.rjust(6) for i in [wheels.data_speed, wheels.data_turn]),
        'Measurements',
        ', '.join(f'{i}'.rjust(6) for i in ['cmd1', 'cmd2', 'speedR_meas', 'speedL_meas', 'batVoltage', 'boardTemp']),
        ', '.join(f'{i}'.rjust(6) for i in wheels.data)
    ]
    viz.updateScreen([100 * i for i in lines.moving_averages], (cart.x1 * 100, cart.y1 * 100), texts)
    print(f'{cart.x1:.2f}\t{cart.y1:.2f}\t{lines.real:0.2f}\t{lines.moving_averages}\t\t\t\t', end='\r')
    fps_clock.tick(30)

    
