import math
from ctypes import c_float, c_void_p, sizeof

import glfw
import glm
import numpy as np
import OpenGL.GL as gl
from PIL import Image
from pyrr import Matrix44

from include.camera import Camera, CameraMovement
from include.model import Model
from include.shader import Shader
from include.texture import load_texture

# -- settings
SRC_WIDTH = 800
SRC_HEIGHT = 600

# -- camera
camera = Camera(glm.vec3([0.0, 0.0, 3.0]))
last_x = SRC_WIDTH / 2
last_y = SRC_HEIGHT / 2
first_mouse = True

# -- timing
delta_time = 0.0
last_frame = 0.0

def main():
    global delta_time, last_frame

    glfw.init()
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    window = glfw.create_window(SRC_WIDTH, SRC_HEIGHT, "LearnOpenGL", None, None)
    if not window:
        print("Window Creation failed!")
        glfw.terminate()

    glfw.make_context_current(window)
    glfw.set_window_size_callback(window, framebuffer_size_callback)
    glfw.set_cursor_pos_callback(window, mouse_callback)
    glfw.set_scroll_callback(window, scroll_callback)

    # tell GLFW to capture our mouse
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    # configure global opengl state
    # 开启深度测试
    gl.glEnable(gl.GL_DEPTH_TEST)
    # gl.glEnable(gl.GL_POINT_SPRITE)
    gl.glEnable(gl.GL_PROGRAM_POINT_SIZE)

    # gl.glEnable(gl.GL_BLEND)
    # gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE)

    # ----------------------------------------------------------------------------------------------
    shader = Shader(r'src/my_src/shaders/1.2.point_sprite.vs', r'src/my_src/shaders/1.2.point_sprite.fs')
    mmodel = Model("res/objects/backpack/backpack.obj")
    model_shader = Shader("src/3.model_loading/shaders/model_loading.vs", "src/3.model_loading/shaders/model_loading.fs")
    ground_shader = Shader(r'src/my_src/shaders/ground.vs', r'src/my_src/shaders/ground')
    
    # ground
    ground_vertices = np.array(
        [
        #position, tex coord
        -5.0,  5.0, 0.0, 0.0, 1.0,
        -5.0, -5.0, 0.0, 0.0, 0.0,
        5.0, -5.0, 0.0, 1.0, 0.0,
        -5.0,  5.0, 0.0, 0.0, 1.0,
        5.0, -5.0, 0.0, 1.0, 0.0,
        5.0,  5.0, 0.0, 1.0, 1.0
        ],
        dtype= np.float32
    )

    point_vertices = [
        # possition3f --- color3f
        -0.5, -0.5, 1.0,  1.0, 0.0, 0.0,
         0.5, -0.5, 0.5,  0.0, 1.0, 0.0,
         0.5,  0.5, 0.7,  0.0, 0.0, 1.0,
    ]

    # point sprite
    vertices = (c_float * len(point_vertices))(*point_vertices)

    point_vao = gl.glGenVertexArrays(1)
    point_vbo = gl.glGenBuffers(1)
    gl.glBindVertexArray(point_vao)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, point_vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, sizeof(vertices), vertices, gl.GL_STATIC_DRAW)
    # positon attr
    gl.glEnableVertexAttribArray(0)
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 6 * sizeof(c_float), gl.ctypes.c_void_p(0))

    # load and create a texture----------------------------------------------------------------------------------------------------------
    texture = load_texture("container.jpg")

    shader.use()
    

    while not glfw.window_should_close(window):
        current_frame = glfw.get_time()
        delta_time = current_frame - last_frame
        last_frame = current_frame
        process_input(window)

        gl.glClearColor(.2, .3, .3, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # model
        model_shader.use()

        # -- view.projection transformations
        projection = glm.perspective(glm.radians(camera.zoom), SRC_WIDTH/SRC_HEIGHT, 0.1, 100.0)
        view = camera.get_view_matrix()
        model_shader.set_mat4("projection", glm.value_ptr(projection))
        model_shader.set_mat4("view", glm.value_ptr(view))

        # -- world transformation
        model = glm.mat4(1.0)
        model = glm.translate(model, [0.0, -0.75, 0.0]) 
        model = glm.scale(model, [0.2, 0.2, 0.2]) 
        model_shader.set_mat4("model", glm.value_ptr(model))

        mmodel.draw(model_shader)

        shader.use()
        model = glm.mat4(1.0)
        view = camera.get_view_matrix()
        projection = glm.perspective(glm.radians(camera.zoom), SRC_WIDTH / SRC_HEIGHT, 0.1, 100.0)
        # 计算屏幕空间的 d
        zoom = camera.get_zoom()
        screenSpacePointZ = SRC_HEIGHT / math.tan(glm.radians(zoom))
        shader.set_mat4('model', glm.value_ptr(model))
        shader.set_mat4('view', glm.value_ptr(view))
        shader.set_mat4('projection', glm.value_ptr(projection))
        shader.set_float("viewSpacePointSize", 80)
        shader.set_float("screenSpacePointZ", screenSpacePointZ)
        
        gl.glBindVertexArray(point_vao)
        gl.glDrawArrays(gl.GL_POINTS, 0, 3)
    
        # 交换缓存
        glfw.swap_buffers(window)
        glfw.poll_events() 

    gl.glDeleteVertexArrays(1, id(point_vao))
    gl.glDeleteBuffers(1, id(point_vbo))
    glfw.terminate()


def framebuffer_size_callback(window, w, h):
    gl.glViewport(0, 0, w, h)


def process_input(window):
    global camera, delta_time

    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(window, True)
    
    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        camera.process_keyboard(CameraMovement.FORWARD, delta_time)
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        camera.process_keyboard(CameraMovement.BACKWARD, delta_time)

    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        camera.process_keyboard(CameraMovement.LEFT, delta_time)
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        camera.process_keyboard(CameraMovement.RIGHT, delta_time)

def mouse_callback(window, xpos, ypos):
    """
    计算鼠标距上一帧的偏移量。
    把偏移量添加到摄像机的俯仰角和偏航角中。
    对偏航角和俯仰角进行最大和最小值的限制。
    计算方向向量。
    """
    global first_mouse, last_x, last_y, camera

    if first_mouse:
        last_x, last_y = xpos, ypos
        first_mouse = False

    xoffset = xpos - last_x
    yoffset = last_y - ypos  # XXX Note Reversed (y-coordinates go from bottom to top)
    last_x = xpos
    last_y = ypos

    camera.process_mouse_movement(xoffset, yoffset)

def scroll_callback(window, dx, dy):
    global camera
    
    camera.process_mouse_scroll(dy)

if __name__ == '__main__':
    main()
