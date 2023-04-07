import math

import glfw
import glm
import numpy as np
import OpenGL.GL as gl
from PIL import Image
from pyrr import Matrix44

from include.shader_old import Shader

width, height = 800, 600
camera_pos   = glm.vec3([0.0, 0.0,  3.0])
camera_front = glm.vec3([0.0, 0.0, -1.0])
camera_up    = glm.vec3([0.0, 1.0,  0.0])

delta_time = 0.0    # 当前帧与上一帧的时间差
last_frame = 0.0    # 上一帧的时间

first_mouse = True
fov = 45.0
yaw = -90.0         # 偏航角
pitch = 0.0         # 俯仰角
sensitivity = 0.1   # 偏移量乘以了sensitivity（灵敏度）值,如果忽略这个值,鼠标移动就会太大了
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

    shader = Shader(r'res/shaders/7.1-camera.shader')

    vertices = [
     # positions      tex_coords
    -0.5, -0.5, -0.5,  0.0, 0.0,
     0.5, -0.5, -0.5,  1.0, 0.0,
     0.5,  0.5, -0.5,  1.0, 1.0,
     0.5,  0.5, -0.5,  1.0, 1.0,
    -0.5,  0.5, -0.5,  0.0, 1.0,
    -0.5, -0.5, -0.5,  0.0, 0.0,

    -0.5, -0.5,  0.5,  0.0, 0.0,
     0.5, -0.5,  0.5,  1.0, 0.0,
     0.5,  0.5,  0.5,  1.0, 1.0,
     0.5,  0.5,  0.5,  1.0, 1.0,
    -0.5,  0.5,  0.5,  0.0, 1.0,
    -0.5, -0.5,  0.5,  0.0, 0.0,

    -0.5,  0.5,  0.5,  1.0, 0.0,
    -0.5,  0.5, -0.5,  1.0, 1.0,
    -0.5, -0.5, -0.5,  0.0, 1.0,
    -0.5, -0.5, -0.5,  0.0, 1.0,
    -0.5, -0.5,  0.5,  0.0, 0.0,
    -0.5,  0.5,  0.5,  1.0, 0.0,

     0.5,  0.5,  0.5,  1.0, 0.0,
     0.5,  0.5, -0.5,  1.0, 1.0,
     0.5, -0.5, -0.5,  0.0, 1.0,
     0.5, -0.5, -0.5,  0.0, 1.0,
     0.5, -0.5,  0.5,  0.0, 0.0,
     0.5,  0.5,  0.5,  1.0, 0.0,

    -0.5, -0.5, -0.5,  0.0, 1.0,
     0.5, -0.5, -0.5,  1.0, 1.0,
     0.5, -0.5,  0.5,  1.0, 0.0,
     0.5, -0.5,  0.5,  1.0, 0.0,
    -0.5, -0.5,  0.5,  0.0, 0.0,
    -0.5, -0.5, -0.5,  0.0, 1.0,

    -0.5,  0.5, -0.5,  0.0, 1.0,
     0.5,  0.5, -0.5,  1.0, 1.0,
     0.5,  0.5,  0.5,  1.0, 0.0,
     0.5,  0.5,  0.5,  1.0, 0.0,
    -0.5,  0.5,  0.5,  0.0, 0.0,
    -0.5,  0.5, -0.5,  0.0, 1.0
    ]

    vertices = np.array(vertices, np.float32)

    vao = gl.glGenVertexArrays(1)
    gl.glBindVertexArray(vao)

    vbo = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)

    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 5 * vertices[0].nbytes, gl.ctypes.c_void_p(0))
    gl.glEnableVertexAttribArray(0)

    gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, 5 * vertices[0].nbytes, gl.ctypes.c_void_p(3 * vertices[0].nbytes))
    gl.glEnableVertexAttribArray(1)

    # -- load texture 1
    texture1 = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture1)
    # -- texture wrapping
    gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
    gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
    # -- texture filterting
    gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

    img = Image.open(r'res/textures/container.jpg').transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, img.width, img.height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, img.tobytes())
    gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

    # -- load texture 2
    texture2 = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture2)
    # -- texture wrapping
    gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
    gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
    # -- texture filterting
    gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

    img = Image.open(r'res/textures/awesomeface.png').transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, img.width, img.height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, img.tobytes())
    gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

    shader.use()
    shader.set_int("texture1", 0)
    shader.set_int("texture2", 1)

    cube_positions = [
        ( 0.0,  0.0,  0.0),
        ( 2.0,  5.0, -15.0),
        (-1.5, -2.2, -2.5),
        (-3.8, -2.0, -12.3),
        ( 2.4, -0.4, -3.5),
        (-1.7,  3.0, -7.5),
        ( 1.3, -2.0, -2.5),
        ( 1.5,  2.0, -2.5),
        ( 1.5,  0.2, -1.5),
        (-1.3,  1.0, -1.5)
    ]

    while not glfw.window_should_close(window):
        current_frame = glfw.get_time()
        delta_time = current_frame - last_frame
        last_frame = current_frame
        print(delta_time, last_frame)

        process_input(window)

        gl.glClearColor(.2, .3, .3, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture1)
        gl.glActiveTexture(gl.GL_TEXTURE1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture2)

        shader.use()
        
        gl.glBindVertexArray(vao)

        view = glm.mat4(1.0)
        view = glm.lookAt(camera_pos, camera_pos + camera_front, camera_up)

        projection = glm.perspective(glm.radians(fov), width / height, 0.1, 100.0)

        # 将矩阵传入着色器, 这通常在每次的渲染迭代中进行，因为变换矩阵会经常变动
        shader.set_mat4('view', glm.value_ptr(view))
        shader.set_mat4('projection', glm.value_ptr(projection))
        for idx, position in enumerate(cube_positions):
            angle = 20.0 * idx
            if idx % 3 == 0:
                angle = glfw.get_time() * 25.0
            model = glm.mat4(1.0)
            model = glm.translate(model, position) 
            model = glm.rotate(model, glm.radians(angle), [1.0, 0.3, 0.5]) 

            shader.set_mat4('model', glm.value_ptr(model))

            gl.glDrawArrays(gl.GL_TRIANGLES, 0, 36)
        
        
        glfw.swap_buffers(window)
        glfw.poll_events() 

    gl.glDeleteVertexArrays(1, id(vao))
    gl.glDeleteBuffers(1, id(vbo))
    glfw.terminate()


