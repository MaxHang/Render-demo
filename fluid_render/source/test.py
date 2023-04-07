import glfw

from include.shader import Shader

glfw.init()
glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

window = glfw.create_window(800, 600, "LearnOpenGL", None, None)
if not window:
    print("Window Creation failed!")
    glfw.terminate()

glfw.make_context_current(window)

# shader = Shader(r"fluid_render/shader/skybox.vs", r"fluid_render/shader/skybox.fs")
shader = Shader(r'src/my_src/shaders/1.2.point_sprite.vs', r'src/my_src/shaders/1.2.point_sprite.fs')

print(1)