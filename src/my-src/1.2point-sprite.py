import glfw
import glm
import math
import numpy as np
import OpenGL.GL as gl
from PIL import Image
from pyrr import Matrix44

from include.shader_old import Shader
from include.camera import Camera, CameraMovement


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
    glfw.set_window_size_callback(window, framebuffer_size_callback)
    glfw.set_cursor_pos_callback(window, mouse_callback)
    glfw.set_scroll_callback(window, scroll_callback)

    # tell GLFW to capture our mouse
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    # configure global opengl state
    # 开启深度测试
    gl.glEnable(gl.GL_DEPTH_TEST)

    # ----------------------------------------------------------------------------------------------
    shader = Shader(r'res/my-shaders/1.2.shader')

    vertices = [
        # possition3f --- color3f
    -0.5, -0.5, 0.0,  1.0, 0.0, 0.0,
     0.5, -0.5, 0.0,  0.0, 1.0, 0.0,
     0.5,  0.5, 0.0,  0.0, 0.0, 1.0,
    ]
    vertices = np.array(vertices, np.float32)

    vao = gl.glGenVertexArrays(1)
    gl.glBindVertexArray(vao)

    vbo = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)
    # positon attr
    gl.glEnableVertexAttribArray(0)
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 6 * vertices[0].nbytes, gl.ctypes.c_void_p(0))
    # color attr
    # gl.glEnableVertexAttribArray(1)
    # gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 6 * vertices[0].nbytes, gl.ctypes.c_void_p(3 * vertices[0].nbytes))

    # load and create a texture----------------------------------------------------------------------------------------------------------
    texture = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture)
    # set the texture wrapping parameters
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
    # set texture filtering parameters
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR_MIPMAP_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    # load image, create texture and generate mipmaps
    img = Image.open(r'res/textures/container.jpg').transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, img.width, img.height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, img.tobytes())
    gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

    while not glfw.window_should_close(window):
        current_frame = glfw.get_time()
        delta_time = current_frame - last_frame
        last_frame = current_frame
        process_input(window)

        gl.glClearColor(.2, .3, .3, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        #点精灵设置
        # gl.glEnable(gl.GL_POINT_SPRITE)
        gl.glEnable(gl.GL_PROGRAM_POINT_SIZE)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE)

        shader.use()
        # 将矩阵传入着色器, 这通常在每次的渲染迭代中进行，因为变换矩阵会经常变动
        model = glm.mat4(1.0)
        view = camera.get_view_matrix()
        projection = glm.perspective(glm.radians(camera.zoom), width / height, 0.1, 100.0)
        shader.set_mat4('model', glm.value_ptr(model))
        shader.set_mat4('view', glm.value_ptr(view))
        shader.set_mat4('projection', glm.value_ptr(projection))
        gl.glBindVertexArray(vao)
        gl.glDrawArrays(gl.GL_POINTS, 0, 3)
    
        # 交换缓存
        glfw.swap_buffers(window)
        glfw.poll_events() 

    gl.glDeleteVertexArrays(1, id(vao))
    gl.glDeleteBuffers(1, id(vbo))
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
