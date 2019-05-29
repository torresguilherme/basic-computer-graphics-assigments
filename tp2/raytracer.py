import argparse
import numpy as np
import math
from threading import Thread, ThreadError

#######################################
### MATH PRIMITIVES
#######################################

class Vec3:
    def __init__(self, *args):
        if len(args) == 3:
            self.x = args[0]
            self.y = args[1]
            self.z = args[2]
        else:
            self.x = 0
            self.y = 0
            self.z = 0
    
    def __getitem__(self, key):
        if key is 0:
            return self.x
        elif key is 1:
            return self.y
        elif key is 2:
            return self.z
        else:
            raise IndexError('Vec3 index must be in range, not ' + key)
    
    def __setitem__(self, key, value):
        if key is 0:
            self.x = value
        elif key is 1:
            self.y = value
        elif key is 2:
            self.z = value
        else:
            raise IndexError('Vec3 index must be in range, not ' + key)
    
    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __iadd__(self, other):
        return self + other
    
    def __isub__(self, other):
        return self - other
    
    def __mul__(self, scalar):
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __imul__(self, scalar):
        return self * scalar
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other):
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.x * other.z - self.z * other.x,
            self.x * other.y - self.y * other.x
        )
    
    def lenght(self):
        return math.sqrt(self.dot(self))
    
    def normalize(self):
        return Vec3(self.x / self.lenght(), self.y / self.lenght(), self.z / self.lenght())

class Ray:
    def __init__(self, *args):
        if len(args) == 2:
            self.start = args[0]
            self.direction = args[1]
        else:
            self.start = Vec3()
            self.direction = Vec3()

    def point_at_t(self, t):
        return self.start + self.direction * t

#######################################
### SHAPE PRIMITIVES
#######################################

class Sphere:
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

#######################################
### RAY INTERSECT HANDLING
#######################################

def trace_rays(shapes, i, j, width, height, camera_eye, camera_up, camera_right, camera_front, focal_dist):
    ray = Ray(camera_eye, Vec3(
        0, 0, 0
    ))

    params = []
    for s in shapes:
        params.append(intersects(ray, s))
    
    for p in params:
        if p > 0:
            color = Vec3(1, 0, 0)
            return [color[0], color[1], color[2]]
    
    return [0, 0, 0]

def intersects(ray, shape):
    return -1

#######################################
### MAIN
#######################################

def main():
    # pegar arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str, help='arquivo de input')
    parser.add_argument('output_file', type=str, help='arquivo de saida')
    parser.add_argument('-width', type=int, help='largura do arquivo de saida')
    parser.add_argument('-height', type=int, help='altura do arquivo de saida')

    args = parser.parse_args()
    inf = args.input_file
    ouf = args.output_file
    width = 480
    height = 340
    if args.width:
        width = args.width
    if args.height:
        height = args.height
    
    # camera parameters
    camera_eye = Vec3()
    focal_dist = 1
    camera_target = Vec3(0, 0, 2)
    camera_up = Vec3(0, 1, 0)
    camera_right = (camera_target - camera_eye).cross(camera_up).normalize()
    camera_front = camera_up.cross(camera_right)

    # get shapes
    shapes = []
    shapes.append(Sphere(Vec3(0, 0, 2), 1))

    # init pixel array
    pixel_array = np.zeros((width, height, 3), dtype=np.uint8)
    
    # calculate rays
    for i in range(len(pixel_array)):
        for j in range(len(pixel_array[i])):
            pixel_array[i][j] = trace_rays(shapes, i, j, width, height, camera_eye, camera_up, camera_right, camera_front, focal_dist)

    # output img
    with open(ouf, 'w') as f:
        f.write('P3\n' + str(width) + ' ' + str(height) + '\n255\n')
        for row in pixel_array:
            for pixel in row:
                for channel in pixel:
                    f.write(str(channel) + ' ')
                f.write(('\n'))
            f.write('\n')

if __name__ == '__main__':
    main()