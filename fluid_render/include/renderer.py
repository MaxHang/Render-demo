import math
import os
import platform
from ctypes import c_float, c_int, c_void_p, sizeof

import glfw
import glm
import numpy as np
import OpenGL.GL as gl
import PIL.Image as Image
import time
from plyfile import PlyData, PlyElement

from fluid_render.include.buffers import VertexBuffer
from fluid_render.include.camera import Camera, CameraMovement
from fluid_render.include.gui_params import ShaderOption
from fluid_render.include.shader import Shader
from fluid_render.include.ssf_renderer import SSFRenderer
from fluid_render.include.static_variable import far, near, particle_radius, skybox_faces, skybox_vertices, lamp_vertices, ground_vertices
from fluid_render.include.texture import load_cubemap, load_texture_2D, create_texture_2D

'''渲染管线'''
WINDOW_WIDTH  = 600
WINDOW_HEIGHT = 480

WINDOW_WIDTH  = 1000
WINDOW_HEIGHT = 800


# WINDOW_WIDTH  = 840
# WINDOW_HEIGHT = 720
# WINDOW_WIDTH  = 1200
# WINDOW_HEIGHT = 1000
# WINDOW_WIDTH  = 720
# WINDOW_HEIGHT = 480
# WINDOW_WIDTH  = 1280
# WINDOW_HEIGHT = 800
# WINDOW_WIDTH  = 1920
# WINDOW_HEIGHT = 1080
# WINDOW_WIDTH  = 2160
# WINDOW_HEIGHT = 1440

