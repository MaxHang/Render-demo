import os
from pathlib import Path

import glm
import OpenGL.GL as gl
from OpenGL.GL import shaders

SHADER_DIR = Path(__file__).absolute().parent.parent.joinpath('shader')

class Shader:

    def __init__(self, vertex_path, fragment_path, geometry_path=None):
        self.m_id = shaders.compileProgram(
            shaders.compileShader(self._load(vertex_path), gl.GL_VERTEX_SHADER),
            shaders.compileShader(self._load(fragment_path), gl.GL_FRAGMENT_SHADER),
        )

    def _load(self, path):
        path = os.path.join(SHADER_DIR, path)
        shader_source = ""
        with open(path, 'r', encoding='utf-8', errors='ignore') as shader_file:
            shader_source = shader_file.readlines()
        return shader_source

    def use(self):
        gl.glUseProgram(self.m_id)

    def set_bool(self, name, value):
        gl.glUniform1i(gl.glGetUniformLocation(self.m_id, name), value)

    def set_int(self, name, value):
        gl.glUniform1i(gl.glGetUniformLocation(self.m_id, name), value)

    def set_float(self, name, value):
        gl.glUniform1f(gl.glGetUniformLocation(self.m_id, name), value)

    def set_vec2(self, name, value):
        gl.glUniform2fv(gl.glGetUniformLocation(self.m_id, name), 1, glm.value_ptr(value))

    def set_vec3(self, name, value):
        gl.glUniform3fv(gl.glGetUniformLocation(self.m_id, name), 1, glm.value_ptr(value))

    def set_vec4(self, name, value):
        gl.glUniform4fv(gl.glGetUniformLocation(self.m_id, name), 1, glm.value_ptr(value))

    def set_mat3(self, name, value):
        gl.glUniformMatrix3fv(gl.glGetUniformLocation(self.m_id, name), 1, gl.GL_FALSE, glm.value_ptr(value))

    def set_mat4(self, name, value):
        gl.glUniformMatrix4fv(gl.glGetUniformLocation(self.m_id, name), 1, gl.GL_FALSE, glm.value_ptr(value))
