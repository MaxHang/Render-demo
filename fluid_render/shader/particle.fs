#version 330 core
out vec4 FragColor;

uniform mat4 projection;

in vec3 viewSpacePos;

void main()
{
	// FragColor = texture(sprite_texture, gl_PointCoord);
    vec3 normal;
    // back to ndc cood
    normal.xy = gl_PointCoord.xy * vec2(2.0, -2.0) + vec2(-1.0, 1.0);
    float r2 = dot(normal.xy, normal.xy);
    if(r2 > 1.0)
        discard;

    FragColor = vec4(0.0, 0.0, 1.0, 1.0);
}
