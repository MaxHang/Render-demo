#version 330 core

layout (location = 0) in vec3 aPos;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

uniform float particleRadius;  // 粒子半径
uniform float pointScale; // 粒子在屏幕空间中的深度值

out vec3 viewSpacePos;      // 粒子在视点空间的坐标

void main(){
    vec4 viewSpacePosVec4 = view * vec4(aPos, 1.0f);
    viewSpacePos          = viewSpacePosVec4.xyz;
    // 根据相似三角形原理设置点精灵在屏幕空间中的大小
    gl_PointSize = particleRadius * (-pointScale / viewSpacePos.z);
    // TODO: 这里可以根据密度防止单个粒子的显示 

    gl_Position  = projection * viewSpacePosVec4;
}