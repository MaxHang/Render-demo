import OpenGL.GL as gl
from OpenGL.GL import shaders

class Shader:

    def __init__(self, file_path) -> None:
        vs, fs = self.paerseShader(file_path)
        self.ID = self.createShaderProgram(vs, fs)
    
    def use(self):
        gl.glUseProgram(self.ID)

    def set_bool(self, name, value):
        gl.glUniform1i(gl.glGetUniformLocation(self.ID, name), value)

    def set_int(self, name, value):
        gl.glUniform1i(gl.glGetUniformLocation(self.ID, name), value)

    def set_float(self, name, value):
        gl.glUniform1f(gl.glGetUniformLocation(self.ID, name), value)

    def set_vec2(self, name, value):
        gl.glUniform2fv(gl.glGetUniformLocation(self.ID, name), 1, value)

    def set_vec3(self, name, value):
        gl.glUniform3fv(gl.glGetUniformLocation(self.ID, name), 1, value)

    def set_vec4(self, name, value):
        gl.glUniform4fv(gl.glGetUniformLocation(self.ID, name), 1, value)

    def set_mat3(self, name, value):
        gl.glUniformMatrix3fv(gl.glGetUniformLocation(self.ID, name), 1, gl.GL_FALSE, value)

    def set_mat4(self, name, value):
        gl.glUniformMatrix4fv(gl.glGetUniformLocation(self.ID, name), 1, gl.GL_FALSE, value)

    def paerseShader(self, file_path: str):
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
            for line in file_object: # line '\n'
                if '#shader' in line:
                    if 'vertex' in line:
                        cur_type = shader_type_dict['vertex']
                    else:
                        cur_type = shader_type_dict['fragment']
                else:
                    shader_source[cur_type] += line
        
        return shader_source[0], shader_source[1]
    
    def createShaderProgram(self, vertex_shader: str, fragment_shader: str):
        vs = shaders.compileShader(vertex_shader, gl.GL_VERTEX_SHADER)
        fs = shaders.compileShader(fragment_shader, gl.GL_FRAGMENT_SHADER)
        program = shaders.compileProgram(vs, fs)
        return program



