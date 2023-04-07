import math
import platform
from ctypes import c_float, c_void_p, sizeof

import glfw
import glm
import numpy as np
import open3d as o3d
import OpenGL.GL as gl

from fluid_render.include.buffers import VertexBuffer
from fluid_render.include.camera import Camera, CameraMovement
from fluid_render.include.shader import Shader
from fluid_render.include.static_vertices import skybox_faces, skybox_vertices
from fluid_render.include.texture import load_cubemap

WINDOW_WIDTH  = 800
WINDOW_HEIGHT = 600

class Renderer:
    """粒子渲染器, 可选渲染天空盒, 粒子地面, 待扩展GUI以及SSF(Screen Space Fluid Rendering)"""

    def __init__(self, camera:Camera) -> None:
        """渲染器变量定义, 具体变量实现通过调用 __init方法"""
        # window---------------------------------------------------------------------------------------
        self.m_width  = None
        self.m_height = None
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
        self.m_camera = None

        # object will be rendered----------------------------------------------------------------------
        """
            要渲染的对象, 存储对应的vao, vbo, 以及shader
            :粒子(流体): 必须
            :天空盒    : 可选
            :粒子底面  : 可选
        """
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
            天空盒(可选)
        """
        self.m_skybox_draw_flag = None
        self.m_skybox_vao       = None
        self.m_skybox_vbo       = None
        self.m_skybox_shader    = None
        self.m_skybox_texture   = None
        # 3.Ground
        """
            粒子底部图片(可选)
        """
        self.m_ground_draw_flag = None
        self.m_ground_vao       = None
        self.m_ground_vbo       = None
        self.m_ground_shader    = None
        # 4.fluid particle surface
        """
            通过SSF将提取从粒子数据中提取流体表面进行渲染
            首先渲染粒子表面的深度信息到深度纹理
            其次渲染厚度信息到厚度纹理
            再次根据深度纹理重建法线信息到法线纹理
            最后根据深度纹理、厚度纹理、法线纹理对物体进行着色
            需要4个shader, 专门写一个SSF渲染器进行保存
        """
        self.m_ssf_fluid_draw_flag = None
        self.m_ssf_renderer        = None

        self.__init(camera)


    def __init(self, camera:Camera):
        """渲染器变量初始化"""
        # window---------------------------------------------------------------------------------------
        self.m_width  = WINDOW_WIDTH
        self.m_height = WINDOW_HEIGHT
            # glfw 初始化
        if not glfw.init():
            raise ValueError("Failed to initialize glfw")

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        if platform.system() == 'Darwin':   # macOS平台
            glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

        self.m_window = glfw.create_window(self.m_width, self.m_height, "Fluid", None, None)
        if not self.m_window:
            glfw.terminate()
            raise ValueError("Failed to create window")
        glfw.make_context_current(self.m_window)

        # camera---------------------------------------------------------------------------------------
        self.m_camera = camera

        self.__bind()

        # object will be rendered----------------------------------------------------------------------
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
        self.m_skybox_draw_flag = True
        self.m_skybox_vao       = gl.glGenVertexArrays(1)
        self.m_skybox_vbo       = VertexBuffer(data=skybox_vertices)
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

    def render(self, path:str):
        """渲染一帧
        
        :param str: 包含一帧粒子数据的ply文件路径
        """
        # 读取并绑定粒子数据
        vertices = read_ply(path)
        self.m_particle_num = len(vertices) // 3
        gl.glBindVertexArray(self.m_particle_vao)
        self.m_particle_vbo.set_vbo_data(data=vertices)
        self.m_particle_vbo.bind()
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 3 * sizeof(c_float), c_void_p(0))
        gl.glBindVertexArray(0)
        if not glfw.window_should_close(self.m_window):
            self.__process_input(self.m_window)
            self.__render()
        else:
            self.__delete()
            self.m_exit = True
            glfw.terminate()

        glfw.swap_buffers(self.m_window)
        glfw.poll_events()
        
    def __render(self):
        """渲染一帧, OpenGL相关"""
        # 设置opengl参数
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glClearColor(0.2, 0.3, 0.3, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        # 得到变换矩阵
        model      = glm.mat4(1.0)
        view       = self.m_camera.get_view_matrix()
        # TODO:将projection也封装成camera的一个函数, 不过camrea需要添加aspect 以及 near far参数(感觉不太合适, 因为这些是平截头体的参数)
        projection = glm.perspective(glm.radians(self.m_camera.get_zoom()), self.m_width / self.m_height, 0.1, 100.0)

        # print(model, view, projection)

        # 先渲染粒子或者流体数据
        if not self.m_ssf_fluid_draw_flag:
            self.m_particle_shader.use()
            self.m_particle_shader.set_mat4('model', model)
            self.m_particle_shader.set_mat4('view', view)
            self.m_particle_shader.set_mat4('projection', projection)
            # 根据相似三角形计算粒子在屏幕空间的缩放比例
            zoom = self.m_camera.get_zoom()
            screen_space_point_z = self.m_height / math.tan(glm.radians(zoom))
            print(screen_space_point_z)
            # TODO: 可能需要一个保存静态常数的文件, 存储诸如粒子半径等信息
            point_radius = 0.075
            self.m_particle_shader.set_float('pointRadius', point_radius)
            self.m_particle_shader.set_float('screenPointZ', screen_space_point_z)
            gl.glBindVertexArray(self.m_particle_vao)
            gl.glDrawArrays(gl.GL_POINTS, 0, self.m_particle_num)
        else:
            # TODO: 完成SSF渲染
            pass

        if self.m_skybox_draw_flag:
            # 天空盒是以摄像机为中心的，这样不论摄像机移动了多远，天空盒都不会变近, 即移除view矩阵的位移部分
            skybox_view = glm.mat4(glm.mat3(view))
            self.m_skybox_shader.use()
            self.m_skybox_shader.set_mat4('view', skybox_view)
            self.m_skybox_shader.set_mat4('projection', projection)
            # 最后渲染天空盒, 在vertex shader中处理天空盒的深度值为1, 即最大, 深度测试时设置片段深度小于或者等于缓冲区时通过测试
            gl.glDepthFunc(gl.GL_LEQUAL)
            gl.glBindVertexArray(self.m_skybox_vao)
            gl.glActiveTexture(gl.GL_TEXTURE0)
            gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.m_skybox_texture)
            gl.glDrawArrays(gl.GL_TRIANGLES, 0, 36)
            gl.glDepthFunc(gl.GL_LESS)


    def __bind(self):
        glfw.set_window_size_callback(self.m_window, self.__framebuffer_size_callback)
        # glfw.set_cursor_pos_callback(self.m_window, self.__mouse_callback)
        glfw.set_scroll_callback(self.m_window, self.__scroll_callback)

        # tell GLFW to capture our mouse
        glfw.set_input_mode(self.m_window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    def __process_input(self, window):
        if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(window, True)

        # if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        #     self.camera.process_keyboard(CameraMovement.FORWARD, delta_time)
        # if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        #     self.camera.process_keyboard(CameraMovement.BACKWARD, delta_time)

        # if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        #     self.camera.process_keyboard(CameraMovement.LEFT, delta_time)
        # if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        #     self.camera.process_keyboard(CameraMovement.RIGHT, delta_time)


    def __framebuffer_size_callback(self, window, width, height):
        self.m_width  = width
        self.m_height = height
        gl.glViewport(0, 0, width, height)


    # def __mouse_callback(self, window, xpos, ypos):
    #     global first_mouse, last_x, last_y

    #     if first_mouse:
    #         last_x, last_y = xpos, ypos
    #         first_mouse = False

    #     xoffset = xpos - last_x
    #     yoffset = last_y - ypos  # XXX Note Reversed (y-coordinates go from bottom to top)
    #     last_x = xpos
    #     last_y = ypos

    #     self.camera.process_mouse_movement(xoffset, yoffset)


    def __scroll_callback(self, window, xoffset, yoffset):
        self.m_camera.process_mouse_scroll(yoffset)

    def __delete(self):
        """释放显存资源"""
        pass
        # vao
        # if self.m_particle_vao:
        #     gl.glDeleteVertexArrays(1, id(self.m_particle_vao))
        # if self.m_skybox_vao:
        #     gl.glDeleteVertexArrays(1, id(self.m_particle_vao))
        # if self.m_ground_vao:
        #     gl.glDeleteVertexArrays(1, id(self.m_particle_vao))
        # vbo
        # if self.m_particle_vbo:
        #     self.m_particle_vbo.delete()
        # if self.m_skybox_vbo:
        #     self.m_skybox_vbo.delete()
        # if self.m_ground_vbo:
        #     self.m_ground_vbo.delete()
        # shader

        # framebuffer

    def exit(self):
        return self.m_exit

def read_ply(path: str)->np.ndarray:
    """读取ply文件包含的粒子数据到ndarry中

    :param path: 文件路径
    :return: 包含粒子位置的ndarry
    """
    pcd = o3d.io.read_point_cloud(path)
    vertices = np.asarray(pcd.points, dtype=np.float32).ravel()
    return vertices
