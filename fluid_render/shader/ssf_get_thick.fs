#version 330 core

in vec3 viewSpacePos;

uniform float particleRadius;

out float thickness;

void main(){
    vec3 normal;
    normal.xy = gl_PointCoord.xy * vec2(2.0, -2.0) + vec2(-1.0, 1.0);
    float r2 = dot(normal.xy, normal.xy);
    if(r2 > 1.0)
        discard;
    normal.z = sqrt(1.0 - r2);

    // 计算粒子的厚度值, 由于采用点精灵绘制流体粒子, 其厚度从中心到边缘逐渐减少, 采用normal的z分量作为厚度值, 并且乘以一个缩放系数
    thickness = 2.0 * particleRadius * normal.z;
}