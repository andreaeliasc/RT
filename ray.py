from lib import *
from sphere import *
from plane import *
from math import pi, tan
from cube import *
#from load import *

BLACK = color(0, 0, 0)
WHITE = color(255, 255, 255)
MAX_RECURSION_DEPTH = 3

class Raytracer(object):
  def __init__(self, width, height):
    self.width = width
    self.height = height
    self.background_color = color(0, 0, 0)
    self.scene = []
    self.light = None
    self.clear()

  def clear(self):
    self.pixels = [
      [self.background_color for x in range(self.width)]
      for y in range(self.height)
    ]

  def write(self, filename):
    writebmp(filename, self.width, self.height, self.pixels)

  def display(self, filename='out.bmp'):
    self.write(filename)

    try:
      from wand.image import Image
      from wand.display import display

      with Image(filename=filename) as image:
        display(image)
    except ImportError:
      pass  # do nothing if no wand is installed

  def point(self, x, y, c = None):
    try:
      self.pixels[y][x] = c or self.current_color
    except:
      pass

  def cast_ray(self, orig, direction, recursion = 0):
    material, intersect = self.scene_intersect(orig, direction)

    if material is None or recursion >= MAX_RECURSION_DEPTH:  # break recursion of reflections after n iterations
      if self.envmap:
        return self.envmap.get_color(direction)
      return self.background_color

    offset_normal = mul(intersect.normal, 1.1)

    if material.albedo[2] > 0:
      reverse_direction = mul(direction, -1)
      reflect_dir = reflect(reverse_direction, intersect.normal)
      reflect_orig = sub(intersect.point, offset_normal) if dot(reflect_dir, intersect.normal) < 0 else sum(intersect.point, offset_normal)
      reflect_color = self.cast_ray(reflect_orig, reflect_dir, recursion + 1)
    else:
      reflect_color = color(0, 0, 0)

    if material.albedo[3] > 0:
      refract_dir = refract(direction, intersect.normal, material.refractive_index)
      refract_orig = sub(intersect.point, offset_normal) if dot(refract_dir, intersect.normal) < 0 else sum(intersect.point, offset_normal)
      refract_color = self.cast_ray(refract_orig, refract_dir, recursion + 1)
    else:
      refract_color = color(0, 0, 0)

    light_dir = norm(sub(self.light.position, intersect.point))
    light_distance = length(sub(self.light.position, intersect.point))

    shadow_orig = sub(intersect.point, offset_normal) if dot(light_dir, intersect.normal) < 0 else sum(intersect.point, offset_normal)
    shadow_material, shadow_intersect = self.scene_intersect(shadow_orig, light_dir)
    shadow_intensity = 0

    if shadow_material and length(sub(shadow_intersect.point, shadow_orig)) < light_distance:
        shadow_intensity = 0.9

    intensity = self.light.intensity * max(0, dot(light_dir, intersect.normal)) * (1 - shadow_intensity)

    reflection = reflect(light_dir, intersect.normal)
    specular_intensity = self.light.intensity * (
      max(0, -dot(reflection, direction))**material.spec
    )

    diffuse = material.diffuse * intensity * material.albedo[0]
    specular = color(223,188,226) * specular_intensity * material.albedo[1]
    reflection = reflect_color * material.albedo[2]
    refraction = refract_color * material.albedo[3]

    return diffuse + specular + reflection + refraction

  def scene_intersect(self, orig, direction):
    zbuffer = float('inf')

    material = None
    intersect = None

    for obj in self.scene:
      hit = obj.ray_intersect(orig, direction)
      if hit is not None:
        if hit.distance < zbuffer:
          zbuffer = hit.distance
          material = obj.material
          intersect = hit

    return material, intersect


  def render(self):
    fov = int(pi/2)
    for y in range(self.height):
      for x in range(self.width):
        i =  (2*(x + 0.5)/self.width - 1) * tan(fov/2) * self.width/self.height
        j =  (2*(y + 0.5)/self.height - 1) * tan(fov/2)
        direction = norm(V3(i, j, -1))
        self.pixels[y][x] = self.cast_ray(V3(0,0,0), direction)




ivory = Material(diffuse=color(252,152,152), albedo=(0.6, 0.3, 0.1, 0), spec=50)
concreto = Material(diffuse=color(156,156,250), albedo=(0.9, 0.1, 0, 0, 0), spec=50)
bloqueCastleA = Material(diffuse=color(252,152,152), albedo=(0.9, 0.1, 0, 0, 0), spec=50)
bloqueCastle = Material(diffuse=color(254,211,211), albedo=(0.9, 0.1, 0, 0, 0), spec=50)
bloqueCastle2 = Material(diffuse=color(255,166,184), albedo=(0.9, 0.1, 0, 0, 0), spec=50)
castillo = Material(diffuse=color(217,190,252), albedo=(0.9, 0.1, 0, 0, 0), spec=1500)
mirror = Material(diffuse=color(138,138,249), albedo=(0, 10, 0.8, 0), spec=1425)
glass = Material(diffuse=color(150, 180, 200), albedo=(0, 0.5, 0.1, 0.8), spec=125, refractive_index=1.5)
cemento =  Material(diffuse=color(116,116,116), albedo=(0.9, 0.1, 0, 0, 0), spec=50)
interior =  Material(diffuse=color(241,163,227), albedo=(0.9, 0.1, 0, 0, 0), spec=50, refractive_index=2.5)
lights = Material(diffuse=color(245,208,61), albedo=(0.8, 0.6, 0.3, 0.1), spec=50)
r = Raytracer(800, 600)

