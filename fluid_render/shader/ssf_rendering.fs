# version 330 core

in vec2 texCoord;

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


uniform int shaderOption;
uniform float near;
uniform float far;
uniform float R0;
uniform float refractiveIndex;
// uniform vec3 cameraPosition;
uniform mat4 view;
uniform mat4 projection;
uniform mat4 inProjection;
uniform sampler2D depthTexture;
uniform sampler2D thickTexture;
uniform sampler2D normalTexture;
uniform sampler2D backGroundTexture;
uniform samplerCube skyboxTexture;
uniform sampler2D   fluidFracTexture;
uniform PointLight light;
uniform Material material;

out vec4 FragColor;

float linearize_depth(float ndcZ) 
{
    return (2.0 * near * far) / (far + near - ndcZ * (far - near));	
}

float cal_fresnel_R(float R0, float costheta){
    float fresnelRatio = clamp(R0 + (1 - R0) * pow(1.0 - costheta, 5), 0, 1);
    return fresnelRatio;
}

vec3 uvToEye(vec2 texCoord, float depth){
    // back to ndc
    vec2 pos   = texCoord * 2.0 - 1.0;
    // viewSpaceZ to ndcZ
    float ndcZ = ((far + near) / (far - near) * depth + 2.0 * far * near / (far - near)) / depth;

    vec4 ndcPos  = vec4(pos.x, pos.y, ndcZ, 1.0);
    vec4 viewPos = inProjection * ndcPos;
    return viewPos.xyz / viewPos.w;
}

#define RENDER_BLUE

#ifdef RENDER_BLUE
const float k_r = 0.5f;
const float k_g = 0.2f;
const float k_b = 0.05f;
#else
// const float k_r = 0.8f;
// const float k_g = 0.2f;
// const float k_b = 0.9f;
const float k_r = 0.5f;
const float k_g = 0.05f;
const float k_b = 0.2f;
#endif

vec3 computeAttennuation(float thickness)
{
    // thickness *= 2;
    return vec3(exp(-k_r * thickness), exp(-k_g * thickness), exp(-k_b * thickness));
}

vec3 computeAttennuationMulti(float thickness)
{
    // thickness *= 2;
    float fluid1_k_r = 0.05;
    float fluid1_k_g = 0.2;
    float fluid1_k_b = 0.5;
    float fluid2_k_r = 0.2f;
    float fluid2_k_g = 0.05f;
    float fluid2_k_b = 0.5f;
    // float fluid1_k_r = 0.5;
    // float fluid1_k_g = 0.2;
    // float fluid1_k_b = 0.05;
    // float fluid2_k_r = 0.5f;
    // float fluid2_k_g = 0.05f;
    // float fluid2_k_b = 0.2f;
    float k_r, k_g, k_b;
    vec2  frac = normalize(texture(fluidFracTexture, texCoord).rg);
    k_r = fluid1_k_r * frac.x + fluid2_k_r * frac.y;
    k_g = fluid1_k_g * frac.x + fluid2_k_g * frac.y;
    k_b = fluid1_k_b * frac.x + fluid2_k_b * frac.y;
    // k_r = fluid1_k_r * 1.0 + fluid2_k_r * 0.0;
    // k_g = fluid1_k_g * 1.0 + fluid2_k_g * 0.0;
    // k_b = fluid1_k_b * 1.0 + fluid2_k_b * 0.0;
    return vec3(exp(-k_r * thickness), exp(-k_g * thickness), exp(-k_b * thickness));
}

vec3 computeAttennuation1(float thickness)
{
    // thickness *= 2;
    float fluid1_k_r = 0.5;
    float fluid1_k_g = 0.2;
    float fluid1_k_b = 0.05;
    float fluid2_k_r = 0.5f;
    float fluid2_k_g = 0.05f;
    float fluid2_k_b = 0.2f;
    float k_r, k_g, k_b;
    k_r = fluid1_k_r;
    k_g = fluid1_k_g;
    k_b = fluid1_k_b;
    return vec3(exp(-k_r * thickness), exp(-k_g * thickness), exp(-k_b * thickness));
}

