import os
from pathlib import Path

import glm

from fluid_render.include.camera import Camera
from fluid_render.include.renderer_separate_v2 import Renderer
from fluid_render.include.static_variable import particle_radius

'''多相-四相混溶'''
# PARTICLE_PLY_DIR = r'D:\XYH\论文实验\本科毕业设计\多相流\多相\四相混溶\r005'
# PARTICLE_PLY_DIR = r'D:\XYH\论文实验\本科毕业设计\多相流\多相\四相混溶\r005-dt4'
# PARTICLE_PLY_DIR = r'D:\XYH\论文实验\本科毕业设计\多相流\多相\四相混溶\r004-dt4'
# PARTICLE_PLY_DIR = r'D:\XYH\论文实验\本科毕业设计\多相流\多相\四相不混溶\r004-dt4'
# PARTICLE_PLY_DIR = r'D:\XYH\论文实验\本科毕业设计\多相流\多相\四相混溶\r004-dt4-v2'
PARTICLE_PLY_DIR = r'D:\XYH\论文实验\本科毕业设计\多相流\多相-yr\四相不混溶-500-3000-1000-5000\r004-0.5X0.5'
# PARTICLE_PLY_DIR = r'D:\XYH\论文实验\本科毕业设计\多相流\多相-yr\四相混溶-500-3000-1000-5000\r004-0.5X0.5'
PARTICLE_PLY_DIR = r'D:\XYH\论文实验\本科毕业设计\多相流\多相-yr\三相不混溶-1000-3000-5000\r004-0.5X0.5'
'''小水块掉落大水块'''
# PARTICLE_PLY_DIR = r'D:\XYH\论文实验\本科毕业设计\多相流\两相\不混溶\小水块掉落大水块\r004-dt4'
# PARTICLE_PLY_DIR = r'D:\XYH\论文实验\本科毕业设计\多相流\两相\混溶\小水块掉落大水块\r004-dt4'
# num_files = len([f for f in os.listdir(PARTICLE_PLY_DIR)if os.path.isfile(os.path.join(PARTICLE_PLY_DIR, f))])
# camera = Camera(position=glm.vec3([-2.29399,    -0.171017,     -1.17689]), yaw=27.10000000000001, pitch=-18.8)
# camera = Camera(position=glm.vec3([-1.94482,    -0.569545,      -1.3672]), yaw=33.2, pitch=-6.600000000000009)
# camera = Camera(position=glm.vec3([ 1.85301,    -0.721585,      0.66702]), yaw=-163.49999999999986, pitch=-13.000000000000032)
camera = Camera(position=glm.vec3([ 2.80193,    -0.493102,     0.948102]), yaw=-163.49999999999986, pitch=-13.000000000000032)

'''渲染管线'''
# camera = Camera(position=glm.vec3([ 2.6341,    -0.146576,      1.32078]), yaw=-153.30000000000027, pitch=-6.900000000000063)
# camera = Camera(position=glm.vec3([ 1.75457,    -0.340536,     0.906647]), yaw=-152.3000000000003, pitch=-18.600000000000044)
# camera = Camera(position=glm.vec3([ 1.70784,    -0.340536,      1.02574]), yaw=-146.4000000000002, pitch=-17.60000000000003)
i = 0

'''渲染'''
num_files = len([f for f in os.listdir(PARTICLE_PLY_DIR)if os.path.isfile(os.path.join(PARTICLE_PLY_DIR, f))])
particle_data_time = 0
_render_time = 0

depth_time        = 0
thick_time        = 0
smooth_depth_time = 0
smooth_thick_time = 0
normal_time       = 0
shader_time       = 0
read_time   = 0
render_time = 0
glfw_frame_time  = 0
ssf_time    = 0
# render_start  = 50
render_start  = 1
# render_start  = 100
# render_start  = 150
render_num  = num_files - 1

fluid_rendere = Renderer(camera)

