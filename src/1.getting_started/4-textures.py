import glfw
import numpy as np
import OpenGL.GL as gl
from PIL import Image

from include.shader_old import Shader

# vertex shaders: determine vertex's position on the screen
# fragment shaders  or  named pixel shaders: determine pixel's color

def processInput(window):
    """
    process all input: query GLFW whether relevant keys are pressed/released this frame and react accordingly
    """
    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(window, True)   

def Tex(file_name):
    return r'res/textures/' + file_name

def main():
    # Initialize the library
    if not glfw.init():
        return
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(640, 480, "Hello World", None, None)
    if not window:
        glfw.terminate()
        return

    # set window's position
    glfw.set_window_pos(window, 400, 200)

    # Make the window's context current
    glfw.make_context_current(window)

    # OpenGL版本信息
    print(gl.glGetString(gl.GL_VERSION))

    my_shader = Shader(r'res/shaders/4-texture.shader')
    my_shader.use()

    # // set up vertex data (and buffer(s)) and configure vertex attributes
    # // ------------------------------------------------------------------
    vertices = [
        # position3f --- color3f --- texturecoords2f
         0.5,  0.5, 0.0,   1.0, 0.0, 0.0,   1.0, 1.0,   # 右上
         0.5, -0.5, 0.0,   0.0, 1.0, 0.0,   1.0, 0.0,   # 右下
        -0.5, -0.5, 0.0,   0.0, 0.0, 1.0,   0.0, 0.0,   # 左下
        -0.5,  0.5, 0.0,   1.0, 1.0, 0.0,   0.0, 1.0,   # 左上
    ]
    
    indices = [         # 索引, 指明使用的是顶点数组中的哪些顶点
        0, 1, 3,
        1, 2, 3,
    ]

    vertexData = np.array(vertices, np.float32)
    indexData = np.array(indices, np.uint32)
    print(vertexData[0].nbytes)

    vao = gl.glGenVertexArrays(1)
    vbo = gl.glGenBuffers(1)
    ibo = gl.glGenBuffers(1)
    gl.glBindVertexArray(vao)

    # vbo    
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, vertexData.nbytes, vertexData, gl.GL_STATIC_DRAW)
    
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 8 * vertexData[0].nbytes, gl.ctypes.c_void_p(0))
    gl.glEnableVertexAttribArray(0)

    gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 8 * vertexData[0].nbytes, gl.ctypes.c_void_p(3 * vertexData[0].nbytes))
    gl.glEnableVertexAttribArray(1)

    gl.glVertexAttribPointer(2, 2, gl.GL_FLOAT, gl.GL_FALSE, 8 * vertexData[0].nbytes, gl.ctypes.c_void_p(6 * vertexData[0].nbytes))
    gl.glEnableVertexAttribArray(2)

    # ibo
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ibo)
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indexData.nbytes, indexData, gl.GL_STATIC_DRAW)
    
    # load and create a texture
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


    # Loop until the user closes the window
    while not glfw.window_should_close(window):
        processInput(window)

        # Render here, e.g. using pyOpenGL
        gl.glClearColor(0.2, 0.3, 0.3, 1.0)    # 设置状态，背景色
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        gl.glBindTexture(gl.GL_TEXTURE_2D, texture)

        my_shader.use()
        gl.glBindVertexArray(vao)
        gl.glDrawElements(gl.GL_TRIANGLES, 6, gl.GL_UNSIGNED_INT, None)

        # Swap front and back buffers
        glfw.swap_buffers(window)

        # Poll for and process events
        glfw.poll_events()

    gl.glDeleteVertexArrays(1, id(vao))
    gl.glDeleteBuffers(1, id(vbo))
    gl.glDeleteBuffers(1, id(ibo))
    glfw.terminate()

if __name__ == "__main__":
    main()