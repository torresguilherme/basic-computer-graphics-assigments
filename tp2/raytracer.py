import argparse
import numpy as np
import math
import itertools
import time
import multiprocessing
import statistics
from multiprocessing.dummy import Pool

PIXEL_SIZE = 0.01
DISTRIBUTED_RAYS = 4
VISION_RANGE = 2 ** 63 - 1
CPUS = multiprocessing.cpu_count()
OBJ_NEAR = 0.0005

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
    
    def __str__(self):
        return '(' + str(self.x) + ',' + str(self.y) + ',' + str(self.z) + ')'
    
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

    def __truediv__(self, scalar):
        return Vec3(self.x / scalar, self.y / scalar, self.z / scalar)
    
    def __trueidiv__(self, scalar):
        return self / scalar
    
    def array(self):
        return [self.x, self.y, self.z]
    
    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z
    
    def cross(self, other):
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.x * other.z - self.z * other.x,
            self.x * other.y - self.y * other.x
        )
    
    def reflect(self, normal):
        return self - 2 * self.dot(normal) * normal
    
    def refract(self, normal, ni_over_nt):
        unit_v = self.normalize()
        cosine = unit_v.dot(normal)
        discriminant = 1 - ni_over_nt * ni_over_nt * (1 - cosine * cosine)
        if(discriminant >= 0):
            return ni_over_nt * (unit_v - normal * cosine) - normal * math.sqrt(discriminant)
        return Vec3(0, 0, 0)

    def lenght(self):
        return math.sqrt(self.dot(self))
    
    def normalize(self):
        return Vec3(self.x / self.lenght(), self.y / self.lenght(), self.z / self.lenght())

class Ray:
    def __init__(self, *args):
        if len(args) == 2:
            self.start = args[0]
            self.direction = args[1].normalize()
        else:
            self.start = Vec3()
            self.direction = Vec3()
    
    def __str__(self):
        return 'Start: ' + str(self.start) + ' Direction: ' + str(self.direction)

    def point_at_t(self, t):
        return self.start + self.direction * t

#######################################
### ILLUMINATION PRIMITIVES
#######################################

class PointLight:
    def __init__(self, position, color):
        self.position = position
        self.color = color
    
    def __str__(self):
        return 'Light position: ' + str(self.position) + ' Color: ' + str(self.color)

class Material:
    def __init__(self, **kwargs):
        self.type = kwargs.get('type')
        self.albedo = kwargs.get('albedo')
        if self.type == 'dielectric':
            # cover glass/dielectric materials
            self.k_refraction = kwargs.get('k_refraction')
        elif self.type == 'reflective':
            # cover metal/reflective material parameters
            self.k_reflectance = kwargs.get('k_reflectance')
            self.fuzz = kwargs.get('fuzz')
        elif self.type == 'phong':
            # cover phong material parameters
            self.shading = kwargs.get('shading')
            self.k_specular = kwargs.get('k_specular')
        else:
            self.type = 'lambert'
            self.k_diffuse = kwargs.get('k_diffuse')
    
    def __str__(self):
        return 'Type: ' + self.type + ' Albedo: ' +  str(self.albedo)

#######################################
### SHAPE PRIMITIVES
#######################################

class Sphere:
    def __init__(self, center, radius, material):
        self.center = center
        self.radius = radius
        self.material = material
    
    def normal(self, point):
        return (point - self.center).normalize() 

#######################################
### RAY INTERSECT HANDLING
#######################################

