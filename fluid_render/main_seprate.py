import os
from pathlib import Path

import glm

from fluid_render.include.camera import Camera
from fluid_render.include.renderer_separate import Renderer
from fluid_render.include.static_variable import particle_radius

'''单相流'''
# PARTICLE_PLY_DIR = 'D:\c-disk-data\Desktop\毕业设计\Graduation-Experment\单相流\\r010'
# PARTICLE_PLY_DIR = 'D:\c-disk-data\Desktop\毕业设计\Graduation-Experment\单相流\\r009'
# PARTICLE_PLY_DIR = 'D:\c-disk-data\Desktop\毕业设计\Graduation-Experment\单相流\\r008'
# PARTICLE_PLY_DIR = 'D:\c-disk-data\Desktop\毕业设计\Graduation-Experment\单相流\\r007'
# PARTICLE_PLY_DIR = 'D:\c-disk-data\Desktop\毕业设计\Graduation-Experment\单相流\\r006'
# PARTICLE_PLY_DIR = 'D:\c-disk-data\Desktop\毕业设计\Graduation-Experment\单相流\\r005'
# PARTICLE_PLY_DIR = 'D:\c-disk-data\Desktop\毕业设计\Graduation-Experment\单相流\\r004'
# PARTICLE_PLY_DIR = 'D:\c-disk-data\Desktop\毕业设计\Graduation-Experment\单相流\\r003'
# PARTICLE_PLY_DIR = 'D:\c-disk-data\Desktop\毕业设计\Graduation-Experment\单相流\\r0035'
# PARTICLE_PLY_DIR = 'D:\c-disk-data\Desktop\毕业设计\Graduation-Experment\单相流\\r0025'.

# PARTICLE_PLY_DIR = 'D:\c-disk-data\Desktop\毕业设计\Graduation-Experment\单相流\\双坝r01'
# PARTICLE_PLY_DIR = 'D:\c-disk-data\Desktop\毕业设计\Graduation-Experment\单相流\\双坝r005'
# PARTICLE_PLY_DIR = 'D:\c-disk-data\Desktop\毕业设计\Graduation-Experment\单相流\\双坝2r005'
'''不混溶多相流体'''
# PARTICLE_PLY_DIR = 'D:\c-disk-data\Desktop\毕业设计\Graduation-Experment\不混溶多相流\\r010'
# PARTICLE_PLY_DIR = 'D:\c-disk-data\Desktop\毕业设计\Graduation-Experment\不混溶多相流\\r009'
# PARTICLE_PLY_DIR = 'D:\c-disk-data\Desktop\毕业设计\Graduation-Experment\不混溶多相流\\r008'
# PARTICLE_PLY_DIR = 'D:\c-disk-data\Desktop\毕业设计\Graduation-Experment\不混溶多相流\\r007'
# PARTICLE_PLY_DIR = 'D:\c-disk-data\Desktop\毕业设计\Graduation-Experment\不混溶多相流\\r006'
# PARTICLE_PLY_DIR = 'D:\c-disk-data\Desktop\毕业设计\Graduation-Experment\不混溶多相流\\r005'
# PARTICLE_PLY_DIR = 'D:\c-disk-data\Desktop\毕业设计\Graduation-Experment\不混溶多相流\\r004'
# PARTICLE_PLY_DIR = 'D:\c-disk-data\Desktop\毕业设计\Graduation-Experment\不混溶多相流\\r003'
# PARTICLE_PLY_DIR = 'D:\c-disk-data\Desktop\毕业设计\Graduation-Experment\不混溶多相流\\r0035'
# PARTICLE_PLY_DIR = 'D:\c-disk-data\Desktop\毕业设计\Graduation-Experment\不混溶多相流\\r0025'

PARTICLE_PLY_DIR = 'D:\c-disk-data\Desktop\毕业设计\Graduation-Experment\不混溶多相流\\r004可视化'
'''混溶多相流体'''