vec3 computeAttennuation2(float thickness)
{
    // 需要每个像素的流相因子占比
    // thickness *= 2;
    float fluid1_k_r = 0.5;
    float fluid1_k_g = 0.2;
    float fluid1_k_b = 0.05;
    float fluid2_k_r = 0.5f;
    float fluid2_k_g = 0.05f;
    float fluid2_k_b = 0.2f;
    float k_r, k_g, k_b;
    k_r = fluid2_k_r;
    k_g = fluid2_k_g;
    k_b = fluid2_k_b;
    return vec3(exp(-k_r * thickness), exp(-k_g * thickness), exp(-k_b * thickness));
}

void rendering_depth(){
    // float viewZ = -texture(depthTexture, texCoord).r;
    // if (viewZ > far - 0.1){
    //     FragColor = vec4(0.0, 0.0, 0.0, 1.0);
    // }
    // else{
    //     float vis_far = 9.9;
    //     if (viewZ > vis_far){
    //         FragColor = vec4(vec3(1.0), 1.0);
    //     }
    //     else{
    //         viewZ     = (viewZ - near) / (vis_far - near);
    //         FragColor = vec4(vec3(viewZ), 1.0);
    //     }
    // }
    float z = -texture(depthTexture, texCoord).r;
    z /= 2;
    z = exp(z) / (exp(z) + 1);
    z = (z - 0.5) * 2;
    FragColor = vec4(z, z, z, 1);

    // float z = -texture(depthTexture, texCoord).r;
    // z /= 5;
    // z = (z - 0.5) * 2;
    // FragColor = vec4(z, z, z, 1);
}

void rendering_thick(){
    float thick = texture(thickTexture, texCoord).r;

    thick = exp(thick) / (exp(thick) + 1);
	thick = (thick - 0.5) * 2;
	FragColor = vec4(thick, thick, thick, 1.0);
}

void rendering_normal(){
    vec3 normalVis = texture(normalTexture, texCoord).xyz * 0.5 + 0.5;
    // vec3 normalVis = texture(normalTexture, texCoord).xyz;
    FragColor = vec4(normalVis, 1.0);
}

void rendering_fresnel(){
    float viewDepth = texture(depthTexture, texCoord).r;
    vec3 viewPos    = uvToEye(texCoord, viewDepth);
    vec3 viewDir    = normalize(-viewPos);

    vec3 N          = texture(normalTexture, texCoord).xyz;
    float fresnelRatio    = cal_fresnel_R(R0, dot(viewDir, N));

    FragColor = vec4(vec3(fresnelRatio), 1.0);
}

void rendering_reflect(){
    float viewDepth = texture(depthTexture, texCoord).r;
    vec3 viewPos    = uvToEye(texCoord, viewDepth);
    vec3 viewDir    = normalize(-viewPos);

    vec3 N          = texture(normalTexture, texCoord).xyz;
    float thickness = texture(thickTexture, texCoord).r;

    vec3  lightDir = normalize(vec3(view * vec4(light.position, 1.0)) - viewPos);
    vec3  H        = normalize(lightDir + viewDir);
    float specular = pow(max(0.0, dot(H, N)), material.shininess);

    float fresnelRatio    = cal_fresnel_R(R0, dot(viewDir, N));
    vec3 colorAttennuation = computeAttennuation(thickness * 0.5f);
    
    vec3 reflectionDir    = reflect(-viewDir, N);
    vec3 reflectionColor  = texture(skyboxTexture, reflectionDir).rgb;

    FragColor = vec4(mix(vec3(0.0), reflectionColor, fresnelRatio) + material.specular * specular, 1.0);
}

