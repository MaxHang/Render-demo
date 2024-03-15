#version 330 core

struct PointLight{
    vec3 position;
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;

    // 光线强度衰减 kc + kl*d + kq * d * d
    float constant;
    float linear;
    float quadratic;
};

struct Material{
    vec3  ambient;
    vec3  diffuse;
    vec3  specular;
    float shininess;
};

in vec3 viewSpacePos;
out vec4 FragColor;

uniform float particleRadius;
uniform vec3 cameraPosition;
uniform mat4 view;
uniform mat4 projection;
uniform PointLight pointLight;
// uniform Material   material;

void main()
{
	// FragColor = texture(sprite_texture, gl_PointCoord);
    FragColor = vec4(0.0f, 0.0f, 0.8f, 1.0f);
    vec3 normal;
    // calculate viewSpace sphere normal from texture coordinates
    normal.xy = gl_PointCoord.xy * vec2(2.0, -2.0) + vec2(-1.0, 1.0);
    float r2  = dot(normal.xy, normal.xy);
    if(r2 > 1.0)
        discard;
    normal.z      = sqrt(1.0 - r2);
    vec3 pixelViewSpacePos  = viewSpacePos + normal * particleRadius;
    vec3 pointLightPos      = (view * vec4(pointLight.position, 1.0)).xyz;
    vec3 lightDir = normalize(pointLightPos - pixelViewSpacePos);
    vec3 viewDir  = normalize(-pixelViewSpacePos);
    vec3 halfDir  = normalize(lightDir + viewDir);
    // ambient
    vec3 ambient = pointLight.ambient * FragColor.rgb;
    // diffuse
    float diff   = max(dot(lightDir, normal), 0.0);
    vec3 diffuse = diff * pointLight.diffuse * FragColor.rgb;
    // sepcular
    float spec    = pow(max(dot(normal, halfDir), 0.0), 8.0);
    vec3 specular = spec * pointLight.specular * vec3(1.0);

    // attenuation
    float dist = length(pointLightPos - pixelViewSpacePos);
    float attenuation = 1.0 / (pointLight.constant + pointLight.linear * dist + pointLight.quadratic * (dist * dist));

    diffuse  *= attenuation;
    specular *= attenuation;

    FragColor.rgb = ambient + diffuse + specular;
    // FragColor.rgb = ambient + diffuse;

    // gamma correction.
	// const float gamma = 2.2f;
	// FragColor.rgb     = pow(FragColor.rgb, vec3(1.0f/gamma));

    // // 法线可视化
    // normal = normalize(normal);
    // FragColor.xyz = 0.5 * normal + 0.5;
    // FragColor.xyz = normal;
}
