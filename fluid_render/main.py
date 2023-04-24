import os
from pathlib import Path

import glm

from fluid_render.include.camera import Camera
from fluid_render.include.renderer import Renderer

PARTICLE_PLY_DIR = Path(__file__).absolute().parent.joinpath('resource', 'particles_data', 'vis_0.001')
# PARTICLE_PLY_DIR = Path(__file__).absolute().parent.joinpath('resource', 'particles_data', 'vis_1_0.001')
# PARTICLE_PLY_DIR = Path(__file__).absolute()ss.parent.joinpath('resource', 'particles_data', 'vis_10000_100')
# PARTICLE_PLY_DIR = Path(__file__).absolute().parent.joinpath('resource', 'particles_data', 'vis_10000_5000')
print(PARTICLE_PLY_DIR)
num_files = len([f for f in os.listdir(PARTICLE_PLY_DIR)if os.path.isfile(os.path.join(PARTICLE_PLY_DIR, f))])

camera = Camera(glm.vec3([0.0, 0.0, 6.0]))

fluid_rendere = Renderer(camera)

i = 0
while not fluid_rendere.exit():
# while True:
    # fluid_rendere.print_window_size()
    fluid_rendere.set_frame_params()
    file_path = os.path.join(PARTICLE_PLY_DIR, f'fluid_{i}.ply')
    # print(file_path)
    fluid_rendere.render(file_path)
    if i < num_files - 1:
        i += 1