from ctypes import c_float, c_uint32, c_void_p, sizeof

import glm
import OpenGL.GL as gl

from fluid_render.include.buffers import VertexBuffer
from fluid_render.include.camera import Camera
from fluid_render.include.gui_params import SmoothOption, ShaderOption, filter_size
from fluid_render.include.shader import Shader
from fluid_render.include.static_variable import far, near, R0_air_to_water, refractive_index, particle_radius, quad_vertices, two_sigma_r2, two_sigma_d2, sigma_r, sigma_d, max_filter_size
from fluid_render.include.texture import create_texture_2D

class SSFRenderer:
    """屏幕空间流体(SSF)渲染, 一帧"""

    def __init__(self, width:int, height:int, camera:Camera, sky_texture:int) -> None:
        """SSF渲染器变量定义, 具体变量实现通过调用 __init方法
        
        :param      camera: 摄像机
        :param       width
        :param      height: 窗口大小
        :param sky_texture: 天空盒纹理缓冲区的id
        """
        # 窗口大小，用于创建帧缓冲的深度、厚度等纹理附件
        self.m_width  = width
        self.m_height = height
        # camera
        self.m_camera = camera
        # 着色选择
        self.m_shader_option = ShaderOption.MultiFluid
        # 模糊选择 
        self.m_smooth_option = SmoothOption.BilateralSeperate
        # 平滑次数
        self.m_iterations    = 3
        # 天空盒
        self.m_sky_texture = sky_texture
        # 帧缓冲
        self.m_fbo = None
        # 帧缓冲纹理附件
            # 用于深度测试
        self.m_depth            = None
            # 平滑后用于重建法向量, 一个作为smooth source 一个作为 smooth target, source_ab用来判断哪个是source
        self.m_source_ab        = None
        self.m_thick_source_ab  = None
        self.m_depth_texture_a  = None
        self.m_depth_texture_b  = None
        self.m_thick_texture_a  = None
        self.m_thick_texture_b  = None
        self.m_normal_texture   = None
            # multi_fluid相关, 记录每个像素的厚度流相比
        self.m_fluid_frac_texture    = None
        # shaders 渲染到纹理附件中
        self.m_get_depth_shader      = None
        self.m_get_thick_shader      = None
            # 多相流厚度流相比shader
        self.m_get_multi_thick_shader = None
        self.m_restore_normal_shader  = None
        # shaders 光滑深度纹理 与 光滑次数
        self.m_guassian_shader           = None
        self.m_bilateral_combine_shader  = None
        self.m_bilateral_seperate_shader = None
        # 平滑厚度纹理
        self.m_thick_blur_shader         = None
        # shaders 渲染到窗口的shader
        self.m_rendering_shader = None
        # 屏幕vbo
        self.m_quad_vao    = None
        """以下信息通过渲染函数参数传递(每一帧)"""
        # 渲染的粒子vao以及数量
        self.m_particle_vao = None
        self.m_particle_num = None
        # 矩阵信息
        self.m_model      = None
        self.m_view       = None
        self.m_projcetion = None
        self.m_point_scale = None

        self.__init()

    def __init(self):
        """初始化变量"""
        # 帧缓冲纹理附件
        self.m_depth  = create_texture_2D(
            internal_format=gl.GL_DEPTH_COMPONENT,
            width=self.m_width,
            height=self.m_height,
            src_format=gl.GL_DEPTH_COMPONENT,
            src_data_type=gl.GL_FLOAT
        )
            # 用于深度平滑的纹理
        self.m_depth_texture_a = create_texture_2D(
            internal_format=gl.GL_R32F,
            width=self.m_width,
            height=self.m_height,
            src_format=gl.GL_RED,
            src_data_type=gl.GL_FLOAT
        )
        self.m_depth_texture_b = create_texture_2D(
            internal_format=gl.GL_R32F,
            width=self.m_width,
            height=self.m_height,
            src_format=gl.GL_RED,
            src_data_type=gl.GL_FLOAT
        )
        self.m_thick_texture_a = create_texture_2D(
            internal_format=gl.GL_R32F,
            width=self.m_width,
            height=self.m_height,
            src_format=gl.GL_RED,
            src_data_type=gl.GL_FLOAT
        )
        self.m_thick_texture_b = create_texture_2D(
            internal_format=gl.GL_R32F,
            width=self.m_width,
            height=self.m_height,
            src_format=gl.GL_RED,
            src_data_type=gl.GL_FLOAT
        )
        self.m_normal_texture = create_texture_2D(
            internal_format=gl.GL_RGB32F,
            width=self.m_width,
            height=self.m_height,
            src_format=gl.GL_RGB,
            src_data_type=gl.GL_FLOAT
        )
        self.m_fluid_frac_texture = create_texture_2D(
            internal_format=gl.GL_RG32F,
            width=self.m_width,
            height=self.m_height,
            src_format=gl.GL_RG,
            src_data_type=gl.GL_FLOAT
        )
        # 创建帧缓冲并且绑定纹理附件
        self.m_fbo = gl.glGenFramebuffers(1)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.m_fbo)
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_DEPTH_ATTACHMENT,  gl.GL_TEXTURE_2D, self.m_depth, 0)  
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, self.m_depth_texture_a, 0)  
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT1, gl.GL_TEXTURE_2D, self.m_normal_texture, 0)
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT2, gl.GL_TEXTURE_2D, self.m_thick_texture_a, 0)
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT3, gl.GL_TEXTURE_2D, self.m_depth_texture_b, 0)
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT4, gl.GL_TEXTURE_2D, self.m_thick_texture_b, 0)
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT5, gl.GL_TEXTURE_2D, self.m_fluid_frac_texture, 0)
        if (gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER) != gl.GL_FRAMEBUFFER_COMPLETE):
            raise RuntimeError("ERROR.FRAMEBUFFER. Framebuffer is not complete!")
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        # shaders
        self.m_get_depth_shader       = Shader('ssf_get_depth.vs', 'ssf_get_depth.fs')
        self.m_get_thick_shader       = Shader('ssf_get_thick.vs', 'ssf_get_thick.fs')
        self.m_get_multi_thick_shader = Shader('ssf_get_multi_thick.vs', 'ssf_get_multi_thick.fs')
        self.m_restore_normal_shader  = Shader('ssf_restore_normal.vs', 'ssf_restore_normal.fs')
        self.m_rendering_shader          = Shader('ssf_rendering.vs', 'ssf_rendering.fs')
        self.m_guassian_shader           = Shader('depth_guassian_blur.vs', 'depth_guassian_blur.fs')
        self.m_bilateral_combine_shader  = Shader('depth_bilateral_combine_blur.vs', 'depth_bilateral_combine_blur.fs')
        self.m_bilateral_seperate_shader = Shader('depth_bilateral_seperate_blur.vs', 'depth_bilateral_seperate_blur.fs')
        self.m_thick_blur_shader         = Shader('thickness_blur.vs', 'thickness_blur.fs')
        # 屏幕vbo
        quad_vbo = VertexBuffer(data=quad_vertices)
        self.m_quad_vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.m_quad_vao)
        quad_vbo.bind()
            # 设置位置
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 4 * sizeof(c_float), c_void_p(0))
        gl.glEnableVertexAttribArray(0)
            # 设置纹理坐标
        gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, 4 * sizeof(c_float), c_void_p(2 * sizeof(c_float)))
        gl.glEnableVertexAttribArray(1)
        gl.glBindVertexArray(0)

    def render(self, particle_vao:int, partical_num:int, point_scale:float, back_ground_texture:int):
        """SSF将粒子渲染为光滑流体"""
        self.m_particle_vao = particle_vao
        self.m_particle_num = partical_num
        self.m_point_scale = point_scale
        
        self.m_source_ab = True
        self.m_thick_source_ab = True

        self.__render_depth()
        if self.m_shader_option == ShaderOption.MultiFluid or self.m_shader_option == ShaderOption.MultiFluid2:
            self.__render_multi_thick()
        else:
            self.__render_thick()

        if self.m_smooth_option == SmoothOption.Guassian:
            for _pass in range(self.m_iterations):
                horizontal = 1
                self.__gaussian_blur(horizontal)
                horizontal = 0
                self.__gaussian_blur(horizontal)
        elif self.m_smooth_option == SmoothOption.BilateralCombine:
            for _pass in range(self.m_iterations):
                self.__bilateral_combine_blur()
        elif self.m_smooth_option == SmoothOption.BilateralSeperate:
            for _pass in range(self.m_iterations):
                blur_dir = glm.vec2(0, 1)
                self.__bilateral_seperate_blur(blur_dir)
                blur_dir = glm.vec2(1, 0)
                self.__bilateral_seperate_blur(blur_dir)
        else:
            pass

        if self.m_smooth_option != SmoothOption.Unsmooth:
            for _pass in range(10):
                blur_dir = glm.vec2(1, 0)
                self.__smooth_thickness(blur_dir)
                blur_dir = glm.vec2(0, 1)
                self.__smooth_thickness(blur_dir)

        self.__restore_normal()

        self.__render(back_ground_texture)
    
    def __render_depth(self):
        """渲染深度, 具有两个渲染对象, depth用于深度测试, depth_texture用于平滑后重建法线向量(NDC空间的值)
        """
        self.m_get_depth_shader.use()
        self.m_get_depth_shader.set_mat4('model', self.m_model)
        self.m_get_depth_shader.set_mat4('view', self.m_view)
        self.m_get_depth_shader.set_mat4('projection', self.m_projcetion)
        self.m_get_depth_shader.set_float('pointScale', self.m_point_scale)
        self.m_get_depth_shader.set_float('particleRadius', particle_radius)

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.m_fbo)
        render_buffers = [gl.GL_COLOR_ATTACHMENT0]  # 0为深度纹理
        render_buffers = (c_uint32 * len(render_buffers))(*render_buffers)
        gl.glDrawBuffers(1, render_buffers)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDisable(gl.GL_BLEND)
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)
        inf = [100.0]
        inf = (c_float * len(inf))(*inf)
        gl.glClearTexImage(self.m_depth_texture_a, 0, gl.GL_RED, gl.GL_FLOAT, inf) # 只在opengl 4.4版本以上使用

        gl.glBindVertexArray(self.m_particle_vao)
        gl.glDrawArrays(gl.GL_POINTS, 0, self.m_particle_num)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER ,0)

    def __render_thick(self):
        """渲染厚度信息到厚度纹理
           渲染时关闭深度测试, 开启混合
        """
        self.m_get_thick_shader.use()
        self.m_get_thick_shader.set_mat4('model', self.m_model)
        self.m_get_thick_shader.set_mat4('view', self.m_view)
        self.m_get_thick_shader.set_mat4('projection', self.m_projcetion)
        self.m_get_thick_shader.set_float('pointScale', self.m_point_scale)
        self.m_get_thick_shader.set_float('particleRadius', particle_radius)

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.m_fbo)
        render_buffers = [gl.GL_COLOR_ATTACHMENT2]  # 2为厚度纹理
        render_buffers = (c_uint32 * len(render_buffers))(*render_buffers)
        gl.glDrawBuffers(1, render_buffers)
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_ONE, gl.GL_ONE) # additive blending, 加法融合, 即原像素值和目标像素值直接相加
        zero = [0.0]
        zero = (c_float * len(zero))(*zero)
        gl.glClearTexImage(self.m_thick_texture_a, 0, gl.GL_RED, gl.GL_FLOAT, zero) # 只在opengl 4.4版本以上使用

        gl.glBindVertexArray(self.m_particle_vao)
        gl.glDrawArrays(gl.GL_POINTS, 0, self.m_particle_num)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

    def __render_multi_thick(self):
        """渲染多相流厚度信息到厚度纹理以及流相纹理
           渲染时关闭深度测试, 开启混合
        """
        self.m_get_multi_thick_shader.use()
        self.m_get_multi_thick_shader.set_mat4('model', self.m_model)
        self.m_get_multi_thick_shader.set_mat4('view', self.m_view)
        self.m_get_multi_thick_shader.set_mat4('projection', self.m_projcetion)
        self.m_get_multi_thick_shader.set_float('pointScale', self.m_point_scale)
        self.m_get_multi_thick_shader.set_float('particleRadius', particle_radius)

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.m_fbo)
        render_buffers = [gl.GL_COLOR_ATTACHMENT2, gl.GL_COLOR_ATTACHMENT5]  # 2为厚度纹理, 5为流相比例纹理
        render_buffers = (c_uint32 * len(render_buffers))(*render_buffers)
        gl.glDrawBuffers(2, render_buffers)
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_ONE, gl.GL_ONE) # additive blending, 加法融合, 即原像素值和目标像素值直接相加
        zero = [0.0]
        zero = (c_float * len(zero))(*zero)
        gl.glClearTexImage(self.m_thick_texture_a, 0, gl.GL_RED, gl.GL_FLOAT, zero) # 只在opengl 4.4版本以上使用
        gl.glClearTexImage(self.m_fluid_frac_texture, 0, gl.GL_RG, gl.GL_FLOAT, zero) # 只在opengl 4.4版本以上使用

        gl.glBindVertexArray(self.m_particle_vao)
        gl.glDrawArrays(gl.GL_POINTS, 0, self.m_particle_num)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

    def __gaussian_blur(self, horizontal:int):
        zoom = glm.radians(self.m_camera.get_zoom())
        self.m_guassian_shader.use()
        self.m_guassian_shader.set_int('horizontal', horizontal)
        self.m_guassian_shader.set_int('MaxFilterSize', max_filter_size)
        self.m_guassian_shader.set_int('filterSize', filter_size)
        self.m_guassian_shader.set_float('zoom', zoom)
        self.m_guassian_shader.set_float('screenHeight', self.m_height)
        self.m_guassian_shader.set_float('particleRadius', particle_radius)
        self.__smooth_depth(self.m_guassian_shader)
        self.m_source_ab = not self.m_source_ab

    def __bilateral_combine_blur(self):
        
        # self.m_bilateral_combine_shader.use()
        # self.m_bilateral_combine_shader.set_float('filterSize', filter_size)
        # self.m_bilateral_combine_shader.set_float('sigma_r', two_sigma_r2)
        # self.m_bilateral_combine_shader.set_float('sigma_d', two_sigma_d2)
        # self.__smooth_depth(self.m_bilateral_combine_shader)
        # self.m_source_ab = not self.m_source_ab
        self.m_bilateral_combine_shader.use()
        self.m_bilateral_combine_shader.set_float('filterSize', 10.0)
        self.m_bilateral_combine_shader.set_float('two_sigma_r2', 2*0.15*0.15)
        self.m_bilateral_combine_shader.set_float('two_sigma_d2', 2*6*6.0)
        self.__smooth_depth(self.m_bilateral_combine_shader)
        self.m_source_ab = not self.m_source_ab

    def __bilateral_seperate_blur(self, blur_dir:glm.vec2):
        # self.m_bilateral_seperate_shader.use()
        # self.m_bilateral_seperate_shader.set_int('filterSize', filter_size)
        # self.m_bilateral_seperate_shader.set_float('sigma_r', 0.25)
        # self.m_bilateral_seperate_shader.set_float('sigma_d', 6.0)
        # self.m_bilateral_seperate_shader.set_vec2('blur_dir', blur_dir)
        # self.__smooth_depth(self.m_bilateral_seperate_shader)
        # self.m_source_ab = not self.m_source_ab
        zoom = glm.radians(self.m_camera.get_zoom())
        self.m_bilateral_seperate_shader.use()
        self.m_bilateral_seperate_shader.set_int('MaxFilterSize', max_filter_size)
        self.m_bilateral_seperate_shader.set_int('filterSize', filter_size)
        self.m_bilateral_seperate_shader.set_float('zoom', zoom)
        self.m_bilateral_seperate_shader.set_float('screenHeight', self.m_height)
        self.m_bilateral_seperate_shader.set_float('particleRadius', particle_radius)
        self.m_bilateral_seperate_shader.set_vec2('blur_dir', blur_dir)
        self.__smooth_depth(self.m_bilateral_seperate_shader)
        self.m_source_ab = not self.m_source_ab

    def __smooth_depth(self, blur_shader:Shader):
        """平滑深度图"""
        blur_shader.use()
        blur_shader.set_int('depthTexture', 0)

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.m_fbo)
        render_buffers = [gl.GL_COLOR_ATTACHMENT3 if self.m_source_ab else gl.GL_COLOR_ATTACHMENT0]  # 0、3为深度纹理
        # render_buffers = [gl.GL_COLOR_ATTACHMENT3]  # 0、3为深度纹理
        render_buffers = (c_uint32 * len(render_buffers))(*render_buffers)
        gl.glDrawBuffers(1, render_buffers)
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glDisable(gl.GL_BLEND)
        inf = [far]
        inf = (c_float * len(inf))(*inf)
        gl.glClearTexImage(self.__get_smooth_target_texture(), 0, gl.GL_RED, gl.GL_FLOAT, inf) # 只在opengl 4.4版本以上使用
       
        gl.glBindVertexArray(self.m_quad_vao)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.__get_smooth_source_texture())
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

    def __smooth_thickness(self, blur_dir:glm.vec2):
        """平滑厚度图"""
        self.m_thick_blur_shader.use()
        self.m_thick_blur_shader.set_float('filterSize', filter_size)
        self.m_thick_blur_shader.set_vec2('blur_dir', blur_dir)
        self.m_thick_blur_shader.set_int('thcikTexture', 0)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.m_fbo)
        render_buffers = [gl.GL_COLOR_ATTACHMENT4 if self.m_thick_source_ab else gl.GL_COLOR_ATTACHMENT2]  # 2、4为厚度纹理
        render_buffers = (c_uint32 * len(render_buffers))(*render_buffers)
        gl.glDrawBuffers(1, render_buffers)
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glDisable(gl.GL_BLEND)
        inf = [0.0]
        inf = (c_float * len(inf))(*inf)
        gl.glClearTexImage(self.__get_thick_smooth_target_texture(), 0, gl.GL_RED, gl.GL_FLOAT, inf) # 只在opengl 4.4版本以上使用

        gl.glBindVertexArray(self.m_quad_vao)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.__get_thick_smooth_source_texture())
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

        self.m_thick_source_ab = not self.m_thick_source_ab
        

    def __restore_normal(self):
        """根据深度图重建每个像素对应观察空间的法向量"""
        # 获取投影矩阵的逆矩阵
        in_projection = glm.inverse(self.m_projcetion)

        self.m_restore_normal_shader.use()
        self.m_restore_normal_shader.set_mat4('inProjection', in_projection)
        self.m_restore_normal_shader.set_int('depthTexture', 0)
        self.m_restore_normal_shader.set_int('screenWidth', self.m_width)
        self.m_restore_normal_shader.set_int('screenHeight', self.m_height)
        self.m_restore_normal_shader.set_float('far', far)
        self.m_restore_normal_shader.set_float('near', near)

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.m_fbo)
        render_buffers = [gl.GL_COLOR_ATTACHMENT1]  # 1为法向纹理
        render_buffers = (c_uint32 * len(render_buffers))(*render_buffers)
        gl.glDrawBuffers(1, render_buffers)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_ALWAYS);
        gl.glDisable(gl.GL_BLEND)
        black = (0.0, 0.0, 0.0)
        black = (c_float * len(black))(*black)
        gl.glClearTexImage(self.m_normal_texture, 0, gl.GL_RGB, gl.GL_FLOAT, black) # 只在opengl 4.4版本以上使用

        gl.glBindVertexArray(self.m_quad_vao)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.__get_smooth_source_texture())
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        gl.glDepthFunc(gl.GL_LESS)

        # 将创建的帧缓冲的深度测试纹理复制到默认帧缓冲的深度测试纹理中
        gl.glBindFramebuffer(gl.GL_READ_FRAMEBUFFER, self.m_fbo)
        gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, 0) # 写人默认帧缓冲中
        gl.glBlitFramebuffer(0,0,self.m_width,self.m_height,0,0,self.m_width,self.m_height,gl.GL_DEPTH_BUFFER_BIT,gl.GL_NEAREST)

    def __render(self, back_ground_texture:int):
        """根据深度纹理、厚度纹理、法线纹理渲染流体表面
           绘制在屏幕vbo上, 由于是2D空间, 不需要深度测试以及混合
        """
        # # 将创建的帧缓冲的深度测试纹理复制到默认帧缓冲的深度测试纹理中
        # gl.glBindFramebuffer(gl.GL_READ_FRAMEBUFFER, self.m_fbo)
        # gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, 0) # 写人默认帧缓冲中
        # gl.glBlitFramebuffer(0,0,self.m_width,self.m_height,0,0,self.m_width,self.m_height,gl.GL_DEPTH_BUFFER_BIT,gl.GL_NEAREST)

        in_projection = glm.inverse(self.m_projcetion)
        # 测试uniform变量
        self.m_rendering_shader.use()
        self.m_rendering_shader.set_int('shaderOption', self.m_shader_option.value)
        self.m_rendering_shader.set_float('near', near)
        self.m_rendering_shader.set_float('far', far)
        self.m_rendering_shader.set_float('R0', R0_air_to_water)
        self.m_rendering_shader.set_float('refractiveIndex', refractive_index)
        self.m_rendering_shader.set_mat4('model', self.m_model)
        self.m_rendering_shader.set_mat4('view', self.m_view)
        self.m_rendering_shader.set_mat4('projection', self.m_projcetion)
        self.m_rendering_shader.set_mat4('inProjection', in_projection)
        self.m_rendering_shader.set_int('depthTexture', 0)
        self.m_rendering_shader.set_int('thickTexture', 1)
        self.m_rendering_shader.set_int('normalTexture', 2)
        self.m_rendering_shader.set_int('backGroundTexture', 3)
        self.m_rendering_shader.set_int('skyboxTexture', 4)
        self.m_rendering_shader.set_int('fluidFracTexture', 5)
        
        # light
        light_position = glm.vec3(5, 5, -5)
        diffuse  = glm.vec3(1.0, 0.5, 0.31)
        ambient  = glm.vec3(1.0, 0.5, 0.31)
        specular = glm.vec3(0.5, 0.5, 0.5)
        self.m_rendering_shader.set_vec3('light.positon' , light_position)
        self.m_rendering_shader.set_vec3('light.ambient' , diffuse)
        self.m_rendering_shader.set_vec3('light.diffuse' , ambient)
        self.m_rendering_shader.set_vec3('light.specular', specular)
        self.m_rendering_shader.set_float("light.constant", 1.0)
        self.m_rendering_shader.set_float("light.linear", 0.09)
        self.m_rendering_shader.set_float("light.quadratic", 0.032)
        m_diffuse  = glm.vec3(0.2, 0.2, 0.5)
        m_ambient  = glm.vec3(0.1, 0.1, 0.8)
        m_specular = glm.vec3(1.0, 1.0, 1.0)
        self.m_rendering_shader.set_vec3('material.ambient' , m_diffuse)
        self.m_rendering_shader.set_vec3('material.diffuse' , m_ambient)
        self.m_rendering_shader.set_vec3('material.specular', m_specular)
        self.m_rendering_shader.set_float('material.shininess', 128.0)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glDisable(gl.GL_BLEND)

        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.__get_smooth_source_texture())
        gl.glActiveTexture(gl.GL_TEXTURE1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.__get_thick_smooth_source_texture())
        gl.glActiveTexture(gl.GL_TEXTURE2)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.m_normal_texture)
        gl.glActiveTexture(gl.GL_TEXTURE3)
        gl.glBindTexture(gl.GL_TEXTURE_2D, back_ground_texture)
        gl.glActiveTexture(gl.GL_TEXTURE4)
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.m_sky_texture)
        gl.glActiveTexture(gl.GL_TEXTURE5)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.m_fluid_frac_texture)
        gl.glBindVertexArray(self.m_quad_vao)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)

    def get_smoothed_depth_texture(self):
        return self.__get_smooth_source_texture()
        
    def __get_smooth_source_texture(self):
        return self.m_depth_texture_a if self.m_source_ab else self.m_depth_texture_b
    
    def __get_smooth_target_texture(self):
        return self.m_depth_texture_b if self.m_source_ab else self.m_depth_texture_a
    
    def __get_thick_smooth_source_texture(self):
        return self.m_thick_texture_a if self.m_thick_source_ab else self.m_thick_texture_b
    
    def __get_thick_smooth_target_texture(self):
        return self.m_thick_texture_b if self.m_thick_source_ab else self.m_thick_texture_a
    
    def set_matrix(self, model:glm.mat4, view:glm.mat4, projection:glm.mat4):
        self.m_model      = model
        self.m_view       = view
        self.m_projcetion = projection
