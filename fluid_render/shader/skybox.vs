#version 330 core
layout (location = 0) in vec3 aPos;

out vec3 TexCoords;

uniform mat4 projection;
uniform mat4 view;

void main()
{
    TexCoords = aPos;
    vec4 pos = gl_Position = projection * view * vec4(aPos, 1.0);
    gl_Position = pos.xyww; // 优化, 将z值改为w值, 这样在经过透视除法之后, 所有点的深度值都为1.0, 即最大深度值
}