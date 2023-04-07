from ctypes import c_float, c_void_p, sizeof
from pathlib import Path

import glfw
import glm
import OpenGL.GL as gl
from pyrr import Matrix44, Vector3

from include.camera import Camera, CameraMovement
from include.shader import Shader

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

light_pos = glm.vec3([1.2, 1.0, 2.0])


def main():
    global delta_time, last_frame

    if not glfw.init():
        raise ValueError("Failed to initialize glfw")

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)

    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    window = glfw.create_window(SRC_WIDTH, SRC_HEIGHT, "learnOpenGL", None, None)
    if not window:
        glfw.terminate()
        raise ValueError("Failed to create window")

    glfw.make_context_current(window)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    glfw.set_cursor_pos_callback(window, mouse_callback)
    glfw.set_scroll_callback(window, scroll_callback)

    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    gl.glEnable(gl.GL_DEPTH_TEST)

    lamp_shader = Shader("src/2.lighting/shaders/1.lamp.vs", "src/2.lighting/shaders/1.lamp.fs")
    lighting_shader = Shader("src/2.lighting/shaders/3.1.materials.vs", "src/2.lighting/shaders/3.1.materials.fs")

    vertices = [
        -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,
         0.5, -0.5, -0.5,  0.0,  0.0, -1.0,
         0.5,  0.5, -0.5,  0.0,  0.0, -1.0,
         0.5,  0.5, -0.5,  0.0,  0.0, -1.0,
        -0.5,  0.5, -0.5,  0.0,  0.0, -1.0,
        -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,

        -0.5, -0.5,  0.5,  0.0,  0.0,  1.0,
         0.5, -0.5,  0.5,  0.0,  0.0,  1.0,
         0.5,  0.5,  0.5,  0.0,  0.0,  1.0,
         0.5,  0.5,  0.5,  0.0,  0.0,  1.0,
        -0.5,  0.5,  0.5,  0.0,  0.0,  1.0,
        -0.5, -0.5,  0.5,  0.0,  0.0,  1.0,

        -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,
        -0.5,  0.5, -0.5, -1.0,  0.0,  0.0,
        -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,
        -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,
        -0.5, -0.5,  0.5, -1.0,  0.0,  0.0,
        -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,

         0.5,  0.5,  0.5,  1.0,  0.0,  0.0,
         0.5,  0.5, -0.5,  1.0,  0.0,  0.0,
         0.5, -0.5, -0.5,  1.0,  0.0,  0.0,
         0.5, -0.5, -0.5,  1.0,  0.0,  0.0,
         0.5, -0.5,  0.5,  1.0,  0.0,  0.0,
         0.5,  0.5,  0.5,  1.0,  0.0,  0.0,

        -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,
         0.5, -0.5, -0.5,  0.0, -1.0,  0.0,
         0.5, -0.5,  0.5,  0.0, -1.0,  0.0,
         0.5, -0.5,  0.5,  0.0, -1.0,  0.0,
        -0.5, -0.5,  0.5,  0.0, -1.0,  0.0,
        -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,

        -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,
         0.5,  0.5, -0.5,  0.0,  1.0,  0.0,
         0.5,  0.5,  0.5,  0.0,  1.0,  0.0,
         0.5,  0.5,  0.5,  0.0,  1.0,  0.0,
        -0.5,  0.5,  0.5,  0.0,  1.0,  0.0,
        -0.5,  0.5, -0.5,  0.0,  1.0,  0.0
    ]
    vertices = (c_float * len(vertices))(*vertices)

    # first, configure the cube's VAO (and VBO)
    cube_vao = gl.glGenVertexArrays(1)
    vbo = gl.glGenBuffers(1)

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, sizeof(vertices), vertices, gl.GL_STATIC_DRAW)

    gl.glBindVertexArray(cube_vao)

    # -- position attribute
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 6 * sizeof(c_float), c_void_p(0))
    gl.glEnableVertexAttribArray(0)
    # -- normal attribute
    gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 6 * sizeof(c_float), c_void_p(3 * sizeof(c_float)))
    gl.glEnableVertexAttribArray(1)

    # -- second configure light vao (vbo is the same)
    light_cube_vao = gl.glGenVertexArrays(1)
    gl.glBindVertexArray(light_cube_vao)

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 6 * sizeof(c_float), c_void_p(0))
    gl.glEnableVertexAttribArray(0)

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

        lighting_shader.use()
        lighting_shader.set_vec3("light.position", glm.value_ptr(light_pos))
        lighting_shader.set_vec3("viewPos", glm.value_ptr(camera.position))

        light_color = glm.vec3([1.0,1.0,1.0])

        diffuse_color = light_color * 0.5
        ambient_color = light_color * 0.2
        lighting_shader.set_vec3("light.ambient", glm.value_ptr(ambient_color))
        lighting_shader.set_vec3("light.diffuse", glm.value_ptr(diffuse_color))
        lighting_shader.set_vec3("light.specular", Vector3([1.0, 1.0, 1.0]))

        # -- material properties
        lighting_shader.set_vec3("material.ambient", Vector3([1.0, 0.5, 0.31]))
        lighting_shader.set_vec3("material.diffuse", Vector3([1.0, 0.5, 0.31]))
        lighting_shader.set_vec3("material.specular", Vector3([0.5, 0.5, 0.5]))
        lighting_shader.set_float("material.shininess", 32.0)

        # -- view.projection transformations
        projection = glm.perspective(camera.zoom, SRC_WIDTH/SRC_HEIGHT, 0.1, 100.0)
        view = camera.get_view_matrix()
        lighting_shader.set_mat4("projection", glm.value_ptr(projection))
        lighting_shader.set_mat4("view", glm.value_ptr(view))

        # -- world transformation
        model = glm.mat4(1.0)
        lighting_shader.set_mat4("model", glm.value_ptr(model))

        # -- render cube
        gl.glBindVertexArray(cube_vao)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 36)

        # -- draw lamp object
        lamp_shader.use()
        lamp_shader.set_mat4("projection", glm.value_ptr(projection))
        lamp_shader.set_mat4("view", glm.value_ptr(view))

        model = glm.mat4(1.0)
        model = glm.translate(model, light_pos)
        model = glm.scale(model, [.2, .2, .2])
        lamp_shader.set_mat4("model", glm.value_ptr(model))

        gl.glBindVertexArray(light_cube_vao)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 36)

        glfw.swap_buffers(window)
        glfw.poll_events()

    gl.glDeleteVertexArrays(1, id(cube_vao))
    gl.glDeleteVertexArrays(1, id(light_cube_vao))
    gl.glDeleteBuffers(1, id(vbo))
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