# PARTICLE_PLY_DIR = r'F:\本科毕业设计\实验\多相流仿真数据\data\r010'
# PARTICLE_PLY_DIR = r'F:\本科毕业设计\实验\多相流仿真数据\data\r009'
# PARTICLE_PLY_DIR = r'F:\本科毕业设计\实验\多相流仿真数据\data\r008'
# PARTICLE_PLY_DIR = r'F:\本科毕业设计\实验\多相流仿真数据\data\r007'
# PARTICLE_PLY_DIR = r'F:\本科毕业设计\实验\多相流仿真数据\data\r006'
PARTICLE_PLY_DIR = r'F:\本科毕业设计\实验\多相流仿真数据\data\r005'
# PARTICLE_PLY_DIR = r'F:\本科毕业设计\实验\多相流仿真数据\data\r004'
# PARTICLE_PLY_DIR = r'F:\本科毕业设计\实验\多相流仿真数据\data\r003'
# PARTICLE_PLY_DIR = r'F:\本科毕业设计\实验\多相流仿真数据\data\r0035'
camera = Camera(position=glm.vec3([ 3.19455,    -0.062028,      1.96609]), yaw=-148.6, pitch=-9.700000000000044)


# camera = Camera(glm.vec3([0.0, -0.4, 1.5]))
# camera = Camera(glm.vec3([0.0, -0.4, 2.5]))
# camera = Camera(glm.vec3([0.0, -0.75, 3.35]))
# camera = Camera(glm.vec3([0.0, -0.75, 4.0]))
# camera = Camera(glm.vec3([0.0, -0.4, 4.0]))
# camera = Camera(position=glm.vec3([3.58238,     -1.33157,   -0.0816039]), yaw=-180.79999999999987, pitch=-3.000000000000007)
# camera = Camera(position=glm.vec3([2.0337,    -0.250305,      1.78807]), yaw=-138.4000000000001, pitch=-20.500000000000004)
# camera = Camera(glm.vec3([0.0, 0.0, 6.0]))
# camera = Camera(glm.vec3([-1.51893,    -0.351282,    -0.768662]))
# camera = Camera(glm.vec3([-0.222567,   -0.0635315,     0.311827]))
# camera = Camera(glm.vec3([0.00944561,     -0.12959,    -0.665845]))
# camera = Camera(glm.vec3([-2.39164, -0.0570935, -4.8922]))

# camera = Camera(position=glm.vec3([0.47572,    -0.184467,    -0.544154]), yaw=-217.99999999999983, pitch=-46.99999999999985)
# camera = Camera(position=glm.vec3([1.5044,    -0.188685,     -1.34377]), yaw=-217.69999999999985, pitch=-25.99999999999982)
'''斜着看单一飞溅粒子 i = 315 r005混溶多相流 r=0.05*1.4'''
i = 315
# camera = Camera(position=glm.vec3([0.46761,    -0.211056,    -0.544868]), yaw=-223.29999999999984, pitch=-40.19999999999981)
'''垂直向下看单一飞溅粒子'''
# camera = Camera(position=glm.vec3([0.0873681,    -0.102423,    -0.498577]), yaw=-270.3000000000003, pitch=-76.00000000000001)
# camera = Camera(position=glm.vec3([0.48324,   -0.0317409,    -0.589103]), yaw=-235.29999999999978, pitch=-68.09999999999984)
'''掠射看'''
# camera = Camera(position=glm.vec3([1.53052,    -0.858172,      0.24197]), yaw=-188.79999999999984, pitch=-1.8999999999998018)
'''差分法向量'''
# camera = Camera(position=glm.vec3([1.03295,    -0.884342,    -0.345068]), yaw=-221.19999999999956, pitch=-18.499999999999805)
# camera = Camera(position=glm.vec3([0.969983,    -0.899016,    -0.345484]), yaw=-178.89999999999978, pitch=-11.399999999999798)
'''法向量重建效果'''
# camera = Camera(position=glm.vec3([2.77292,     0.275244,     -2.51193]), yaw=-221.8999999999996, pitch=-19.299999999999756)
'''菲涅尔现象'''
# camera = Camera(position=glm.vec3([0.0375937,    -0.721166,      2.10372]), yaw=-90.10000000000004, pitch=0.6000000000000063)
# camera = Camera(position=glm.vec3([-2.26477,    -0.322368,      2.37549]), yaw=-46.39999999999997, pitch=-3.9999999999999916)
'''仰视'''
# camera = Camera(position=glm.vec3([-0.0235366,     -5.07381,     0.411799]), yaw=-90.39999999999996, pitch=84.60000000000005)
'''俯视'''
# camera = Camera(position=glm.vec3([-0.0225242,     3.53975,     0.266791]), yaw=-89.60000000000002, pitch=-84.6000000000001)
'''组会演示'''
# camera = Camera(position=glm.vec3([0.0463156,    -0.412788,      3.37289]), yaw=-92.20000000000007, pitch=-15.200000000000008)


