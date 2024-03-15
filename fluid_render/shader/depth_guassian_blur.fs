# version 330 core

in vec2 texCoord;

uniform int horizontal;
uniform int MaxFilterSize;
uniform int filterSize;
uniform float zoom;
uniform float screenHeight;
uniform float particleRadius;
uniform sampler2D depthTexture;

out float smoothDepth;

float compute_weight1D(float r, float two_sigma2)
{
    return exp(-r * r / two_sigma2);
}

void main(){
    vec2  tex_offset = 1.0 / textureSize(depthTexture, 0);
    vec4  dtc = (horizontal == 0) ? vec4(tex_offset.x, 0, -tex_offset.x, 0) : vec4(0, tex_offset.y, 0, -tex_offset.y);
    float pixelDepth = texture(depthTexture, texCoord).r;

    float ratio      = screenHeight / 2.0 / tan(zoom / 2.0);
    float K          = -filterSize * ratio * particleRadius * 0.1;
    int   filterSize_pixel = min(MaxFilterSize, int(ceil(K / pixelDepth)));
    float sigma      = filterSize_pixel / 3.0f;
    float two_sigma2 = 2.0f * sigma * sigma;

    vec4  sample_tex = texCoord.xyxy;
    float dist       = 0;
    float dr         = dtc.x + dtc.y;
    vec2  sum2       = vec2(pixelDepth, 0);
    vec2  wsum2      = vec2(1, 0);

    vec2 sample_depth;
    vec2 w2;
    for(int x = 1; x <= filterSize_pixel; ++x){
        sample_tex += dtc;
        dist       += dr;

        sample_depth.x = texture(depthTexture, sample_tex.xy).r;
        sample_depth.y = texture(depthTexture, sample_tex.zw).r;
        w2             = vec2(compute_weight1D(dist, two_sigma2));
        // w2             = vec2(compute_weight1D(x, two_sigma2));
        // w2             = vec2(1);

        sum2  += sample_depth * w2;
        wsum2 += w2;
    }

    vec2 filterVal = vec2(sum2.x, wsum2.x) + vec2(sum2.y, wsum2.y);
    smoothDepth = filterVal.x / filterVal.y;
}

