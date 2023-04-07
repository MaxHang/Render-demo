#version 330 core
layout (location = 0) in vec3 aPos;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

uniform float pointRadius;    // 视点空间中的粒子大小
uniform float screenPointZ; // 屏幕空间中的深度值

out vec3 viewSpacePos;       // 视点空间的点坐标

void main()
{
    vec4 viewSpacePos_vec4 = view * model * vec4(aPos, 1.0f);
    viewSpacePos = viewSpacePos_vec4.xyz;
    float dist = length(vec3(viewSpacePos_vec4 / viewSpacePos_vec4.w));
    // 根据相似三角形原理设置点精灵的大小
    gl_PointSize = pointRadius * (screenPointZ / dist);
	gl_Position = projection * view * model * vec4(aPos, 1.0f);
}