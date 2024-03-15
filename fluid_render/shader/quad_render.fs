#version 330 core

in vec2 texCoord;

uniform vec4 activateSSFFluid;
uniform sampler2D fluid1SSFTexture;
uniform sampler2D fluid2SSFTexture;
uniform sampler2D fluid3SSFTexture;
uniform sampler2D fluid4SSFTexture;

out vec4 FragColor;

void main()
{
    vec3 color1 = texture(fluid1SSFTexture, texCoord).rgb;
    vec3 color2 = texture(fluid2SSFTexture, texCoord).rgb;
    vec3 color3 = texture(fluid3SSFTexture, texCoord).rgb;
    vec3 color4 = texture(fluid4SSFTexture, texCoord).rgb;

    FragColor.rgb = color1 * activateSSFFluid.x + color2 * activateSSFFluid.y + color3 * activateSSFFluid.z + color4 * activateSSFFluid.w;
    FragColor.a = 1.0;
}