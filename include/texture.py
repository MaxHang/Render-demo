import os
from pathlib import Path

import OpenGL.GL as gl
from PIL import Image

RESOURCES = Path(__file__).absolute().parent.parent.joinpath('res')
TEXTURES_DIR = RESOURCES.joinpath('textures')
TEXTURES_SKYBOX_DIR = TEXTURES_DIR.joinpath('skybox')


def load_texture(path,
                 mag_filter=gl.GL_LINEAR,
                 min_filter=gl.GL_LINEAR_MIPMAP_LINEAR,
                 wrap_s=gl.GL_REPEAT, wrap_t=gl.GL_REPEAT,
                 flip_y=False, flip_x=False,
                 generate_mipmaps=True):

    textureID = gl.glGenTextures(1)
    img = Image.open(os.path.join(TEXTURES_DIR, path))
    img = flip_image(img, flip_x, flip_y)

    format_ = {
        1 : gl.GL_RED,
        3 : gl.GL_RGB,
        4 : gl.GL_RGBA,
    }.get(len(img.getbands()))

    gl.glBindTexture(gl.GL_TEXTURE_2D, textureID)
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

    return textureID


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

    textureID = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, textureID)

    for i in range(len(faces)):
        try:
            img = Image.open(os.path.join(TEXTURES_SKYBOX_DIR, faces[i]))

            gl.glTexImage2D(gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, gl.GL_RGB, img.width, img.height, 0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, img.tobytes())

            img.close()
            
        except:
            print("Cubemap texture failed to load at path: " + faces[i])


    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_CUBE_MAP, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_EDGE)

    return textureID