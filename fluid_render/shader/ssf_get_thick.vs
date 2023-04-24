#version 330 core

layout (location = 0) in vec3 aPos;

uniform mat4 model; // 一般为单位矩阵, 可以不参与运算
uniform mat4 view;
uniform mat4 projection;

uniform float particleRadius;
uniform float pointScale;

out vec3 viewSpacePos;

void main(){
    vec4 viewSpacePosVec4 = view * vec4(aPos, 1.0);
    viewSpacePos          = viewSpacePosVec4.xyz;

    gl_PointSize = particleRadius* (-pointScale / viewSpacePos.z);
    gl_Position = projection * viewSpacePosVec4;
}