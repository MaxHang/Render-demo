#version 330 core

uniform float particleRadius;
uniform mat4 projection;

in vec3 viewSpacePos;   // 点精灵在摄像机空间中的中心点
out float viewSpaceDepth;   // 渲染viewZ到第1个颜色附件

/*
 * 首先通过点精灵像素纹理坐标计算得到像素在viewSpace中的法向量
 * 随后得到点精灵每个像素在视点空间中的坐标: viewSpacePos + normal * particleRadius
 * 然后再对视点空间中的坐标做投影变换, 随后进行透视除法, 便可以得到NDC空间中的深度值保存到深度可视纹理中
 */

void main(){
    vec3 normal;
    // 计算法向量
    normal.xy = gl_PointCoord.xy * vec2(2.0, -2.0) + vec2(-1.0, 1.0);
    float r2  = dot(normal.xy, normal.xy);
    if(r2 > 1.0)
        discard;        // kill pixels outside circle
    normal.z  = sqrt(1.0 - r2);

    // 计算点精灵像素在视点空间的坐标
    vec4 pixelViewSpacePos = vec4(viewSpacePos + normal * particleRadius, 1.0);
    // 坐投影变换、透视除法得到NDC空间深度值
    vec4 pixelClipSpacePos = projection * pixelViewSpacePos;
    float ndcZ             = pixelClipSpacePos.z / pixelClipSpacePos.w;
    // 根据ndcZ计算 gl_FragDepth, 参考http://www.songho.ca/opengl/gl_transform.html 以及 https://blog.csdn.net/fatcat123/article/details/103861403
    gl_FragDepth = 0.5*(gl_DepthRange.diff * ndcZ + gl_DepthRange.far  + gl_DepthRange.near);
    viewSpaceDepth = pixelViewSpacePos.z;
}

// void main(){
//     vec3 normal;
//     normal.xy = gl_PointCoord.xy * vec2(2.0, -2.0) + vec2(-1.0, 1.0);
//     float r2  = dot(normal.xy, normal.xy);
//     if(r2 > 1.0)
//         discard; 
//     normal.z  = sqrt(1.0 - r2);
//     float pixelDepth = viewSpacePos.z + normal.z * particleRadius;
// }