i = 1
j = 0
k = 0
# i = 100
# i = 198
# i = 650
# i = 315
# i = 500
# i = 870
# i = 1503
print(i)
flag = True
save_img_dir = r'D:\XYH\论文实验\本科毕业设计\渲染多遍-保存图片\小水块掉落大水块\不混溶\r004-dt4'
save_img_dir = r'D:\XYH\论文实验\本科毕业设计\渲染多遍-保存图片\三相溃坝\不混溶-yr\r004-0.5X0.5'
# save_img_dir = r'D:\XYH\论文实验\本科毕业设计\渲染多遍-保存图片\四相溃坝\不混溶-yr\r004-0.5X0.5'

save_flag = True
if not os.path.exists(save_img_dir):
    os.makedirs(save_img_dir)

k_fluid = [1, 2, 3, 4]
k_fluid = [1, 2, 3]
# k_fluid = [1, 2]
# k_fluid = [1, 3]
while not fluid_rendere.exit():
    # print(i)
    k += 1
    fluid_rendere.set_frame_params()
    # file_path = os.path.join(PARTICLE_PLY_DIR, f'granular_{i}.ply')
    file_path = os.path.join(PARTICLE_PLY_DIR, f'fluid_{i}.ply')
    # file_path = os.path.join(PARTICLE_PLY_DIR, f'frame_{i}.ply')
    fluid_rendere.render(file_path, k_fluid)
    # if i < 201:
    if i < num_files - 1:
        # fluid_rendere.save_frame_img(save_img_dir)
        if save_flag:
            fluid_rendere.save_frame_img(save_img_dir, i)
        i += 1
    if flag:
        print('粒子数量: %d'%fluid_rendere.m_particle_num)
        flag = False
    # if k >= render_start and k < render_num:
    #     j += 1
    #     depth_time        += fluid_rendere.m_ssf_renderer.depth_time
    #     thick_time        += fluid_rendere.m_ssf_renderer.thick_time
    #     smooth_depth_time += fluid_rendere.m_ssf_renderer.smooth_depth_time
    #     smooth_thick_time += fluid_rendere.m_ssf_renderer.smooth_thick_time
    #     normal_time       += fluid_rendere.m_ssf_renderer.normal_time
    #     shader_time       += fluid_rendere.m_ssf_renderer.shader_time
    #     render_time       += fluid_rendere.render_time
    #     # read_time         += fluid_rendere.read_time
    #     glfw_frame_time   += fluid_rendere.delta_time
    #     ssf_time          += fluid_rendere.ssf_time

        # _render_time     += fluid_rendere._render_time
        # particle_data_time += fluid_rendere.particle_data_time
    # elif k >= render_num:
    #     break

    # camera.print_camera_position()


try:
    '''一帧渲染时间'''
    count = 6
    av_depth        = round(depth_time / j, count)
    av_thick        = round(thick_time / j, count)
    av_smooth_depth = round(smooth_depth_time / j, count)
    av_smooth_thick = round(smooth_thick_time / j, count)
    av_normal       = round(normal_time / j, count)
    av_shader       = round(shader_time / j, count)
    av_render       = round(render_time / j, count)
    av_read         = round(read_time / j, count)
    av_frame        = round(av_render + av_read, count)
    av_glfw         = round(glfw_frame_time / j, count)
    av_ssf          = round(ssf_time / j, count)

    av_render1       = round(_render_time / j, count)
    av_particle_data = round(particle_data_time / j, count)

    print(f'粒子数为{fluid_rendere.m_particle_num}, {j}帧平均一帧平滑时间为{av_smooth_depth},{j}帧平均一帧渲染时间为{av_render}, {j}帧平均一帧读取时间为{av_read}, {j}帧平均一帧总时间为{av_frame}')
    '''
    粒子半径, 
    粒子数目, 
    深度时间，
    厚度时间, 
    平滑深度时间, 
    平滑厚度时间, 
    法向量时间，
    着色时间，
    渲染时间, 
    读取文件时间, 
    一帧时间(渲染+读取), 
    glfw一帧时间, 
    ssf时间'''
    print(particle_radius, 
        fluid_rendere.m_particle_num, 
        av_depth,
        av_thick,
        av_smooth_depth, 
        av_smooth_thick,
        av_normal,
        av_shader,
        av_render, 
        av_read, 
        av_frame, 
        av_glfw,
        av_ssf,

        #   av_render1,
        #   av_particle_data
        )
except Exception as e:
    print(e) 