def on_resize(window, w, h):
    gl.glViewport(0, 0, w, h)


def process_input(window):
    global camera_pos, camera_front
    camera_speed = 2.5 * delta_time

    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(window, True)
    
    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        camera_pos += camera_speed * camera_front
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        camera_pos -= camera_speed * camera_front
 
    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        camera_pos -= glm.normalize(glm.cross(camera_front, camera_up)) * camera_speed
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        camera_pos += glm.normalize(glm.cross(camera_front, camera_up)) * camera_speed

def mouse_callback(window, xpos, ypos):
    """
    计算鼠标距上一帧的偏移量。
    把偏移量添加到摄像机的俯仰角和偏航角中。
    对偏航角和俯仰角进行最大和最小值的限制。
    计算方向向量。
    """
    global first_mouse, pitch, yaw, last_x, last_y, camera_front
    if first_mouse:
        last_x, last_y = xpos, ypos
        first_mouse = False

    xoffset = xpos - last_x
    yoffset = last_y - ypos  # XXX Note Reversed (y-coordinates go from bottom to top)
    last_x = xpos
    last_y = ypos

    xoffset *= sensitivity
    yoffset *= sensitivity

    yaw += xoffset
    pitch += yoffset
    if pitch > 89.0:
        pitch = 89.0
    if pitch < -89.0:
        pitch = -89.0

    front = glm.vec3()
    front.x = math.cos(math.radians(yaw)) * math.cos(math.radians(pitch))
    front.y = math.sin(math.radians(pitch))
    front.z = math.sin(math.radians(yaw)) * math.cos(math.radians(pitch))
    camera_front = glm.normalize(front)

def scroll_callback(window, dx, dy):
    global fov
    if fov >= 1.0 and fov <= 45.0:
        fov -= dy

    if fov <= 1.0:
        fov = 1.0
    if fov >= 45.0:
        fov = 45.0

if __name__ == '__main__':
    main()