void rendering_refract(){
    float viewDepth = texture(depthTexture, texCoord).r;
    vec3 viewPos    = uvToEye(texCoord, viewDepth);
    vec3 viewDir    = normalize(-viewPos);

    vec3 N          = texture(normalTexture, texCoord).xyz;
    float thickness = texture(thickTexture, texCoord).r;
    float fresnelRatio    = cal_fresnel_R(R0, dot(viewDir, N));
    vec3 colorAttennuation = computeAttennuation(thickness * 0.5f);

    vec3 refractionDir   = refract(-viewDir, N, 1.0 / refractiveIndex);
    vec3 refractionColor = colorAttennuation * vec3(texture(backGroundTexture, texCoord + refractionDir.xy * 0.2));

    FragColor = vec4(mix(refractionColor, vec3(0.0), fresnelRatio), 1.0);
}

void rendering_BlinnPhong(){
    vec3  N         = texture(normalTexture, texCoord).xyz;
    float viewDepth = texture(depthTexture, texCoord).r;
    vec3  viewPos   = uvToEye(texCoord, viewDepth);
    vec3  viewDir   = normalize(-viewPos);

    vec3  lightDir = normalize(vec3(view * vec4(light.position, 1.0)) - viewPos);
    vec3  H        = normalize(lightDir + viewDir);
    float specular = pow(max(0.0, dot(H, N)), material.shininess);
    // float specular = 0;
    float diffuse  = max(0.0, dot(lightDir, N)) * 1.0;

    FragColor = vec4(material.ambient + material.diffuse * diffuse + material.specular * specular + vec3(0.0, 0.0, 0.2), 1.0);
}

void rendering_Full(){
    float viewDepth = texture(depthTexture, texCoord).r;
    vec3 viewPos    = uvToEye(texCoord, viewDepth);
    vec3 viewDir    = normalize(-viewPos);

    vec3 N          = texture(normalTexture, texCoord).xyz;
    float thickness = texture(thickTexture, texCoord).r;

    vec3  lightDir = normalize(vec3(view * vec4(light.position, 1.0)) - viewPos);
    vec3  H        = normalize(lightDir + viewDir);
    float specular = pow(max(0.0, dot(H, N)), material.shininess);

    float fresnelRatio    = cal_fresnel_R(R0, dot(viewDir, N));
    vec3 colorAttennuation = computeAttennuation(thickness);
    vec3 reflectionDir   = reflect(-viewDir, N);
    vec3 reflectionColor = texture(skyboxTexture, reflectionDir).rgb;
    vec3 refractionDir   = refract(-viewDir, N, 1.0 / refractiveIndex);
    vec3 refractionColor = colorAttennuation * vec3(texture(backGroundTexture, texCoord + refractionDir.xy * 0.2));

    FragColor = vec4(mix(refractionColor, reflectionColor, fresnelRatio) + material.specular * specular, 1.0);
}

void rendering_Multi_Fluid(){
    float viewDepth = texture(depthTexture, texCoord).r;
    vec3 viewPos    = uvToEye(texCoord, viewDepth);
    vec3 viewDir    = normalize(-viewPos);

    vec3 N          = texture(normalTexture, texCoord).xyz;
    float thickness = texture(thickTexture, texCoord).r;

    vec3  lightDir = normalize(vec3(view * vec4(light.position, 1.0)) - viewPos);
    vec3  H        = normalize(lightDir + viewDir);
    float specular = pow(max(0.0, dot(H, N)), material.shininess);

    float fresnelRatio    = cal_fresnel_R(R0, dot(viewDir, N));
    vec3 colorAttennuation = computeAttennuationMulti(thickness);
    vec3 reflectionDir   = reflect(-viewDir, N);
    vec3 reflectionColor = texture(skyboxTexture, reflectionDir).rgb;
    vec3 refractionDir   = refract(-viewDir, N, 1.0 / refractiveIndex);
    vec3 refractionColor = colorAttennuation * vec3(texture(backGroundTexture, texCoord + refractionDir.xy * 0.2));

    FragColor = vec4(mix(refractionColor, reflectionColor, fresnelRatio) + material.specular * specular, 1.0);
}

