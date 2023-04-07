import math

import glfw
import numpy as np
from OpenGL.GL import *
from OpenGL.GL import shaders

from include.IndexBuffer import IndexBuffer
from include.VertexBuffer import VertexBuffer

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

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(640, 480, "Hello World", None, None)
    if not window:
        glfw.terminate()
        return

    # set window's position
    glfw.set_window_pos(window, 400, 200)

    # Make the window's context current
    glfw.make_context_current(window)
    # V-Sync: 垂直同步
    glfw.swap_interval(1)

    # OpenGL版本信息
    print(glGetString(GL_VERSION))

    vertex_src, fragment_src = paerseShader(r'res/shaders/uniform-test.shader')
    shader_program = createShaderProgram(vertex_src, fragment_src)

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


    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    # vbo    
    vbo = VertexBuffer(positions)
    vbo.Bind()
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    # ibo
    ibo = IndexBuffer(indices)
    ibo.Bind()

    vbo.Unbind()
    glBindVertexArray(0); 

    glUseProgram(shader_program)
    # Loop until the user closes the window
    while not glfw.window_should_close(window):
        processInput(window)

        # Render here, e.g. using pyOpenGL
        glClearColor(0.2, 0.3, 0.3, 1.0)    # 设置状态，背景色
        glClear(GL_COLOR_BUFFER_BIT)

        
        time_value = glfw.get_time()
        greenValue = math.sin(time_value) / 2.0 + 0.5
        vertex_color_location = glGetUniformLocation(shader_program, 'u_Color')
        glUniform4f(vertex_color_location, 0.0, greenValue, 0.0, 1.0)

        glBindVertexArray(vao)
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

        # Swap front and back buffers
        glfw.swap_buffers(window)

        # Poll for and process events
        glfw.poll_events()

    glDeleteProgram(shader_program)
    glDeleteVertexArrays(1, vao)
    vbo.Delete()
    ibo.Delete()
    

    glfw.terminate()

if __name__ == "__main__":
    main()