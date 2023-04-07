import math

import glfw
import glm
import numpy as np
import OpenGL.GL as gl
from PIL import Image
from pyrr import Matrix44

from include.camera import Camera, CameraMovement
from include.shader_old import Shader

width, height = 800, 600

delta_time = 0.0    # 当前帧与上一帧的时间差
last_frame = 0.0    # 上一帧的时间

camera = Camera([0.0, 0.0, 3.0])
first_mouse = True
last_x = 800 / 2
last_y = 600 / 2

def main():
    global delta_time, last_frame

    glfw.init()
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    window = glfw.create_window(width, height, "LearnOpenGL", None, None)
    if not window:
        print("Window Creation failed!")
        glfw.terminate()

    glfw.make_context_current(window)
    glfw.set_window_size_callback(window, on_resize)
    glfw.set_cursor_pos_callback(window, mouse_callback)
    glfw.set_scroll_callback(window, scroll_callback)

    # tell GLFW to capture our mouse
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    # configure global opengl state
    # 开启深度测试
    gl.glEnable(gl.GL_DEPTH_TEST)

    shader = Shader(r'res/my-shaders/1.1.shader')

    # vertices = [
    #  # positions      tex_coords
    #  1.0,  1.0,  1.0, 1.0,  
	# 0.67, 0.68, 0.82, 1.0,  
	#  1.0,  0.5,  0.5, 1.0,  
	#  1.0, 0.82, 0.65, 1.0, 
    # ]
    vertices = [
    -0.5, -0.5, 0.0,  
     0.5, -0.5, 0.0,  
     0.5,  0.5, 0.0,  
    -0.5,  0.5, 0.0, 
    ]
    indices = [         # 索引, 指明使用的是顶点数组中的哪些顶点
        0, 1, 2,
        2, 3, 0,
    ]

    vertices = np.array(vertices, np.float32)
    indices = np.array(indices, np.uint32)

    vao = gl.glGenVertexArrays(1)
    gl.glBindVertexArray(vao)

    vbo = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)
    gl.glEnableVertexAttribArray(0)
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, gl.ctypes.c_void_p(0))

    ebo = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ebo)
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, gl.GL_STATIC_DRAW)

    while not glfw.window_should_close(window):
        current_frame = glfw.get_time()
        delta_time = current_frame - last_frame
        last_frame = current_frame
        process_input(window)

        gl.glClearColor(.2, .3, .3, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # gl.glEnable(gl.GL_POINT_SPRITE)

        shader.use()
        # 将矩阵传入着色器, 这通常在每次的渲染迭代中进行，因为变换矩阵会经常变动
        model = glm.mat4(1.0)
        view = camera.get_view_matrix()
        projection = glm.perspective(glm.radians(camera.zoom), width / height, 0.1, 100.0)
        shader.set_mat4('model', glm.value_ptr(model))
        shader.set_mat4('view', glm.value_ptr(view))
        shader.set_mat4('projection', glm.value_ptr(projection))
        gl.glBindVertexArray(vao)
        gl.glDrawElements(gl.GL_TRIANGLES, 6, gl.GL_UNSIGNED_INT, gl.ctypes.c_void_p(0))
    
        glfw.swap_buffers(window)
        glfw.poll_events() 

    gl.glDeleteVertexArrays(1, id(vao))
    gl.glDeleteBuffers(1, id(vbo))
    gl.glDeleteBuffers(1, id(ebo))
    glfw.terminate()


def on_resize(window, w, h):
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
