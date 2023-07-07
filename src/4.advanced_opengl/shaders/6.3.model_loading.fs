#version 330 core
out vec4 FragColor;

in vec3 Normal;
in vec3 Position;

uniform vec3 cameraPos;
uniform mat4 invView;
uniform samplerCube skybox;

uniform sampler2D texture_diffuse1;

void main() {
    // FragColor = texture(texture_diffuse1, TexCoords);

    // 反射贴图
    // vec3 I = normalize(Position);
    // vec3 R = reflect(I, normalize(Normal));
    // FragColor = texture(skybox, R);


    // positon Normal 摄像机空间的位置与法向量
    // vec3 worldPos = vec3(invView * vec4(Position, 1.0));
    // vec3 worldN   = transpose(inverse(mat3(invView))) * Normal;
    // vec3 I = normalize(worldPos - cameraPos);
    // vec3 R = reflect(I, normalize(worldN));
    // FragColor = vec4(texture(skybox, R).rgb, 1.0);

    vec3 normalVis = Normal * 0.5 + 0.5;
    FragColor = vec4(normalVis, 1.0);

    // vec3 I = normalize(Position);
    // vec3 R = reflect(I, normalize(Normal));
    // vec3 worldR = transpose(inverse(mat3(invView))) * R;
    // // vec3 worldR = vec3(invView * vec4(R, 1.0));
    // FragColor = vec4(texture(skybox, worldR).rgb, 1.0);


    // vec3 position = vec3(invView * vec4(Position, 1.0));
    // vec3 I = normalize(position - cameraPos);
    // vec3 R = reflect(I, normalize(Normal));
    // FragColor = texture(skybox, R);
    // vec3 I = normalize(Position - cameraPos);
    // vec3 R = reflect(I, normalize(Normal));
    // FragColor = texture(skybox, R);

    // 折射贴图
    // float ratio = 1.00 / 1.52;
    // vec3 I = normalize(Position - cameraPos);
    // vec3 R = refract(I, normalize(Normal), ratio);
    // FragColor = texture(skybox, R);
}