r.light = Light(
  position=V3(-20, 100, 20),
  intensity=1.5
)

r.background_color = color(131, 175, 255)

r.scene = [
  Cube(V3(0, -2, -2), 3, glass),

]


#arbol izq
r.scene.append( Cube(V3(-1.5, -0.5, -3), 0.5 , concreto ))
r.scene.append( Cube(V3(-1.5, 0, -3), 0.5 , castillo ) )
r.scene.append( Cube(V3(-1.5, 0.5, -3), 0.5 , concreto ))
r.scene.append( Cube(V3(-1.5, 1, -3), 0.5 , castillo ))

r.scene.append( Cube(V3(-2, 1, -3), 0.5 , bloqueCastleA ) )
r.scene.append( Cube(V3(-1, 1, -3), 0.5 , bloqueCastle ) )
r.scene.append( Cube(V3(-1.5, 1.5, -3), 0.5 , bloqueCastle ) )

#interior
r.scene.append( Cube(V3(-2, 1, -3), 0.5 , bloqueCastleA ) )
r.scene.append( Cube(V3(-1, 1, -3), 0.5 , bloqueCastle ) )
r.scene.append( Cube(V3(-1.5, 1.5, -3), 0.5 , bloqueCastle ) )



#arbol derecha
r.scene.append( Cube(V3(1.5, -0.5, -3), 0.5 , concreto ))
r.scene.append( Cube(V3(1.5, 0, -3), 0.5 , castillo ) )
r.scene.append( Cube(V3(1.5, 0.5, -3), 0.5 , concreto ))
r.scene.append( Cube(V3(1.5, 1, -3), 0.5 , castillo ))

r.scene.append( Cube(V3(1, 1, -3), 0.5 , bloqueCastleA ) )
r.scene.append( Cube(V3(2, 1, -3), 0.5 , bloqueCastle2 ) )
r.scene.append( Cube(V3(1.5, 1.5, -3), 0.5 , bloqueCastle ) )


#arbol centro
r.scene.append( Cube(V3(0, -0.5, -3), 0.5 , cemento ))
r.scene.append( Cube(V3(0, 0, -3), 0.5 , cemento ) )
r.scene.append( Cube(V3(0, 0.5, -3), 0.5 , mirror ))
r.scene.append( Cube(V3(0, 1, -3), 0.5 , bloqueCastle2 ))

r.scene.append( Cube(V3(0.5, -0.5, -3), 0.5 , interior ))
r.scene.append( Cube(V3(0.5, 0, -3), 0.5 , interior ) )
r.scene.append( Cube(V3(0.5, 0.5, -3), 0.5 , interior ))
r.scene.append( Cube(V3(0.5, 1, -3), 0.5 , interior ))

r.scene.append( Cube(V3(1, -0.5, -3), 0.5 , interior ))
r.scene.append( Cube(V3(1, 0, -3), 0.5 , interior ) )
r.scene.append( Cube(V3(1, 0.5, -3), 0.5 , interior ))
r.scene.append( Cube(V3(1, 1, -3), 0.5 , interior ))

r.scene.append( Cube(V3(-0.5, -0.5, -3), 0.5 , interior ))
r.scene.append( Cube(V3(-0.5, 0, -3), 0.5 , interior ) )
r.scene.append( Cube(V3(-0.5, 0.5, -3), 0.5 , interior ))
r.scene.append( Cube(V3(-0.5, 1, -3), 0.5 , interior ))

r.scene.append( Cube(V3(-1, -0.5, -3), 0.5 , interior ))
r.scene.append( Cube(V3(-1, 0, -3), 0.5 , interior ) )
r.scene.append( Cube(V3(-1, 0.5, -3), 0.5 , interior ))
r.scene.append( Cube(V3(-1, 1, -3), 0.5 , interior ))








#techo
r.scene.append( Cube(V3(-0.5, 1, -3), 0.5 , bloqueCastle2 ) )
r.scene.append( Cube(V3(0, 1, -3.5), 0.5 , bloqueCastleA ) )
r.scene.append( Cube(V3(0.5, 1, -3), 0.5 , bloqueCastle ) )
r.scene.append( Cube(V3(0, 1.5, -3), 0.5 , bloqueCastleA ) )

#Lights
r.scene.append( Sphere(V3(-0.5, 1, -3), 0.5 , lights) )



#r.scene.append(glLoad("oso1.obj"))




r.envmap = Envmap("original1.bmp")

r.render()
r.write('TangledLights.bmp')