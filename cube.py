from lib import *
from plane import *
from sphere import *

class Cube(object):
  def __init__(self, position, size, material):
    self.position = position
    self.size = size
    self.material = material
    self.planes = []

    halfSize = size / 2

    self.planes.append(Plane(sum(position, V3(halfSize,0,0)), V3(1,0,0), material))
    self.planes.append(Plane(sum(position, V3(-halfSize,0,0)), V3(-1,0,0), material))

    self.planes.append(Plane(sum(position, V3(0,halfSize,0)), V3(0,1,0), material))
    self.planes.append(Plane(sum(position, V3(0,-halfSize,0)), V3(0,-1,0), material))

    self.planes.append(Plane(sum(position, V3(0,0,halfSize)), V3(0,0,1), material))
    self.planes.append(Plane(sum(position, V3(0,0,-halfSize)), V3(0,0,-1), material))


  def ray_intersect(self, origin, direction):
    epsilon = 0.001
    min_boundbox = [0, 0, 0]
    max_boundbox = [0, 0, 0]

    for i in range(3):
      min_boundbox[i] = self.position[i] - (epsilon + self.size / 2)
      max_boundbox[i] = self.position[i] + (epsilon + self.size / 2)

    t = float('inf')
    intersect = None

    for plane in self.planes:
      plane_intersect = plane.ray_intersect(origin, direction)

      if plane_intersect is not None:
        if plane_intersect.point[0] >= min_boundbox[0] and plane_intersect.point[0] <= max_boundbox[0]:
          if plane_intersect.point[1] >= min_boundbox[1] and plane_intersect.point[1] <= max_boundbox[1]:
            if plane_intersect.point[2] >= min_boundbox[2] and plane_intersect.point[2] <= max_boundbox[2]:
              if plane_intersect.distance < t:
                t = plane_intersect.distance
                intersect = plane_intersect

    if intersect is None:
      return None

    return Intersect(
      distance = intersect.distance,
      point = intersect.point,
      normal = intersect.normal
    )