'''多相流体管线---------------------------------------------------------------------'''
# PARTICLE_PLY_DIR = 'E:\data\\r0035'
# # PARTICLE_PLY_DIR = r'D:\XYH\论文实验\本科毕业设计\多相流\两相溃坝\r005'
# PARTICLE_PLY_DIR = r'D:\XYH\论文实验\本科毕业设计\多相流\两相溃坝\r004'
# # PARTICLE_PLY_DIR = r'D:\XYH\论文实验\本科毕业设计\多相流\两相溃坝\testr005'
# # PARTICLE_PLY_DIR = r'D:\XYH\论文实验\本科毕业设计\多相流\不混溶两相溃坝\r005'
# PARTICLE_PLY_DIR = r'D:\XYH\论文实验\本科毕业设计\多相流\不混溶两相溃坝\r004'
# num_files = len([f for f in os.listdir(PARTICLE_PLY_DIR)if os.path.isfile(os.path.join(PARTICLE_PLY_DIR, f))])
# camera = Camera(position=glm.vec3([-2.29399,    -0.171017,     -1.17689]), yaw=27.10000000000001, pitch=-18.8)
# camera = Camera(position=glm.vec3([-1.94482,    -0.569545,      -1.3672]), yaw=33.2, pitch=-6.600000000000009)
i = 0
'''---------------------------------------------------------------------------------'''
'''多相-四相混溶'''
# PARTICLE_PLY_DIR = r'D:\XYH\论文实验\本科毕业设计\多相流\多相\四相混溶\r005'
# PARTICLE_PLY_DIR = r'D:\XYH\论文实验\本科毕业设计\多相流\多相\四相混溶\r005-dt4'
# PARTICLE_PLY_DIR = r'D:\XYH\论文实验\本科毕业设计\多相流\多相\四相混溶\r004-dt4'
PARTICLE_PLY_DIR = r'D:\XYH\论文实验\本科毕业设计\多相流\多相\四相不混溶\r004-dt4'
# PARTICLE_PLY_DIR = r'D:\XYH\论文实验\本科毕业设计\多相流\多相\四相混溶\r004-dt4-v2'
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

'''---------------------------------------------------------------------------------'''

'''pbd'''
# camera = Camera(glm.vec3([-20.0, 0.0, 50.0]))
# PARTICLE_PLY_DIR = r'E:\code\AI3D\AI3D\physika\out\build\x64-Debug\examples\granular_particle\ply'

# print(PARTICLE_PLY_DIR)
# num_files = len([f for f in os.listdir(PARTICLE_PLY_DIR)if os.path.isfile(os.path.join(PARTICLE_PLY_DIR, f))])

'''---------------------------------------------------------------------------------'''

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
render_start  = 10
# render_start  = 100
# render_start  = 150
render_num  = render_start + 89

fluid_rendere = Renderer(camera)

i = 0
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
save_img_dir = r'D:\XYH\论文实验\本科毕业设计\保存图片\四相溃坝\混溶\r004-dt4-v2'
save_img_dir = r'D:\XYH\论文实验\本科毕业设计\保存图片\四相溃坝\不混溶\r004-dt4'
save_img_dir = r'D:\XYH\论文实验\本科毕业设计\保存图片\两相\混溶\r003'
save_img_dir = r'D:\XYH\论文实验\本科毕业设计\保存图片\两相\小水块掉落大水块\不混溶\r004-dt4'
save_img_dir = r'D:\XYH\论文实验\本科毕业设计\保存图片\两相\小水块掉落大水块\混溶\r004-dt4'
save_img_dir = r'D:\XYH\论文实验\本科毕业设计\保存图片\渲染管线\四相混溶'
save_img_dir = r'D:\XYH\论文实验\本科毕业设计\保存图片\易用性实验'
save_flag = False
if not os.path.exists(save_img_dir):
    os.makedirs(save_img_dir)

k_fluid = [1, 2, 3, 4]
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
        i += 1
        # fluid_rendere.save_frame_img(save_img_dir)
        if save_flag and i == 200:
            fluid_rendere.save_frame_img(save_img_dir, i)
            save_flag = False
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
    #     read_time         += fluid_rendere.read_time
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