class Renderer:
    """粒子渲染器, 可选渲染天空盒, 粒子地面, 待扩展GUI以及SSF(Screen Space Fluid Rendering)"""

    def __init__(self, camera:Camera, light=None) -> None:
        """渲染器变量定义, 具体变量实现通过调用 __init方法"""
        # window---------------------------------------------------------------------------------------
        self.m_width  = WINDOW_WIDTH
        self.m_height = WINDOW_HEIGHT

        self.m_window = None
        self.m_exit   = None

        # GUI
        """
            TODO:
            添加gui
            imgui
            nanogui
        """

        # camera---------------------------------------------------------------------------------------
        self.m_camera = camera

        # 变换矩阵
        self.m_model      = None
        self.m_view       = None
        self.m_projection = None

        # light----------------------------------------------------------------------------------------
        # self.m_light = light

        # object will be rendered----------------------------------------------------------------------
        """
            要渲染的对象, 存储对应的vao, vbo, 以及shader
            :粒子(SSF) : 必须
            :天空盒    : 可选
            :粒子底面  : 可选
            :灯        : 可选
        """
        self.m_skybox_draw_flag    = True
        self.m_lamp_draw_flag      = False
        self.m_ground_draw_flag    = False
        self.m_ssf_fluid_draw_flag = True
        # backGround
        self.m_back_ground_fbo     = None
        self.m_back_ground_texture = None
        self.m_back_ground_depth   = None
        self.test_shader           = None
        # 1.particle
        """
            粒子, 需要位置、大小信息(必须, 大小设置为0.075), 密度, 速度等(可选)
        """
        self.m_particle_num    = None
        self.m_particle_vao    = None
        self.m_particle_vbo    = None
        self.m_particle_shader = None
        # 2.SkyBox
        """
            天空盒
        """
        self.m_skybox_vao       = None
        self.m_skybox_vbo       = None
        self.m_skybox_shader    = None
        self.m_skybox_texture   = None
        # 3.Ground
        """
            粒子底部图片
        """
        self.m_ground_vao       = None
        self.m_ground_shader    = None
        self.m_ground_texture   = None
        # 灯
        """灯"""
        self.m_lamp_vao         = None
        self.m_lamp_shader      = None
        # 4.fluid particle surface
        """
            通过SSF将提取从粒子数据中提取流体表面进行渲染
            首先渲染粒子表面的深度信息到深度纹理
            其次渲染厚度信息到厚度纹理
            再次根据深度纹理重建法线信息到法线纹理
            最后根据深度纹理、厚度纹理、法线纹理对物体进行着色
            需要4个shader, 专门写一个SSF渲染器进行保存
        """
        self.m_ssf_renderer        = None
        # frame related parameters
        """回调事件相关参数
        
        :delta_time: 渲染上一帧所用的时间
        :pre_frame_time: 上一帧的时间
        :pre_x
        :pre_y: 上一帧的鼠标位置
        :first_mouse: 是否是第一次获取鼠标输入
        """
        self.delta_time     = None
        self.pre_frame_time = None
        self.pre_x          = None
        self.pre_y          = None
        self.first_mouse    = None

        self.particle_data_time = None
        self._render_time = None
        self.render_time = None
        self.read_time  = None
        self.ssf_time   = None

        self.m_current_frame_number = 0

        '''OpenGL的查询机制,这里用于时间戳的查询, 用来获取指令运行的时长'''
        # self.queries         = None
        # self.ssf_time_buf    = None
        # self.render_time_buf = None

        self.__init()


    def __init(self):
        """渲染器变量初始化"""
        # window---------------------------------------------------------------------------------------
        # if not glfw.init():
        #     raise ValueError("Failed to initialize glfw")
        glfw.init()
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        if platform.system() == 'Darwin':   # macOS平台
            glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

        self.m_window = glfw.create_window(self.m_width, self.m_height, "Fluid", None, None)
        if not self.m_window:
            self.m_exit = True
            glfw.terminate()
            raise ValueError("Failed to create window")
        glfw.make_context_current(self.m_window)

        glfw.set_window_pos(self.m_window, 100, 100)
        # 绑定回调函数
        self.__bind()

        # object will be rendered----------------------------------------------------------------------
        # backGround
        self.m_back_ground_fbo     = gl.glGenFramebuffers(1)
        self.m_back_ground_depth  = create_texture_2D(
            internal_format=gl.GL_DEPTH_COMPONENT,
            width=self.m_width,
            height=self.m_height,
            src_format=gl.GL_DEPTH_COMPONENT,
            src_data_type=gl.GL_FLOAT
        )
        self.m_back_ground_texture = create_texture_2D(
            internal_format=gl.GL_RGB32F,
            width=self.m_width,
            height=self.m_height,
            src_format=gl.GL_RGB,
            src_data_type=gl.GL_FLOAT
        )
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.m_back_ground_fbo)
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_DEPTH_ATTACHMENT,  gl.GL_TEXTURE_2D, self.m_back_ground_depth, 0)
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, self.m_back_ground_texture, 0)  
        if (gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER) != gl.GL_FRAMEBUFFER_COMPLETE):
            raise RuntimeError("ERROR.FRAMEBUFFER. Framebuffer is not complete!")
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        self.test_shader = Shader('back_ground_test.vs', 'back_ground_test.fs')
        # 1.particle
        self.m_particle_num = 0
        self.m_particle_vao = gl.glGenVertexArrays(1)
        # self.m_particle_vbo = VertexBuffer()
        self.m_particle_vbo = VertexBuffer()
        """从fluid_render文件夹下的shader文件夹中读取"""
        self.m_particle_shader = Shader('particle.vs', 'particle.fs')
        # 设置可以在shader中更改点精灵大小
        gl.glEnable(gl.GL_PROGRAM_POINT_SIZE)
        # 2.SkyBox
        """
        顶点数据以及面数据从static_vertices.py读取
        TODO:
            要么把VAO也封装成类, 要么把vbo也设置为缓存指针而不是类
        """
        self.m_skybox_vao = gl.glGenVertexArrays(1)
        self.m_skybox_vbo = VertexBuffer(data=skybox_vertices)
        gl.glBindVertexArray(self.m_skybox_vao)
        self.m_skybox_vbo.bind()
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 3 * sizeof(c_float), c_void_p(0))
        gl.glEnableVertexAttribArray(0)
        self.m_skybox_vbo.unbind()
        gl.glBindVertexArray(0)
        """从fluid_render文件夹下的shader文件夹中读取, TODO:可以提取出fluid_render/shader/"""
        self.m_skybox_shader  = Shader('skybox.vs', 'skybox.fs')
        self.m_skybox_texture = load_cubemap(skybox_faces)
        self.m_skybox_shader.use()
        self.m_skybox_shader.set_int('skybox', 0)
        # 3.ground
        self.m_ground_vao     = gl.glGenVertexArrays(1)
        ground_vbo            = VertexBuffer(data=ground_vertices)
        gl.glBindVertexArray(self.m_ground_vao)
        ground_vbo.bind()
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 5 * sizeof(c_float), c_void_p(0))
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, 5 * sizeof(c_float), c_void_p(3 * sizeof(c_float)))
        gl.glEnableVertexAttribArray(1)
        gl.glBindVertexArray(0)
        self.m_ground_shader  = Shader('ground.vs', 'ground.fs')
        # self.m_ground_texture = load_texture_2D('white.jpg')
        # self.m_ground_texture = load_texture_2D('stone2.jpg')
        # self.m_ground_texture = load_texture_2D('stone3.jpg')
        self.m_ground_texture = load_texture_2D('wood.jpg')
        # self.m_ground_texture = load_texture_2D('blue_marble.png')
        # self.m_ground_texture = load_texture_2D('marble.jpg')
        self.m_ground_shader.use()
        self.m_ground_shader.set_int('groundTexture', 0)
        # 灯
        self.m_lamp_vao = gl.glGenVertexArrays(1)
        lamp_vbo        = VertexBuffer(data=lamp_vertices)
        gl.glBindVertexArray(self.m_lamp_vao)
        lamp_vbo.bind()
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 3 * sizeof(c_float), c_void_p(0))
        gl.glEnableVertexAttribArray(0)
        lamp_vbo.unbind()
        gl.glBindVertexArray(0)
        self.m_lamp_shader = Shader('lamp.vs', 'lamp.fs')
        # 4.SSF
        self.m_ssf_renderer = SSFRenderer(self.m_width, self.m_height, self.m_camera, self.m_skybox_texture)
        # frame related params
        self.delta_time     = 0.0
        self.pre_frame_time = 0.0
        self.pre_x          = 0.0
        self.pre_y          = 0.0
        self.first_mouse    = True

        '''OpenGL查询'''
        # self.queries         = gl.glGenQueries(1)
        # self.ssf_time_buf    = (c_int * 1)(*[0])
        # self.render_time_buf = (c_int * 1)(*[0])

    def render(self, path:str):
        """渲染一帧
        
        :param path: 包含一帧粒子数据的ply文件路径
        """
        self.m_current_frame_number += 1
        # 读取并绑定粒子数据
        read_start = time.perf_counter()
        vertices, vertices_stride = read_ply(path, self.m_ssf_renderer.m_shader_option)
        self.read_time = time.perf_counter() - read_start

        # particle_data_start = time.perf_counter()
        self.m_particle_num = len(vertices) // vertices_stride
        self.m_particle_vbo.set_vbo_data(data=vertices)
        gl.glBindVertexArray(self.m_particle_vao)
        self.m_particle_vbo.bind()
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, vertices_stride * sizeof(c_float), c_void_p(0))
        if vertices_stride > 3:
            gl.glEnableVertexAttribArray(1)
            gl.glVertexAttribPointer(1, vertices_stride - 3, gl.GL_FLOAT, gl.GL_FALSE, vertices_stride * sizeof(c_float), c_void_p(3 * sizeof(c_float)))
        gl.glBindVertexArray(0)
        # self.particle_data_time = time.perf_counter() - particle_data_start
    
        render_start = time.perf_counter()
        if not glfw.window_should_close(self.m_window):
            self.__process_input(self.m_window)
            # _render_start = time.perf_counter()
            self.__render()
            # self._render_time = time.perf_counter() - _render_start
        else:
            self.__delete()
            self.m_exit = True
            glfw.terminate()
        self.render_time = time.perf_counter() - render_start
        glfw.swap_buffers(self.m_window)
        glfw.poll_events()

    def __render(self):
        """渲染一帧, OpenGL相关"""
        # 得到变换矩阵
        zoom = self.m_camera.get_zoom()
        self.m_model      = glm.mat4(1.0)
        self.m_view       = self.m_camera.get_view_matrix()
        self.m_projection = glm.perspective(glm.radians(zoom), self.m_width / self.m_height, near, far)
        self.m_ssf_renderer.set_matrix(self.m_model, self.m_view, self.m_projection)
        point_scale = self.m_height * (1.0 / math.tan(glm.radians(zoom)))
        # light
        # light_position = glm.vec3(1.2, 1.0, 2.0)
        light_position = glm.vec3(5, 5, -5)
        diffuse  = glm.vec3(1.0, 0.5, 0.31)
        ambient  = glm.vec3(1.0, 0.5, 0.31)
        specular = glm.vec3(0.5, 0.5, 0.5)

        # 首先渲染非流体部分(即背景, 用于流体折射采样), 使用一个帧缓冲
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.m_back_ground_fbo)
        gl.glClearColor(0.2, 0.3, 0.3, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        # gl.glEnable(gl.GL_DEPTH_TEST)
        self.__render_back_ground(light_position)

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        gl.glClearColor(0.2, 0.3, 0.3, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # 测试背景
        # self.test_shader.use()
        # self.test_shader.set_int('screenTexture', 0)
        # gl.glDisable(gl.GL_DEPTH_TEST)
        # gl.glActiveTexture(gl.GL_TEXTURE0)
        # gl.glBindTexture(gl.GL_TEXTURE_2D, self.m_back_ground_texture)
        # gl.glBindVertexArray(self.m_ssf_renderer.m_quad_vao)
        # gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)
        

        # 渲染粒子或者流体数据
        if not self.m_ssf_fluid_draw_flag:
            self.m_particle_shader.use()
            self.m_particle_shader.set_mat4('model', self.m_model)
            self.m_particle_shader.set_mat4('view', self.m_view)
            self.m_particle_shader.set_mat4('projection', self.m_projection)
            self.m_particle_shader.set_float('particleRadius', particle_radius)
            self.m_particle_shader.set_float('pointScale', point_scale)
            # ligth
            self.m_particle_shader.set_vec3('cameraPosition', self.m_camera.get_pos())
            self.m_particle_shader.set_vec3('pointLight.positon' , light_position)
            self.m_particle_shader.set_vec3('pointLight.ambient' , diffuse)
            self.m_particle_shader.set_vec3('pointLight.diffuse' , ambient)
            self.m_particle_shader.set_vec3('pointLight.specular', specular)
            self.m_particle_shader.set_float("pointLight.constant", 1.0)
            self.m_particle_shader.set_float("pointLight.linear", 0.09)
            self.m_particle_shader.set_float("pointLight.quadratic", 0.032)

            gl.glEnable(gl.GL_DEPTH_TEST)
            gl.glBindVertexArray(self.m_particle_vao)
            gl.glDrawArrays(gl.GL_POINTS, 0, self.m_particle_num)
        else:
            ssf_start = time.perf_counter()
            self.m_ssf_renderer.render(self.m_particle_vao, self.m_particle_num, point_scale, self.m_back_ground_texture)
            self.ssf_time = time.perf_counter() - ssf_start

        # gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        # self.__render_back_ground(light_position)

    def __render_back_ground(self, light_position:glm.vec3):
        """绘制背景"""
        if self.m_lamp_draw_flag:
            lamp_model = glm.translate(light_position)
            lamp_model = glm.scale(lamp_model, [0.2, 0.2, 0.2])
            self.m_lamp_shader.use()
            self.m_lamp_shader.set_mat4('model', lamp_model)
            self.m_lamp_shader.set_mat4('view', self.m_view)
            self.m_lamp_shader.set_mat4('projection', self.m_projection)
            gl.glEnable(gl.GL_DEPTH_TEST)
            gl.glBindVertexArray(self.m_lamp_vao)
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, 36)

        if self.m_ground_draw_flag:
            self.m_ground_shader.use()
            self.m_ground_shader.set_mat4('model', self.m_model)
            self.m_ground_shader.set_mat4('view', self.m_view)
            self.m_ground_shader.set_mat4('projection', self.m_projection)
            gl.glEnable(gl.GL_DEPTH_TEST)
            gl.glBindVertexArray(self.m_ground_vao)
            gl.glActiveTexture(gl.GL_TEXTURE0)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.m_ground_texture)
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)

        if self.m_skybox_draw_flag:
            # 天空盒是以摄像机为中心的，这样不论摄像机移动了多远，天空盒都不会变近, 即移除view矩阵的位移部分
            skybox_view = glm.mat4(glm.mat3(self.m_view))
            self.m_skybox_shader.use()
            self.m_skybox_shader.set_mat4('view', skybox_view)
            self.m_skybox_shader.set_mat4('projection', self.m_projection)
            # 最后渲染天空盒, 在vertex shader中处理天空盒的深度值为1, 即最大, 深度测试时设置片段深度小于或者等于缓冲区时通过测试
            gl.glEnable(gl.GL_DEPTH_TEST)
            gl.glDepthFunc(gl.GL_LEQUAL)
            gl.glBindVertexArray(self.m_skybox_vao)
            gl.glActiveTexture(gl.GL_TEXTURE0)
            gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.m_skybox_texture)
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, 36)
            gl.glDepthFunc(gl.GL_LESS)
    
    def __bind(self):
        glfw.set_window_size_callback(self.m_window, self.__framebuffer_size_callback)
        glfw.set_cursor_pos_callback(self.m_window, self.__mouse_callback)
        glfw.set_scroll_callback(self.m_window, self.__scroll_callback)

        # tell GLFW to capture our mouse
        glfw.set_input_mode(self.m_window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    def __process_input(self, window):
        if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(window, True)

        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
            self.m_camera.process_keyboard(CameraMovement.FORWARD, self.delta_time)
        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
            self.m_camera.process_keyboard(CameraMovement.BACKWARD, self.delta_time)

        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
            self.m_camera.process_keyboard(CameraMovement.LEFT, self.delta_time)
        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
            self.m_camera.process_keyboard(CameraMovement.RIGHT, self.delta_time)


    def __framebuffer_size_callback(self, window, width, height):
        self.m_width  = width
        self.m_height = height
        
        gl.glViewport(0, 0, width, height)


    def __mouse_callback(self, window, xpos, ypos):
        if self.first_mouse:
            self.pre_x, self.pre_y = xpos, ypos
            self.first_mouse = False

        xoffset = xpos - self.pre_x
        yoffset = self.pre_y - ypos  # XXX Note Reversed (y-coordinates go from bottom to top)
        self.pre_x = xpos
        self.pre_y = ypos

        self.m_camera.process_mouse_movement(xoffset, yoffset)


    def __scroll_callback(self, window, xoffset, yoffset):
        self.m_camera.process_mouse_scroll(yoffset)

    def __delete(self):
        """释放显存资源"""
        # vao
        if self.m_particle_vao:
            gl.glDeleteVertexArrays(1, id(self.m_particle_vao))
        if self.m_skybox_vao:
            gl.glDeleteVertexArrays(1, id(self.m_skybox_vao))
        if self.m_ground_vao:
            gl.glDeleteVertexArrays(1, id(self.m_ground_vao))
        # vbo
        if self.m_particle_vbo:
            self.m_particle_vbo.delete()
        if self.m_skybox_vbo:
            self.m_skybox_vbo.delete()
        # shader

        # framebuffer

    def set_frame_params(self):
        cur_frame_time = glfw.get_time()
        self.delta_time = cur_frame_time - self.pre_frame_time
        self.pre_frame_time = cur_frame_time
        # print(f'上一帧用用时:{self.delta_time}')

    def get_delta_time(self):
        """返回上一帧渲染时间"""
        return self.delta_time

    def exit(self):
        return self.m_exit

    def print_window_size(self):
        print(f"width{self.m_width}, height{self.m_height}")

    def save_frame_img(self, save_dir: str, frame_number: int):
        if self.exit():
            return
        """保存当前帧图像"""
        shader_option_file_prefix_dict = {
            ShaderOption.Depth: 'depth_',
            ShaderOption.Thick: 'thcik_',
            ShaderOption.MultiFrac: 'frac_',
            ShaderOption.Normal: 'normal_',
            ShaderOption.Attenuation: 'attenuation_',
            ShaderOption.MultiAttenuation: 'attenuation_',
        }
        file_prefix = shader_option_file_prefix_dict.get(self.m_ssf_renderer.m_shader_option, '')
        if self.m_ssf_renderer.m_iterations > 0 and self.m_ssf_renderer.m_shader_option in [ShaderOption.Depth, ShaderOption.Thick, ShaderOption.MultiFrac]:
            file_prefix = 'smooth_' + file_prefix
        if not self.m_ssf_fluid_draw_flag:
            file_prefix = 'particle_'
        data = gl.glReadPixels(0, 0, self.m_width, self.m_height, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE)
        image = Image.frombytes("RGBA", (self.m_width, self.m_height), data)

        # 在读取之后，图像可能是上下颠倒的，需要翻转
        image = image.transpose(Image.FLIP_TOP_BOTTOM)

        # 保存图像
        image.save(os.path.join(save_dir, file_prefix + 'frame_%d.png'%frame_number))

        print('保存第%d帧'%frame_number)

def read_ply(path:str, shader_option:ShaderOption):
    """读取ply文件包含的粒子数据到ndarry中

    :param path: 文件路径

    :return: 包含粒子位置以及 多相流 粒子的流相比例 的ndarray
    """
    with open(path, 'rb') as f:
        plydata = PlyData.read(f)
    # vertices_stride = len(plydata['vertex'].properties)
    properties = [property.name for property in plydata['vertex'].properties]
    if shader_option in [ShaderOption.MultiFluid, ShaderOption.MultiFrac, ShaderOption.MultiAttenuation, ShaderOption.MultiRefract]:
        vertices_data = [
            plydata['vertex']['x'], 
            plydata['vertex']['y'], 
            plydata['vertex']['z'],
        ]
        vertices_stride = 7
        num_vertices = len(plydata['vertex']['x'])  # 获取顶点数量
        for i in range(1, 5):
            if f'fluid{i}_frac' in properties:
                vertices_data.append(plydata['vertex'][f'fluid{i}_frac'])
            else:
                # 如果fluid{i}_frac不在properties中，添加一个由0组成的数组
                vertices_data.append(np.zeros(num_vertices, dtype=np.float32))
        vertices = np.asarray(vertices_data, dtype=np.float32).T.ravel()
    else:
        vertices = np.asarray([
            plydata['vertex']['x'], 
            plydata['vertex']['y'], 
            plydata['vertex']['z'],
            ], dtype=np.float32).T.ravel()
        vertices_stride = 3
    # vertices = np.append(vertices, [0,0,2,1,0])
    # vertices = np.asarray([0,0,2,1,0],dtype=np.float32)
    # vertices_stride = 5
    return vertices, vertices_stride


# def read_ply(path:str, shader_option:ShaderOption):
#     """读取ply文件包含的粒子数据到ndarry中

#     :param path: 文件路径

#     :return: 包含粒子位置以及 多相流 粒子的流相比例 的ndarray
#     """
#     with open(path, 'rb') as f:
#         plydata = PlyData.read(f)
#     # vertices_stride = len(plydata['vertex'].properties)
#     properties = [property.name for property in plydata['vertex'].properties]
#     if shader_option in [ShaderOption.MultiFluid, ShaderOption.MultiFrac, ShaderOption.MultiAttenuation, ShaderOption.MultiRefract]:
#         vertices_data = [
#             plydata['vertex']['x'], 
#             plydata['vertex']['y'], 
#             plydata['vertex']['z'],
#         ]
#         vertices_stride = 3
#         num_vertices = len(plydata['vertex']['x'])  # 获取顶点数量
#         for i in range(1, 5):
#             if f'fluid{i}_frac' in properties:
#                 vertices_stride += 1
#                 vertices_data.append(plydata['vertex'][f'fluid{i}_frac'])
#             else:
#                 break
#         vertices = np.asarray(vertices_data, dtype=np.float32).T.ravel()
#     else:
#         vertices = np.asarray([
#             plydata['vertex']['x'], 
#             plydata['vertex']['y'], 
#             plydata['vertex']['z'],
#             ], dtype=np.float32).T.ravel()
#         vertices_stride = 3
#     return vertices, vertices_stride