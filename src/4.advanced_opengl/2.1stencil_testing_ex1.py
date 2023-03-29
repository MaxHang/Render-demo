import sys
import glm
import glfw
import OpenGL.GL as gl
from pathlib import Path
from pyrr import Vector3, Matrix44

from include.model import Model
from include.shader import Shader
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
    gl.glEnable(gl.GL_STENCIL_TEST)
    gl.glStencilOp(gl.GL_KEEP, gl.GL_KEEP, gl.GL_REPLACE)

    model = Model("res/objects/nanosuit/nanosuit.obj")
    model_shader = Shader("src/4.advanced_opengl/shaders/2.1.model_loading.vs", "src/4.advanced_opengl/shaders/2.1.model_loading.fs")
    single_color_shader = Shader("src/4.advanced_opengl/shaders/2.1.model_outline.vs", "src/4.advanced_opengl/shaders/2.shader_single_color.fs")
    
    # draw in wireframe
    # gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
    # sys.exit()

    while not glfw.window_should_close(window):
        # -- time logic
        current_frame = glfw.get_time()
        delta_time = current_frame - last_frame
        last_frame = current_frame

        # -- input
        process_input(window)

        # -- render
        gl.glClearColor(0.05, 0.05, 0.05, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT | gl.GL_STENCIL_BUFFER_BIT)

        # -- view.projection transformations
        projection = glm.perspective(glm.radians(camera.zoom), SRC_WIDTH/SRC_HEIGHT, 0.1, 100.0)
        view = camera.get_view_matrix()

        model_shader.use()

        model_shader.set_mat4("projection", glm.value_ptr(projection))
        model_shader.set_mat4("view", glm.value_ptr(view))

        # 启动模板缓冲的写入
        gl.glStencilFunc(gl.GL_ALWAYS, 1, 0xFF)
        gl.glStencilMask(0xFF)
        mmodel = glm.mat4(1.0)
        mmodel = glm.translate(mmodel, [0.0, -0.75, 0.0]) 
        mmodel = glm.scale(mmodel, [0.2, 0.2, 0.2]) 
        model_shader.set_mat4("model", glm.value_ptr(mmodel))
        model.draw(model_shader)

        # 渲染边界
        single_color_shader.use()
        single_color_shader.set_mat4("projection", glm.value_ptr(projection))
        single_color_shader.set_mat4("view", glm.value_ptr(view))
        gl.glStencilFunc(gl.GL_NOTEQUAL, 1, 0xFF)
        gl.glStencilMask(0x00)  # 禁止写入模板
        gl.glDisable(gl.GL_DEPTH_TEST)
        mmodel = glm.mat4(1.0)
        mmodel = glm.translate(mmodel, [0.0, -0.75, 0.0]) 
        mmodel = glm.scale(mmodel, [0.2, 0.2, 0.2]) 
        single_color_shader.set_mat4("model", glm.value_ptr(mmodel))
        model.draw(single_color_shader)

        gl.glEnable(gl.GL_DEPTH_TEST)

        glfw.swap_buffers(window)
        glfw.poll_events()

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
