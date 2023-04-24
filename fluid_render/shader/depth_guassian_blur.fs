# version 330 core

in vec2 texCoord;

uniform sampler2D depthTexture;
uniform int horizontal;

out float smoothDepth;

// const float weight[8] = float[] (0.197448, 0.174697, 0.120999, 0.065602, 0.02784, 0.009246, 0.002403, 0.000489);
const float weight[8] = float[] (0.19950134764464322, 0.17605932135785024, 0.12100368400046488, 0.06476860475414932, 0.02699957138957373, 0.008765477469243018, 0.0022162597803590165, 0.00043640742603817315);
// const float weight[13] = float[] (0.19947114025583798, 0.17603266343079443, 0.12098536229300463, 0.06475879785084124, 0.026995483264053932, 0.008764150249206145, 0.00221592420658135, 0.00043634134764345816, 6.691511290093393e-05, 7.991870555661203e-06, 7.433597575725681e-07, 5.3848800227596896e-08, 3.037941425751144e-09);

void main(){
    vec2 tex_offset = 1.0 / textureSize(depthTexture, 0);
    float result = texture(depthTexture, texCoord).r * weight[0];

    for (int i = 1; i < weight.length(); i++){
        result += texture(depthTexture, texCoord + vec2(tex_offset.x * i * horizontal, tex_offset.y * i * (1-horizontal))).r * weight[i];
        result += texture(depthTexture, texCoord - vec2(tex_offset.x * i * horizontal, tex_offset.y * i * (1-horizontal))).r * weight[i];
    }

    smoothDepth = result;
}