def trace_rays(shapes, point_lights, i, j, width, height, camera_eye, camera_up, camera_right, camera_front, focal_dist):
    ipc = camera_eye + camera_front * focal_dist
    colors = []
    for k in range(DISTRIBUTED_RAYS):
        sampling_offset = (k % math.sqrt(DISTRIBUTED_RAYS) / math.sqrt(DISTRIBUTED_RAYS), \
                            k / math.sqrt(DISTRIBUTED_RAYS) / math.sqrt(DISTRIBUTED_RAYS))
        # ray = eye + t * (pixel_pos - eye)
        ray = Ray(camera_eye, (ipc - camera_eye) + (camera_right * (j - width/2 + sampling_offset[0]) * PIXEL_SIZE) \
            + (camera_up * (height/2 - i + sampling_offset[1]) * PIXEL_SIZE))
        
        params = []
        for s in shapes:
            params.append(intersects(ray, s))
        
        min_t = VISION_RANGE
        color = Vec3(0, 0, 0)
        for p in params:
            if p[0] >= focal_dist and p[0] < min_t:
                color = p[1]
                min_t = p[0]
        
        if color != Vec3(0, 0, 0):
            occlusions = []
            for light in point_lights:
                occlusions.append(occlusion(ray, min_t, shapes, light))
        color *= statistics.mean(occlusions)
        colors.append(color)

    # retorna media das cores
    average = [0, 0, 0]
    for k in range(DISTRIBUTED_RAYS):
        for l in range(3):
            average[l] += colors[k][l]
    for k in range(3):
        average[k] /= DISTRIBUTED_RAYS
    return average

def intersects(ray, shape):
    # intersect with sphere
    try:
        oc = ray.start - shape.center
        a = ray.direction.dot(ray.direction)
        b = 2 * oc.dot(ray.direction)
        c = oc.dot(oc) - shape.radius * shape.radius
        discriminant = b * b - 4 * a * c
        if discriminant >= 0:
            solution = (-b - math.sqrt(discriminant))/ (2 * a)
            return solution, shape.material.albedo * shape.material.k_diffuse
        else:
            return -1, Vec3(0, 0, 0)
    except AttributeError:
        pass
    
    # intersect with triangle

    return -1, Vec3(0, 0, 0)

def occlusion(ray, point_of_intersection, shapes, light):
    k_occlusion = 1
    ray_to_light = Ray(ray.point_at_t(point_of_intersection), light.position - ray.point_at_t(point_of_intersection))
    for shape in shapes:
        if intersects(ray_to_light, shape)[0] > OBJ_NEAR:
            k_occlusion = 0
        else:
            k_occlusion = max(0.0, 1+ray_to_light.direction.dot(ray.direction))
    return k_occlusion

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
    focal_dist = 2
    camera_target = Vec3(0, 0, 2)
    camera_up = Vec3(0, 1, 0)
    camera_right = camera_up.cross(camera_target - camera_eye).normalize()
    camera_up = camera_right.cross((camera_target - camera_eye).normalize())
    camera_front = (camera_target - camera_eye).normalize()

    # get shapes
    shapes = []
    ground_material = Material(type='lambert', albedo=Vec3(0, 255, 150), k_diffuse=0.8)
    ball_material = Material(type='lambert', albedo=Vec3(255, 255, 0), k_diffuse=0.9)
    shapes.append(Sphere(Vec3(0, -100, 20), 100, ground_material))
    shapes.append(Sphere(Vec3(0, 0, 5), 1, ball_material))

    # get lights
    point_lights = [PointLight(Vec3(3, 3, 3), Vec3(255, 255, 255)), PointLight(Vec3(-3, 3, 3), Vec3(255, 255, 255))]

    # init pixel array
    pixel_array = np.zeros((height, width, 3), dtype=np.uint8)
    
    # render image
    start_time = time.time()

    for i in range(height):
        for j in range(width):
            pixel_array[i][j] = trace_rays(shapes, point_lights, i, j, width, height, camera_eye, camera_up, camera_right, camera_front, focal_dist)

    #pool = Pool(CPUS)
    #results = pool.starmap(trace_rays, [itertools.repeat(shapes), range(width), range(height), \
    #    itertools.repeat(width), itertools.repeat(height), \
    #    itertools.repeat(camera_eye), itertools.repeat(camera_up), itertools.repeat(camera_right), \
    #    itertools.repeat(camera_front), itertools.repeat(focal_dist)])

    end_time = time.time() - start_time
    print('Imagem renderizada em ' + str(end_time) + ' segundos')

    # output img
    with open(ouf, 'w') as f:
        f.write('P3\n' + str(width) + ' ' + str(height) + '\n255\n')
        for row in pixel_array:
            for pixel in row:
                for channel in pixel:
                    f.write(str(channel) + ' ')
            f.write('\n')

if __name__ == '__main__':
    main()