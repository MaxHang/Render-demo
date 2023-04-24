import math
from ctypes import c_float, c_void_p, sizeof

import glfw
import glm
import numpy as np
import open3d as o3d
import OpenGL.GL as gl

from include.camera import Camera, CameraMovement
from include.model import Model
from include.shader import Shader
from include.texture import load_cubemap, load_texture

# -- settings
SRC_WIDTH = 800
SRC_HEIGHT = 600

# -- camera
camera = Camera(glm.vec3([0.0, 0.0, 8.0]))
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
    skybox_shader = Shader("src/4.advanced_opengl/shaders/6.1.skybox.vs", "src/4.advanced_opengl/shaders/6.1.skybox.fs")
    skybox_vertices = [
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
    ]
    # skybox
    skybox_vbo = gl.glGenBuffers(1)
    skybox_vao = gl.glGenVertexArrays(1)
    vertices = (c_float * len(skybox_vertices))(*skybox_vertices)

    gl.glBindVertexArray(skybox_vao)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, skybox_vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, sizeof(vertices), vertices, gl.GL_STATIC_DRAW)
    # -- position attribute
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 3 * sizeof(c_float), c_void_p(0))
    gl.glEnableVertexAttribArray(0)
    
    # pcd = o3d.io.read_point_cloud("src/my_src/test.ply")
    start = glfw.get_time()
    pcd = o3d.io.read_point_cloud("fluid_render/resource/particles_data/vis_1_0.001/fluid_40.ply")
    vertices = np.asarray(pcd.points, dtype=np.float32).ravel()
    print(f"读取文件解析位置用时: {glfw.get_time() - start}")
    print(len(vertices) // 3)
    print(vertices)

    # point sprite

    point_vao = gl.glGenVertexArrays(1)
    point_vbo = gl.glGenBuffers(1)
    gl.glBindVertexArray(point_vao)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, point_vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)
    # positon attr
    gl.glEnableVertexAttribArray(0)
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 3 * sizeof(c_float), gl.ctypes.c_void_p(0))

    # point_vertices = [
    #     # possition3f --- color3f
    #     -0.5, -0.5, 1.0,  1.0, 0.0, 0.0,
    #      0.5, -0.5, 0.5,  0.0, 1.0, 0.0,
    #      0.5,  0.5, 0.7,  0.0, 0.0, 1.0,
    #     # -0.25412, -0.11759,  0.01171, 255, 0  , 255,
    #     #  0.18866,  0.0793 ,  0.00609, 255, 0  , 255,
    #     #  0.03777,  0.06232, -0.00753, 255, 0  , 255,
    #     # -0.25185, -0.08387, -0.01735, 255, 0  , 255,
    #     # -0.35174, -0.16687, -0.00875, 0  , 255, 0  ,
    # ]

    # # point sprite
    # vertices = (c_float * len(point_vertices))(*point_vertices)

    # point_vao = gl.glGenVertexArrays(1)
    # point_vbo = gl.glGenBuffers(1)
    # gl.glBindVertexArray(point_vao)
    # gl.glBindBuffer(gl.GL_ARRAY_BUFFER, point_vbo)
    # gl.glBufferData(gl.GL_ARRAY_BUFFER, sizeof(vertices), vertices, gl.GL_STATIC_DRAW)
    # # positon attr
    # gl.glEnableVertexAttribArray(0)
    # gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 6 * sizeof(c_float), gl.ctypes.c_void_p(0))



    # load and create a texture----------------------------------------------------------------------------------------------------------
    texture = load_texture("container.jpg")

    faces = [
        "right.jpg",
        "left.jpg",
        "top.jpg",
        "bottom.jpg",
        "front.jpg",
        "back.jpg",
    ]

    # load textures
    skybox_texture = load_cubemap(faces)

    skybox_shader.use()
    skybox_shader.set_int('skybox', 0)
    
    i = 0

    while not glfw.window_should_close(window):
        current_frame = glfw.get_time()
        delta_time = current_frame - last_frame
        # print(delta_time)
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


        pcd = o3d.io.read_point_cloud(f"fluid_render/resource/particles_data/vis_1_0.001/fluid_{i}.ply")
        vertices = np.asarray(pcd.points, dtype=np.float32).ravel()
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, point_vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(point_vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, point_vbo)
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 3 * sizeof(c_float), gl.ctypes.c_void_p(0))
        gl.glBindVertexArray(0)
        
        model = glm.mat4(1.0)
        view = camera.get_view_matrix()
        projection = glm.perspective(glm.radians(camera.zoom), SRC_WIDTH / SRC_HEIGHT, 0.1, 100.0)

        # print(model, view, projection)

        shader.use()
        shader.set_mat4('model', glm.value_ptr(model))
        shader.set_mat4('view', glm.value_ptr(view))
        shader.set_mat4('projection', glm.value_ptr(projection))
        # 计算屏幕空间的 d
        zoom = camera.get_zoom()
        screenSpacePointZ = SRC_HEIGHT / math.tan(glm.radians(zoom))
        shader.set_float("pointRadius", 0.075)
        shader.set_float("pointScale", screenSpacePointZ)

        gl.glBindVertexArray(point_vao)
        gl.glDrawArrays(gl.GL_POINTS, 0, len(vertices) // 3)
        if i < 77:
            i += 1

        # draw skybox at last
        gl.glDepthFunc(gl.GL_LEQUAL) # 片段深度小于或者等于时通过测试
        skybox_shader.use()
        projection = glm.perspective(glm.radians(camera.zoom), SRC_WIDTH/SRC_HEIGHT, 0.1, 100.0)
        view = glm.mat4(glm.mat3(camera.get_view_matrix())) # 通过保留view的左上角3*3矩阵移除位移效果
        skybox_shader.set_mat4("projection", glm.value_ptr(projection))
        skybox_shader.set_mat4("view", glm.value_ptr(view))
        gl.glBindVertexArray(skybox_vao)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, skybox_texture)    # 纹理单元0被默认激活，当前纹理绑定到纹理单元0
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 36)
        gl.glBindVertexArray(0)
        gl.glDepthFunc(gl.GL_LESS) # 改回默认
    
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
