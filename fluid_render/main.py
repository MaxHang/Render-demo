import os
from pathlib import Path

import glm

from fluid_render.include.camera import Camera
from fluid_render.include.renderer import Renderer

# PARTICLE_PLY_DIR = Path(__file__).absolute().parent.joinpath('resource', 'particles_data', 'vis_0.001')
PARTICLE_PLY_DIR = 'E:\data\ex7'
# PARTICLE_PLY_DIR = 'E:\data\ex6'
# PARTICLE_PLY_DIR = 'E:\data\ex5'
# PARTICLE_PLY_DIR = 'E:\data\ex4'
# PARTICLE_PLY_DIR = 'E:\data\ex3'
# PARTICLE_PLY_DIR = 'E:\data\ex2'
# PARTICLE_PLY_DIR = 'E:\data\ex1'
# PARTICLE_PLY_DIR = Path(__file__).absolute().parent.joinpath('resource', 'particles_data', 'plydemo')
# PARTICLE_PLY_DIR = Path(__file__).absolute().parent.joinpath('resource', 'particles_data', 'jrh')
# PARTICLE_PLY_DIR = Path(__file__).absolute().parent.joinpath('resource', 'particles_data', 'vis_1_0.001')
# PARTICLE_PLY_DIR = Path(__file__).absolute().parent.joinpath('resource', 'particles_data', 'vis_10000_100')
# PARTICLE_PLY_DIR = Path(__file__).absolute().parent.joinpath('resource', 'particles_data', 'vis_10000_5000')
print(PARTICLE_PLY_DIR)
num_files = len([f for f in os.listdir(PARTICLE_PLY_DIR)if os.path.isfile(os.path.join(PARTICLE_PLY_DIR, f))])

camera = Camera(glm.vec3([0.0, -0.75, 4.0]))
# camera = Camera(glm.vec3([0.0, 0.0, 6.0]))
# camera = Camera(glm.vec3([-1.51893,    -0.351282,    -0.768662]))
# camera = Camera(glm.vec3([-0.222567,   -0.0635315,     0.311827]))
# camera = Camera(glm.vec3([0.00944561,     -0.12959,    -0.665845]))
# camera = Camera(glm.vec3([-2.39164, -0.0570935, -4.8922]))

fluid_rendere = Renderer(camera)

i = 0
# i = 401
while not fluid_rendere.exit():
# while True:
    # fluid_rendere.print_window_size()
    print(i)
    fluid_rendere.set_frame_params()
    file_path = os.path.join(PARTICLE_PLY_DIR, f'fluid_{i}.ply')
    # file_path = os.path.join(PARTICLE_PLY_DIR, f'frame_{i}.ply')
    # print(file_path)
    fluid_rendere.render(file_path)
    # if i < 315:
    #     i += 1
    if i < num_files - 1:
        i += 1
    # camera.print_camera_position()
    # if i < 16:
    #     i += 1