import numpy as np

class Cart:
    def __init__(self, count_dists, lr=0.005):
        self.width = .45
        self.length = .6
        self.distances = [1] * count_dists
        self.lr = lr
        self.x1 = 0
        self.y1 = 0
        self.prev_dist = None
    
    def fxy(self):
        dist = np.array(self.distances).reshape(4,1)
        if (self.prev_dist == dist).all():
            return
        A = np.array([[-self.width/2], [self.width/2]] * 2)
        B = np.array([[self.length], [self.length], [-self.length], [-self.length]]) / 2
        x1 = 0
        y1 = 0
        for i in range(100):
            x0, y0 = x1, y1
            x_vec = (x0 - A)
            y_vec = (y0 - B)
            mult = (np.square(x0-A) + np.square(y0-B) - np.square(dist)) # constants for each grad term
            grad_x = np.sum(mult * x_vec)
            grad_y = np.sum(mult * y_vec)
            x1 = x0 - self.lr * grad_x
            y1 = y0 - self.lr * grad_y
        self.x1 = x1
        self.y1 = y1
        self.prev_dist = dist
        


if __name__ == "__main__":
    point = np.array((0, 5))
    receivers = np.array([[-.225, .3], [.225, .3], [-.225, -.3], [.225, -.3]])
    distxy = receivers - point
    dist = np.linalg.norm(distxy, axis=1)

    print((point[0] - receivers[:, 0]) ** 2 + (point[1] - receivers[:, 1]) ** 2 - dist ** 2)

    cart = Cart(4)
    cart.distances = list(dist)
    print(cart.fxy())


    

