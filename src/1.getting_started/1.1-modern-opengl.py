import glfw
import numpy as np

from OpenGL.GL import *
from OpenGL.GL import shaders


# vertex shaders: determine vertex's position on the screen
# fragment shaders  or  named pixel shaders: determine pixel's color

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
    # glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    # glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    # glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    
    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(640, 480, "Hello World", None, None)
    if not window:
        glfw.terminate()
        return

    # Make the window's context current
    glfw.make_context_current(window)

    # OpenGL版本信息
    print(glGetString(GL_VERSION))

    FLOAT_BYTE = 4
    positions = [
        -0.5, -0.5, 0.0, 1.0, 0.0, 0.0,
         0.0,  0.5, 0.0, 0.0, 1.0, 0.0,
         0.5, -0.5, 0.0, 0.0, 0.0, 1.0,
    ]
    vertexData = np.array(positions, np.float32)
    # 表明需要一个缓冲区
    buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, buffer)
    # 缓冲区的大小与数据
    glBufferData(GL_ARRAY_BUFFER, vertexData.nbytes, vertexData, GL_STATIC_DRAW)

    # what is in the memory, and how its laid out
    # glVertexAttribPointer 
    '''
    顶点属性，假设现在顶点有 位置、颜色、纹理三个属性，分别是2维，3维，2维，且都是4字节的浮点数
    glVertexAttribPointer(	
        GLuint index,               属性的索引，位置就是0，颜色就是1，纹理就是2, 与vertex中layout loaction对应
        GLint size,                 属性的组件数量，例如位置是二维的就是2
        GLenum type,                属性组件的类型，例如float
        GLboolean normalized,       属性是否需要规则化，例如0-255 规则化为 0-1
        GLsizei stride,             顶点的偏移量，这里是(2+3+2)*4，简单来说就是这个属性第二次出现的地方到整个数组0位置之间有多少字节
        const GLvoid * pointer);    属性在顶点内的偏移量，这里位置是0，颜色是2*4，纹理是(2+3)*4
    从VBO管理的内存中获得数据，具体是那个VBO则是通过在调用glVertexAttribPointer时绑定到GL_ARRAY_BUFFER的VBO决定的
    '''
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, FLOAT_BYTE * 6, ctypes.c_void_p(0))
    # If enabled, the generic vertex attribute array is used when glDrawArrays, glMultiDrawArrays, glDrawElements, glMultiDrawElements, or glDrawRangeElements is called.
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, FLOAT_BYTE * 6, ctypes.c_void_p(12))
    # If enabled, the generic vertex attribute array is used when glDrawArrays, glMultiDrawArrays, glDrawElements, glMultiDrawElements, or glDrawRangeElements is called.
    glEnableVertexAttribArray(1)
    
    vertex_src, fragment_src = paerseShader(r'res/shaders/Basic.shader')
    print('VERTEX')
    print(vertex_src)
    print('FRAGMENT')
    print(fragment_src)
    shader_program = createShaderProgram(vertex_src, fragment_src)
    glUseProgram(shader_program)

    # Loop until the user closes the window
    while not glfw.window_should_close(window):
        # Render here, e.g. using pyOpenGL
        glClear(GL_COLOR_BUFFER_BIT)

        glDrawArrays(GL_TRIANGLES, 0, 3)

        # Swap front and back buffers
        glfw.swap_buffers(window)

        # Poll for and process events
        glfw.poll_events()


    # 删除program
    glDeleteProgram(shader_program)

    glfw.terminate()

if __name__ == "__main__":
    main()