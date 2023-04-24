#version 330 core

in vec3 viewSpacePos;
out vec4 FragColor;

uniform float particleRadius;
uniform mat4 projection;

void main()
{
	// FragColor = texture(sprite_texture, gl_PointCoord);
    FragColor = vec4(0.0, 0.0, 1.0, 1.0);
    vec3 normal;
    normal.xy = gl_PointCoord.xy * vec2(2.0, -2.0) + vec2(-1.0, 1.0);
    float r2  = dot(normal.xy, normal.xy);
    if(r2 > 1.0)
        discard;
    normal.z      = sqrt(1.0 - r2);
    FragColor.xyz = 0.5 * normal + 0.5;
}
