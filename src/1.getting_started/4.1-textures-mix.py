import glfw
import numpy as np
import OpenGL.GL as gl
from PIL import Image

from include.shader_old import Shader


def main():
    glfw.init()
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    window = glfw.create_window(800, 600, "LearnOpenGL", None, None)
    if not window:
        print("Window Creation failed!")
        glfw.terminate()

    glfw.make_context_current(window)
    glfw.set_window_size_callback(window, on_resize)

    shader = Shader(r'res/shaders/4-texture-mix.shader')

    vertices = [
     # positions         colors          tex_coords
     0.5,  0.5, 0.0,  1.0, 0.0, 0.0,  1.0, 1.0,  # top right
     0.5, -0.5, 0.0,  0.0, 1.0, 0.0,  1.0, 0.0,  # bottom right
    -0.5, -0.5, 0.0,  0.0, 0.0, 1.0,  0.0, 0.0,  # bottom left
    -0.5,  0.5, 0.0,  1.0, 1.0, 0.0,  0.0, 1.0,  # top left
    ]

    indices = [
        0, 1, 3,
        1, 2, 3
    ]

    vertices = np.array(vertices, np.float32)
    indices = np.array(indices, np.uint32)

    vao = gl.glGenVertexArrays(1)
    gl.glBindVertexArray(vao)

    vbo = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)

    ebo = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ebo)
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, gl.GL_STATIC_DRAW)

    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 8 * vertices[0].nbytes, gl.ctypes.c_void_p(0))
    gl.glEnableVertexAttribArray(0)

    gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 8 * vertices[0].nbytes, gl.ctypes.c_void_p(3 * vertices[0].nbytes))
    gl.glEnableVertexAttribArray(1)

    gl.glVertexAttribPointer(2, 2, gl.GL_FLOAT, gl.GL_FALSE, 8 * vertices[0].nbytes, gl.ctypes.c_void_p(6 * vertices[0].nbytes))
    gl.glEnableVertexAttribArray(2)

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

    while not glfw.window_should_close(window):
        process_input(window)

        gl.glClearColor(.2, .3, .3, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture1)
        gl.glActiveTexture(gl.GL_TEXTURE1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture2)

        shader.use()
        gl.glBindVertexArray(vao)
        gl.glDrawElements(gl.GL_TRIANGLES, 6, gl.GL_UNSIGNED_INT, gl.ctypes.c_void_p(0))

        glfw.poll_events()
        glfw.swap_buffers(window)

    gl.glDeleteVertexArrays(1, id(vao))
    gl.glDeleteBuffers(1, id(vbo))
    gl.glDeleteBuffers(1, id(ebo))
    glfw.terminate()


def on_resize(window, w, h):
    gl.glViewport(0, 0, w, h)


def process_input(window):
    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(window, True)


if __name__ == '__main__':
    main()
