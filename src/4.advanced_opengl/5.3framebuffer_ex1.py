import glfw
import glm
import platform
import OpenGL.GL as gl
from pathlib import Path
from pyrr import Vector3, Matrix44
from ctypes import c_float, sizeof, c_void_p


from include.shader import Shader
from include.texture import load_texture
from include.camera import Camera, CameraMovement

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

    if not glfw.init():
        raise ValueError("Failed to initialize glfw")

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    if platform.system() == 'Darwin':
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

    window = glfw.create_window(SRC_WIDTH, SRC_HEIGHT, "learnOpenGL", None, None)
    if not window:
        glfw.terminate()
        raise ValueError("Failed to create window")

    glfw.make_context_current(window)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    glfw.set_cursor_pos_callback(window, mouse_callback)
    glfw.set_scroll_callback(window, scroll_callback)

    # tell GLFW to capture our mouse
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    gl.glEnable(gl.GL_DEPTH_TEST)
    # gl.glDepthFunc(gl.GL_ALWAYS)

    shader = Shader("src/4.advanced_opengl/shaders/1.1.depth_testing.vs", "src/4.advanced_opengl/shaders/1.1.depth_testing.fs")
    screen_shader = Shader("src/4.advanced_opengl/shaders/5.1.framebuffer_screen.vs", "src/4.advanced_opengl/shaders/5.1.framebuffer_screen.fs")

    cube_vertices = [
        # positions        texture Coords
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

    plane_vertices = [
        #positions         texture Coords (note we set these higher than 1 (together with GL_REPEAT as texture wrapping mode). this will cause the floor texture to repeat)
         5.0, -0.5,  5.0,  2.0, 0.0,
        -5.0, -0.5,  5.0,  0.0, 0.0,
        -5.0, -0.5, -5.0,  0.0, 2.0,

         5.0, -0.5,  5.0,  2.0, 0.0,
        -5.0, -0.5, -5.0,  0.0, 2.0,
         5.0, -0.5, -5.0,  2.0, 2.0
    ]

    quad_vertices = [
    # positions    texCoords
        -0.3,  1.0,  0.0, 1.0,
        -0.3,  0.7,  0.0, 0.0,
         0.3,  0.7,  1.0, 0.0,

        -0.3,  1.0,  0.0, 1.0,
         0.3,  0.7,  1.0, 0.0,
         0.3,  1.0,  1.0, 1.0
    ]

    # cube
    cube_vbo = gl.glGenBuffers(1)
    cube_vao = gl.glGenVertexArrays(1)
    vertices = (c_float * len(cube_vertices))(*cube_vertices)

    gl.glBindVertexArray(cube_vao)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, cube_vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, sizeof(vertices), vertices, gl.GL_STATIC_DRAW)
    # -- position attribute
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 5 * sizeof(c_float), c_void_p(0))
    gl.glEnableVertexAttribArray(0)
    # -- uv attribute
    gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, 5 * sizeof(c_float), c_void_p(3 * sizeof(c_float)))
    gl.glEnableVertexAttribArray(1)
    gl.glBindVertexArray(0)

    # plane
    plane_vbo = gl.glGenBuffers(1)
    plane_vao = gl.glGenVertexArrays(1)
    vertices = (c_float * len(plane_vertices))(*plane_vertices)

    gl.glBindVertexArray(plane_vao)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, plane_vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, sizeof(vertices), vertices, gl.GL_STATIC_DRAW)
    # -- position attribute
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 5 * sizeof(c_float), c_void_p(0))
    gl.glEnableVertexAttribArray(0)
    # -- uv attribute
    gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, 5 * sizeof(c_float), c_void_p(3 * sizeof(c_float)))
    gl.glEnableVertexAttribArray(1)
    gl.glBindVertexArray(0)

    # quad
    quad_vao = gl.glGenVertexArrays(1)
    quad_vbo = gl.glGenBuffers(1)
    vertices = (c_float * len(quad_vertices))(*quad_vertices)
    gl.glBindVertexArray(quad_vao)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, quad_vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, sizeof(vertices), vertices, gl.GL_STATIC_DRAW)
    # -- position attribute
    gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 4 * sizeof(c_float), c_void_p(0))
    gl.glEnableVertexAttribArray(0)
    # -- uv attribute
    gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, 4 * sizeof(c_float), c_void_p(2 * sizeof(c_float)))
    gl.glEnableVertexAttribArray(1)
    gl.glBindVertexArray(0)
    
    # load textures
    cube_texture = load_texture("container.jpg")
    floor_texture = load_texture("metal.png")

    shader.use()
    shader.set_int('texture1', 0)

    screen_shader.use()
    screen_shader.set_int('screenTexture', 0)

    # framebuffer configuration
    # 创建帧缓存对象，并且绑定
    framebuffer = gl.glGenFramebuffers(1)
    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, framebuffer)
    # 创建纹理图像，将其作为颜色附件附加到帧缓存中，纹理的维度设置为窗口的宽度和高度
    tex_colorbuffer = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, tex_colorbuffer)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, SRC_WIDTH, SRC_HEIGHT, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, None)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
    gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, tex_colorbuffer, 0)
    # create a renderbuffer object for depth and stencil attachment (we won't be sampling these)
    rbo = gl.glGenRenderbuffers(1)
    gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, rbo)
    gl.glRenderbufferStorage(gl.GL_RENDERBUFFER, gl.GL_DEPTH24_STENCIL8, SRC_WIDTH, SRC_HEIGHT)
    gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, 0)
    gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER, gl.GL_DEPTH_STENCIL_ATTACHMENT, gl.GL_RENDERBUFFER, rbo)
    # now that we actually created the framebuffer and added all attachments we want to check if it is actually complete now
    if (gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER) != gl.GL_FRAMEBUFFER_COMPLETE):
        raise RuntimeError("ERROR.FRAMEBUFFER. Framebuffer is not complete!")
    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

    while not glfw.window_should_close(window):
        # -- time logic
        current_frame = glfw.get_time()
        delta_time = current_frame - last_frame
        last_frame = current_frame

        # -- input
        process_input(window)

        # -- render
        # first render pass: mirror texture.
        # bind to framebuffer and draw to color texture as we normally 
        # would, but with the view camera reversed.
        # bind to framebuffer and draw scene as we normally would to color texture
        # 1.自建缓冲保存后视镜
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, framebuffer)
        gl.glClearColor(0.1, 0.1, 0.1, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glEnable(gl.GL_DEPTH_TEST)
        # -- view.projection transformations
        shader.use()
        projection = glm.perspective(camera.zoom, SRC_WIDTH/SRC_HEIGHT, 0.1, 100.0)
        camera.yaw += 180.0
        camera.process_mouse_movement(0, 0, False)
        view = camera.get_view_matrix()
        camera.yaw -= 180.0
        camera.process_mouse_movement(0, 0, True)
        shader.set_mat4("projection", glm.value_ptr(projection))
        shader.set_mat4("view", glm.value_ptr(view))

        # cube
        gl.glBindVertexArray(cube_vao)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, cube_texture)
        model = glm.mat4(1.0)
        model = glm.translate(model, (-1.0, 0.0, -1.0))
        shader.set_mat4("model", glm.value_ptr(model))
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 36)
        model = glm.mat4(1.0)
        model = glm.translate(model, (2.0, 0.0, 0.0))
        shader.set_mat4("model", glm.value_ptr(model))
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 36)

        # floor
        gl.glBindVertexArray(plane_vao)
        gl.glBindTexture(gl.GL_TEXTURE_2D, floor_texture)
        model = glm.mat4(1.0)
        shader.set_mat4("model", glm.value_ptr(model))
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)
        gl.glBindVertexArray(0)


        # 2.默认缓冲绘制原来的图像
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        gl.glClearColor(0.1, 0.1, 0.1, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        # -- view.projection transformations
        shader.use()
        projection = glm.perspective(camera.zoom, SRC_WIDTH/SRC_HEIGHT, 0.1, 100.0)
        view = camera.get_view_matrix()
        shader.set_mat4("projection", glm.value_ptr(projection))
        shader.set_mat4("view", glm.value_ptr(view))

        # cube
        gl.glBindVertexArray(cube_vao)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, cube_texture)
        model = glm.mat4(1.0)
        model = glm.translate(model, (-1.0, 0.0, -1.0))
        shader.set_mat4("model", glm.value_ptr(model))
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 36)
        model = glm.mat4(1.0)
        model = glm.translate(model, (2.0, 0.0, 0.0))
        shader.set_mat4("model", glm.value_ptr(model))
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 36)

        # floor
        gl.glBindVertexArray(plane_vao)
        gl.glBindTexture(gl.GL_TEXTURE_2D, floor_texture)
        model = glm.mat4(1.0)
        shader.set_mat4("model", glm.value_ptr(model))
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)
        gl.glBindVertexArray(0)

        # 3.通过颜色纹理绘制后视镜视角
        gl.glDisable(gl.GL_DEPTH_TEST)

        screen_shader.use()
        gl.glBindVertexArray(quad_vao)
        gl.glBindTexture(gl.GL_TEXTURE_2D, tex_colorbuffer)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 6)

        glfw.swap_buffers(window)
        glfw.poll_events()

    gl.glDeleteVertexArrays(1, id(cube_vao))
    gl.glDeleteBuffers(1, id(cube_vbo))
    gl.glDeleteVertexArrays(1, id(plane_vao))
    gl.glDeleteBuffers(1, id(plane_vbo))
    gl.glDeleteVertexArrays(1, id(quad_vao))
    gl.glDeleteBuffers(1, id(quad_vbo))

    glfw.terminate()


def process_input(window):
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


def framebuffer_size_callback(window, width, height):
    gl.glViewport(0, 0, width, height)


def mouse_callback(window, xpos, ypos):
    global first_mouse, last_x, last_y

    if first_mouse:
        last_x, last_y = xpos, ypos
        first_mouse = False

    xoffset = xpos - last_x
    yoffset = last_y - ypos  # XXX Note Reversed (y-coordinates go from bottom to top)
    last_x = xpos
    last_y = ypos

    camera.process_mouse_movement(xoffset, yoffset)


def scroll_callback(window, xoffset, yoffset):
    camera.process_mouse_scroll(yoffset)


if __name__ == '__main__':
    main()