void rendering_Multi_Fluid_2(){
    float viewDepth = texture(depthTexture, texCoord).r;
    vec3 viewPos    = uvToEye(texCoord, viewDepth);
    vec3 viewDir    = normalize(-viewPos);

    vec3 N          = texture(normalTexture, texCoord).xyz;
    float thickness = texture(thickTexture, texCoord).r;

    vec3  lightDir = normalize(vec3(view * vec4(light.position, 1.0)) - viewPos);
    vec3  H        = normalize(lightDir + viewDir);
    float specular = pow(max(0.0, dot(H, N)), material.shininess);

    float fresnelRatio      = cal_fresnel_R(R0, dot(viewDir, N));
    vec3 colorAttennuation1 = computeAttennuation1(thickness);
    vec3 colorAttennuation2 = computeAttennuation2(thickness);
    vec2  fluidFrac         = normalize(texture(fluidFracTexture, texCoord).rg);

    vec3 reflectionDir   = reflect(-viewDir, N);
    vec3 reflectionColor = texture(skyboxTexture, reflectionDir).rgb;
    vec3 refractionDir   = refract(-viewDir, N, 1.0 / refractiveIndex);
    vec3 refractionColor = colorAttennuation1 * vec3(texture(backGroundTexture, texCoord + refractionDir.xy * 0.2)) * fluidFrac.x 
                         + colorAttennuation2 * vec3(texture(backGroundTexture, texCoord + refractionDir.xy * 0.2)) * fluidFrac.y;

    FragColor = vec4(mix(refractionColor, reflectionColor, fresnelRatio) + material.specular * specular, 1.0);
}

void rendering_Full_without_thick(){
    float viewDepth = texture(depthTexture, texCoord).r;
    vec3 viewPos    = uvToEye(texCoord, viewDepth);
    vec3 viewDir    = normalize(-viewPos);

    vec3 N          = texture(normalTexture, texCoord).xyz;

    vec3  lightDir = normalize(vec3(view * vec4(light.position, 1.0)) - viewPos);
    vec3  H        = normalize(lightDir + viewDir);
    float specular = pow(max(0.0, dot(H, N)), material.shininess);

    float fresnelRatio    = cal_fresnel_R(R0, dot(viewDir, N));
    vec3 reflectionDir   = reflect(-viewDir, N);
    vec3 reflectionColor = texture(skyboxTexture, reflectionDir).rgb;
    vec3 refractionDir   = refract(-viewDir, N, 1.0 / refractiveIndex);
    vec3 refractionColor = vec3(texture(backGroundTexture, texCoord + refractionDir.xy * 0.2));

    FragColor = vec4(mix(refractionColor, reflectionColor, fresnelRatio) + material.specular * specular, 1.0);
}

void rendering_Attenuation(){
    float thickness = texture(thickTexture, texCoord).r;
    vec3 colorAttennuation = computeAttennuation(thickness);

    FragColor = vec4(colorAttennuation, 1.0);
}

void main(){
    // ze to z_ndc to gl_FragDepth
	// REF: https://computergraphics.stackexchange.com/questions/6308/why-does-this-gl-fragdepth-calculation-work?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
	// float viewZ = texture(depthTexture, texCoord).r;
	// float ndcZ  = ((far + near) / (far - near) * viewZ + 2.0 * far * near / (far - near)) / viewZ;
	// gl_FragDepth = 0.5 * (gl_DepthRange.diff * ndcZ + gl_DepthRange.far + gl_DepthRange.near);	

    if(shaderOption == 1)
        rendering_depth();
    else if (shaderOption == 2)
        rendering_thick();
    else if (shaderOption == 3)
        rendering_normal();
    else if (shaderOption == 4)
        rendering_fresnel();
    else if (shaderOption == 5)
        rendering_reflect();
    else if (shaderOption == 6)
        rendering_refract();
    else if (shaderOption == 7)
        rendering_BlinnPhong();
    else if (shaderOption == 8)
        rendering_Multi_Fluid();
    else if (shaderOption == 9)
        rendering_Multi_Fluid_2();
    else if (shaderOption == 10)
        rendering_Attenuation();
    else
        rendering_Full();

    // // gamma correction.
	// const float gamma = 2.2f;
	// FragColor.rgb     = pow(FragColor.rgb, vec3(1.0f/gamma));
}