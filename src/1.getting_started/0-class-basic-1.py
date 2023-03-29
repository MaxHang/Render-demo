import glfw
import numpy as np

import OpenGL.GL as gl

from include.shader_old import Shader

# vertex shaders: determine vertex's position on the screen
# fragment shaders  or  named pixel shaders: determine pixel's color

def processInput(window):
    """
    process all input: query GLFW whether relevant keys are pressed/released this frame and react accordingly
    """
    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(window, True)    

def main():
    # Initialize the library
    if not glfw.init():
        return

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

    my_shader = Shader(r'res/shaders/Basic.shader')
    my_shader.use()

    # // set up vertex data (and buffer(s)) and configure vertex attributes
    # // ------------------------------------------------------------------
    vertices = [
        -0.5, -0.5,     # 0     
         0.5, -0.5,     # 1
         0.0,  0.5,     # 2
    ]
    
    indices = [         # 索引, 指明使用的是顶点数组中的哪些顶点
        0, 1, 2,
    ]

    vertexData = np.array(vertices, np.float32)
    indexData = np.array(indices, np.uint32)

    vao = gl.glGenVertexArrays(1)
    vbo = gl.glGenBuffers(1)
    ibo = gl.glGenBuffers(1)
    gl.glBindVertexArray(vao)

    # vbo    
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, vertexData.nbytes, vertexData, gl.GL_STATIC_DRAW)
    
    gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, gl.ctypes.c_void_p(0))
    gl.glEnableVertexAttribArray(0)

    # ibo
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ibo)
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indexData.nbytes, indexData, gl.GL_STATIC_DRAW)
    
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
    gl.glBindVertexArray(0); 

    # Loop until the user closes the window
    while not glfw.window_should_close(window):
        processInput(window)

        # Render here, e.g. using pyOpenGL
        gl.glClearColor(0.2, 0.3, 0.3, 1.0)    # 设置状态，背景色
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        gl.glBindVertexArray(vao)

        gl.glDrawElements(gl.GL_TRIANGLES, 3, gl.GL_UNSIGNED_INT, None)

        # Swap front and back buffers
        glfw.swap_buffers(window)

        # Poll for and process events
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()