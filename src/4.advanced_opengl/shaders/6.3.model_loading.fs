#version 330 core
out vec4 FragColor;

in vec3 Normal;
in vec3 Position;

uniform vec3 cameraPos;
uniform samplerCube skybox;

uniform sampler2D texture_diffuse1;

void main() {
    // FragColor = texture(texture_diffuse1, TexCoords);

    // 反射贴图
    // vec3 I = normalize(Position - cameraPos);
    // vec3 R = reflect(I, normalize(Normal));
    // FragColor = texture(skybox, R);

    // 折射贴图
    float ratio = 1.00 / 1.52;
    vec3 I = normalize(Position - cameraPos);
    vec3 R = refract(I, normalize(Normal), ratio);
    FragColor = texture(skybox, R);
}
