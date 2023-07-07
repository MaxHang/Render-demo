import os
from pathlib import Path

import OpenGL.GL as gl
from PIL import Image

RESOURCES    = Path(__file__).absolute().parent.parent.joinpath('resource')
FLOOR_DIR = RESOURCES.joinpath('floor')
SKYBOX_DIR   = RESOURCES.joinpath('skybox')
# SKYBOX_DIR   = RESOURCES.joinpath('Sky', 'sky01')
# SKYBOX_DIR   = RESOURCES.joinpath('Sky', 'sky02')
# SKYBOX_DIR   = RESOURCES.joinpath('Sky', 'sky04')
SKYBOX_DIR   = RESOURCES.joinpath('Sky', 'sky05')
# SKYBOX_DIR   = RESOURCES.joinpath('Sky', 'sky07')
# SKYBOX_DIR   = RESOURCES.joinpath('Sky', 'sky07')


def load_texture_2D(path,
                 mag_filter=gl.GL_LINEAR,
                 min_filter=gl.GL_LINEAR_MIPMAP_LINEAR,
                 wrap_s=gl.GL_REPEAT, wrap_t=gl.GL_REPEAT,
                 flip_y=False, flip_x=False,
                 generate_mipmaps=True):

    texture_id = gl.glGenTextures(1)
    img = Image.open(os.path.join(FLOOR_DIR, path))
    img = flip_image(img, flip_x, flip_y)

    format_ = {
        1 : gl.GL_RED,
        3 : gl.GL_RGB,
        4 : gl.GL_RGBA,
    }.get(len(img.getbands()))

    gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, format_, img.width, img.height, 0, format_, gl.GL_UNSIGNED_BYTE, img.tobytes())
    
    img.close()
    
    if generate_mipmaps:
        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

    # -- texture wrapping
    gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, wrap_s)
    gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, wrap_t)
    # -- texture filterting
    gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, min_filter)
    gl.glTexParameter(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, mag_filter)

    return texture_id


def flip_image(img, flip_y=False, flip_x=False):
    if flip_y:
        return img.transpose(Image.FLIP_TOP_BOTTOM)
    elif flip_x:
        return img.transpose(Image.FLIP_LEFT_RIGHT)
    return img


# loads a cubemap texture from 6 individual texture faces
# order:
# +X (right)
# -X (left)
# +Y (top)
# -Y (bottom)
# +Z (front) 
# -Z (back)
# -------------------------------------------------------
def load_cubemap(faces : list[str]) -> int:

    texture_id = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, texture_id)

    for i in range(len(faces)):
        try:
            img = Image.open(os.path.join(SKYBOX_DIR, faces[i]))

            gl.glTexImage2D(gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, gl.GL_RGB, img.width, img.height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, img.tobytes())

            img.close()
            
        except:
            print("Cubemap texture failed to load at path: " + faces[i])


    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_EDGE)

    return texture_id

def create_texture_2D(
    internal_format, 
    width, height, 
    src_format, 
    src_data_type, 
    min_filter=gl.GL_LINEAR,
    mag_filter=gl.GL_LINEAR,
    ):
    """创建纹理附件
    
    :param target_format: 把纹理存储为何种格式
    :param width
    :param height       : 纹理的size
    :param src_fromat   : 源图的格式
    :param src_data_type: 原图数据类型
    :param minfilter
    :param magfilter    : 纹理过滤方式

    :return: 纹理缓冲区的id
    """
    texture_id = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, internal_format, width, height, 0, src_format, src_data_type, None)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, min_filter)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, mag_filter)
    # borderColor = (0.0, 0.0, 0.0, 1.0)
    # gl.glTexParameterfv(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_BORDER_COLOR, borderColor); 
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE);
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE);
    return texture_id
