import glfw
import numpy as np

from OpenGL.GL import *
from OpenGL.GL import shaders


# Vertex Array Object:  VAO
# Vertex Buffer Object: VBO
# Index Buffer Object:  IBO / EBO
# Element


# vertex shaders: determine vertex's position on the screen
# fragment shaders  or  named pixel shaders: determine pixel's color

def processInput(window):
    """
    process all input: query GLFW whether relevant keys are pressed/released this frame and react accordingly
    """
    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(window, True)

def paerseShader(file_path: str):
    """
    param:
        file_path: 存储shader文本程序的文件路径
    return:
        vertex_shader 与 fragment_shader
    """
    shader_type_dict = {
        'none': -1,
        'vertex': 0,
        'fragment': 1,
    }
    shader_source = [''] * 2
    cur_type = shader_type_dict['none']
    with open(file_path, 'r') as file_object:
        for line in file_object: # line带'\n'
            if '#shader' in line:
                if 'vertex' in line:
                    cur_type = shader_type_dict['vertex']
                else:
                    cur_type = shader_type_dict['fragment']
            else:
                shader_source[cur_type] += line
    
    return shader_source[0], shader_source[1]

def createShaderProgram(vertex_shader: str, fragment_shader: str):
    vs = shaders.compileShader(vertex_shader, GL_VERTEX_SHADER)
    fs = shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER)
    program = shaders.compileProgram(vs, fs)
    return program
    

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
    print(glGetString(GL_VERSION))

    FLOAT_BYTE = 4
    # positions = [
    #     -0.5, -0.5,
    #      0.5, -0.5,
    #      0.5,  0.5,

    #      0.5,  0.5,
    #     -0.5,  0.5,
    #     -0.5, -0.5,
    # ]

    vertex_src, fragment_src = paerseShader(r'res/shaders/Basic.shader')
    shader_program = createShaderProgram(vertex_src, fragment_src)
    glUseProgram(shader_program)

    # // set up vertex data (and buffer(s)) and configure vertex attributes
    # // ------------------------------------------------------------------
    positions = [
        -0.5, -0.5,     # 0     
         0.5, -0.5,     # 1
         0.5,  0.5,     # 2
        -0.5,  0.5,     # 3
    ]
    
    indices = [         # 索引, 指明使用的是顶点数组中的哪些顶点
        0, 1, 2,
        2, 3, 0,
    ]

    vertexData = np.array(positions, np.float32)
    indexData = np.array(indices, np.uint32)

    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    # 表明需要一个GL_ARRAY_BUFFER类型的缓冲区, vbo
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    # 把数组复制到当前绑定缓冲
    glBufferData(GL_ARRAY_BUFFER, vertexData.nbytes, vertexData, GL_STATIC_DRAW)
    
    # what is in the memory, and how its laid out
    # glVertexAttribPointer 
    # glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, FLOAT_BYTE * 2, ctypes.c_void_p(0))
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
    # If enabled, the generic vertex attribute array is used when glDrawArrays, glMultiDrawArrays, glDrawElements, glMultiDrawElements, or glDrawRangeElements is called.
    glEnableVertexAttribArray(0)

    # 索引缓冲区
    ibo = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo)
    # 缓冲区的大小与数据
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indexData.nbytes, indexData, GL_STATIC_DRAW)
    
    # note that this is allowed, the call to glVertexAttribPointer registered VBO as the vertex attribute's bound vertex buffer object so afterwards we can safely unbind
    glBindBuffer(GL_ARRAY_BUFFER, 0)

    # remember: do NOT unbind the EBO while a VAO is active as the bound element buffer object IS stored in the VAO; keep the EBO bound.
    # glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0);

    # You can unbind the VAO afterwards so other VAO calls won't accidentally modify this VAO, but this rarely happens. Modifying other
    # VAOs requires a call to glBindVertexArray anyways so we generally don't unbind VAOs (nor VBOs) when it's not directly necessary.
    glBindVertexArray(0)

    

    # Loop until the user closes the window
    while not glfw.window_should_close(window):
        processInput(window)

        # Render here, e.g. using pyOpenGL
        glClear(GL_COLOR_BUFFER_BIT)

        glBindVertexArray(vao)

        # glDrawArrays(GL_TRIANGLES, 0, 6)
        # 具有索引
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

        # Swap front and back buffers
        glfw.swap_buffers(window)

        # Poll for and process events
        glfw.poll_events()

    # optional: de-allocate all resources once they've outlived their purpose:
    # ------------------------------------------------------------------------
    # glDeleteVertexArrays(1, vao)
    # glDeleteBuffers(1, vbo)
    # glDeleteBuffers(1, ibo)
    # 删除program
    glDeleteProgram(shader_program)

    glfw.terminate()

if __name__ == "__main__":
    main()