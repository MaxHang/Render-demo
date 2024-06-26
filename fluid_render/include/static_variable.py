import numpy as np
import glm
from fluid_render.include.helper import cal_fresnel_R0
from fluid_render.include.gui_params import filter_size

skybox_vertices = np.array(
    [
    # positions          
    -1.0,  1.0, -1.0,
    -1.0, -1.0, -1.0,
     1.0, -1.0, -1.0,
     1.0, -1.0, -1.0,
     1.0,  1.0, -1.0,
    -1.0,  1.0, -1.0,

    -1.0, -1.0,  1.0,
    -1.0, -1.0, -1.0,
    -1.0,  1.0, -1.0,
    -1.0,  1.0, -1.0,
    -1.0,  1.0,  1.0,
    -1.0, -1.0,  1.0,

     1.0, -1.0, -1.0,
     1.0, -1.0,  1.0,
     1.0,  1.0,  1.0,
     1.0,  1.0,  1.0,
     1.0,  1.0, -1.0,
     1.0, -1.0, -1.0,

    -1.0, -1.0,  1.0,
    -1.0,  1.0,  1.0,
     1.0,  1.0,  1.0,
     1.0,  1.0,  1.0,
     1.0, -1.0,  1.0,
    -1.0, -1.0,  1.0,

    -1.0,  1.0, -1.0,
     1.0,  1.0, -1.0,
     1.0,  1.0,  1.0,
     1.0,  1.0,  1.0,
    -1.0,  1.0,  1.0,
    -1.0,  1.0, -1.0,

    -1.0, -1.0, -1.0,
    -1.0, -1.0,  1.0,
     1.0, -1.0, -1.0,
     1.0, -1.0, -1.0,
    -1.0, -1.0,  1.0,
     1.0, -1.0,  1.0,
    ],
    dtype=np.float32
)

# skybox的六个面
# skybox_faces = [
#     "right.jpg",
#     "left.jpg",
#     "top.jpg",
#     "bottom.jpg",
#     "front.jpg",
#     "back.jpg",
# ]
# skybox_faces = [
#     "posx.jpg",
#     "negx.jpg",
#     "posy.jpg",
#     "negy.jpg",
#     "posz.jpg",
#     "negz.jpg",
# ]
skybox_faces = [
    "posx.png",
    "negx.png",
    "posy.png",
    "negy.png",
    "posz.png",
    "negz.png",
]
# skybox_faces = [
#     "posx.png",
#     "negx.png",
#     "posy.png",
#     "negy.png",
#     "posz.png",
#     "negz.png",
# ]

# 灯
lamp_vertices = skybox_vertices

ground_vertices = np.array(
    [
	#position, tex coord
	-5.0, -1.5,  5.0, 0.0, 1.0,
	-5.0, -1.5, -5.0, 0.0, 0.0,
	 5.0, -1.5, -5.0, 1.0, 0.0,
	-5.0, -1.5,  5.0, 0.0, 1.0,
	 5.0, -1.5, -5.0, 1.0, 0.0,
	 5.0, -1.5,  5.0, 1.0, 1.0
    ],
    dtype= np.float32
)
# ground_vertices = np.array(
#     [
# 	#position, tex coord
# 	-5.0, -2.0,  5.0, 0.0, 1.0,
# 	-5.0, -2.0, -5.0, 0.0, 0.0,
# 	 5.0, -2.0, -5.0, 1.0, 0.0,
# 	-5.0, -2.0,  5.0, 0.0, 1.0,
# 	 5.0, -2.0, -5.0, 1.0, 0.0,
# 	 5.0, -2.0,  5.0, 1.0, 1.0
#     ],
#     dtype= np.float32
# )

# 屏幕空间的位置以及纹理
quad_vertices = np.array(
    [
    # positions  also as  texCoords
    -1.0,  1.0,  0.0, 1.0,
    -1.0, -1.0,  0.0, 0.0,
     1.0, -1.0,  1.0, 0.0,
    -1.0,  1.0,  0.0, 1.0,
     1.0, -1.0,  1.0, 0.0,
     1.0,  1.0,  1.0, 1.0,
    ],
    dtype= np.float32
)

# 粒子半径
particle_radius = 0.1
# particle_radius = 0.09
# particle_radius = 0.08
particle_radius = 0.07
particle_radius = 0.06
# particle_radius = 0.05
# particle_radius = 0.04
# particle_radius = 0.03
# particle_radius = 0.035
# particle_radius = 0.025

# 010
# 009
# 008
# 007
# 006
# 005
# 004
# 003
# 002



# 远近平面
near = 0.1
far  = 100.0

# Bilateral filter:  refer to https://en.wikipedia.org/wiki/Bilateral_filter
"""Bilateral filter:  refer to https://en.wikipedia.org/wiki/Bilateral_filter

:param sigma_r: 像素值高斯函数的sigma
:param sigma_d: 坐标值高斯函数的sigma

As the range parameter sigma_r increases, the bilateral filter gradually approaches Gaussian convolution more closely because the range Gaussian widens and flattens, which means that it becomes nearly constant over the intensity interval of the image.
As the spatial parameter sigma_d increases, the larger features get smoothened.
"""
max_filter_size = 100
max_filter_size = 150
# max_filter_size = 50
# 双边过滤
sigma_r = 0.15
sigma_d = 0.7 * particle_radius
#  2*sigma平方
two_sigma_r2 = 2 * sigma_r * sigma_r
two_sigma_d2 = 2 * sigma_d * sigma_d

# 窄范围过滤
delta = 10 * filter_size
mu    = 1 * filter_size

""" 菲涅尔项, 使用Schlick近似, Schlick近似给出了反射系数R, 表示反射光占入射光的能量的比例

    R(theta) = R0 + (1 - R0) * (1 - cos(theta))^5
    R0 = ((n1 - n2)/(n1 + n2)) ^ 2
"""

n_water = 1.33
n_air   = 1.0
refractive_index = n_water / n_air
R0_air_to_water = cal_fresnel_R0(n_air, n_water)
# R0_air_to_water = 0.5
# R0_air_to_water = 1.0

"""材质信息
"""
emerald_material = glm.vec3(0.0215, 0.1745, 0.0215), glm.vec3(0.07568, 0.61424, 0.07568), glm.vec3(0.633, 0.727811, 0.633), 0.6
pearl_material = glm.vec3(0.25, 0.20725, 0.20725), glm.vec3(1.0, 0.829, 0.829), glm.vec3(0.296648, 0.296648, 0.296648), 0.088


material = emerald_material

use_set_activate_flag = False
# set_activate_values = glm.vec4(0.25,0.25,0.25,0.25)
set_activate_values = glm.vec4(1.0, 1.0, 1.0, 1.0)
set_activate_values = set_activate_values / 4.0