import platform
from ctypes import c_float, c_void_p, sizeof
from pathlib import Path

import glfw
import glm
import OpenGL.GL as gl
from pyrr import Matrix44, Vector3

from include.camera import Camera, CameraMovement
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

    shader = Shader("src/4.advanced_opengl/shaders/1.2.depth_testing.vs", "src/4.advanced_opengl/shaders/1.2.depth_testing.fs")

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


    # load textures
    cube_texture = load_texture("marble.jpg")
    floor_texture = load_texture("metal.png")

    shader.use()
    shader.set_int('texture1', 0)


    while not glfw.window_should_close(window):
        # -- time logic
        current_frame = glfw.get_time()
        delta_time = current_frame - last_frame
        last_frame = current_frame

        # -- input
        process_input(window)

        # -- render
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

        glfw.swap_buffers(window)
        glfw.poll_events()

    gl.glDeleteVertexArrays(1, id(cube_vao))
    gl.glDeleteBuffers(1, id(cube_vbo))
    gl.glDeleteVertexArrays(1, id(plane_vao))
    gl.glDeleteBuffers(1, id(plane_vbo))

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
