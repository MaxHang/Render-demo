import numpy as np
from OpenGL.GL import *


class VertexBuffer:
    def __init__(self, data, size = None):
        np_data = np.array(data, np.float32)

        self.id = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.id)
        glBufferData(GL_ARRAY_BUFFER, np_data.nbytes, np_data, GL_STATIC_DRAW)
    
    def Bind(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.id)

    def Unbind(self):
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def Delete(self):
        glDeleteBuffers(1, self.id)
