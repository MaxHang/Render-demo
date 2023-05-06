import numpy as np
import OpenGL.GL as gl


class VertexBuffer:
    def __init__(self, data:np.ndarray=None , size:int=None):
        self.m_id = gl.glGenBuffers(1)

        if data is not None:
            self.set_vbo_data(data, size)

    def set_vbo_data(self, data, size=None):
        if size:
            size_used = size
        else:
            size_used = data.nbytes
        self.bind()
        gl.glBufferData(gl.GL_ARRAY_BUFFER, size_used, data, gl.GL_STATIC_DRAW)
        self.unbind()
    
    def bind(self):
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.m_id)

    def unbind(self):
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

    def delete(self):
        gl.glDeleteBuffers(1, id(self.m_id))