import serial
import time
import threading

from optimize import Cart

class SerialLines:
    def __init__(self, alpha=0.5):
        self.serial_lines = [
            serial.Serial(f'/dev/ttyUSB{i}', 115200, timeout=2) for i in range(4)
        ]
        self.moving_averages = [1] * 4
        self.real = 1
        self.alpha = alpha
        self.error = [0] * 4
    
    def run(self, line):
        while True:
            output = self.serial_lines[line].readline().decode('ascii')
            if len(output) > 0 and output[0] != 'I':
                output = output[:-2]
                self.moving_averages[line] = self.moving_averages[line] * (1-self.alpha) + self.alpha * float(output)
            elif len(output) == 0:
                self.error[line] = 1
                if sum(self.error) == 4:
                    self.moving_averages = [1] * 4
            self.real = sum(self.moving_averages) / len(self.moving_averages)
    
if __name__ == '__main__':
    lines = SerialLines()
    threads = [threading.Thread(target=lines.run, args=(i,), daemon=True) for i in range(4)]
    any(thread.start() for thread in threads)

    cart = Cart(4)

    from gui import Visualization
    viz = Visualization()

    while True:
        cart.distances = lines.moving_averages
        cart.fxy()
        x, y = cart.x1, cart.y1
        viz.updateScreen([100 * i for i in lines.moving_averages], (x * 100, y * 100), [])
        print(f'{x:.2f}\t{y:.2f}\t{lines.real:0.2f}\t{lines.moving_averages}')
        time.sleep(0.1)




