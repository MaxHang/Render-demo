#version 330 core

// 双边分离过滤 https://en.wikipedia.org/wiki/Bilateral_filter
// spatial(domain) 空间: 即坐标差异 高斯函数的sigma
// range   范围: 像素值(这里是深度)差异 高斯函数的sigma
// 一次选择水平或者竖直方向进行过滤

// in vec2 texCoord;

// uniform int filterSize;
// uniform float sigma_d;
// uniform float sigma_r;
// uniform vec2  blur_dir;
// uniform sampler2D depthTexture;

// out float smoothDepth;
in vec2 texCoord;

uniform int MaxFilterSize;
uniform int filterSize;
uniform float zoom;
uniform float screenHeight;
uniform float particleRadius;
uniform vec2  blur_dir;
uniform sampler2D depthTexture;

out float smoothDepth;


const float thresholdRatio = 10.0;
float compute_weight2D(vec2 r, float two_sigma2)
{
    return exp(-dot(r, r) / two_sigma2);
}

float compute_weight1D(float r, float two_sigma2)
{
    return exp(-r * r / two_sigma2);
}

// void main(){
//     // gets size of single texel.
//     vec2 tex_offset = 1.0 / textureSize(depthTexture, 0);
//     vec2 blur_dir_offset = blur_dir * tex_offset;

//     float pixelDepth = texture(depthTexture, texCoord).r;
//     float ratio      = screenHeight / (2.0 * tan(zoom / 2.0));
//     float K          = filterSize * ratio * particleRadius * 0.1;
//     int   pixelFilterSize = min(MaxFilterSize, int(ceil(K / pixelDepth)));
//     float sigma_d = pixelFilterSize / 3.0f;
//     float two_sigma_d2 = 2.0f * sigma_d * sigma_d;

//     float threshold        = particleRadius * thresholdRatio;
//     float sigma_depth      = threshold / 3.0f;
//     float two_sigma_depth2 = 2.0f * sigma_depth * sigma_depth;

//     // 同时对左右边进行取样, xy对右边取样, zw对左边取样, 权重同理
//     vec4  sample_tex = texCoord.xyxy;
//     float dist       = 0;
//     vec2  sum2       = vec2(pixelDepth, 0);
//     vec2  wsum2      = vec2(1, 0);

//     vec2 sample_depth;
//     vec2 w2_dist;
//     vec2 w2_depth;
//     vec2 depthDiff;
//     for(int x = 1; x <= pixelFilterSize; ++x){
//         sample_tex.xy += blur_dir_offset;
//         sample_tex.zw -= blur_dir_offset;
//         dist           = x;

//         sample_depth.x = texture(depthTexture, sample_tex.xy).r;
//         sample_depth.y = texture(depthTexture, sample_tex.zw).r;
//         depthDiff      = sample_depth - vec2(pixelDepth);

//         // w2_dist = vec2(compute_weight1D(dist, two_sigma_d2));
//         w2_dist = vec2(1);
//         w2_depth.x = compute_weight1D(depthDiff.x, two_sigma_depth2);
//         w2_depth.y = compute_weight1D(depthDiff.y, two_sigma_depth2);

//         sum2  += sample_depth * w2_dist * w2_depth;
//         wsum2 += w2_dist * w2_depth;
//     }
    
//     vec2 filterVal = vec2(sum2.x, wsum2.x) + vec2(sum2.y, wsum2.y);
//     smoothDepth = filterVal.x / filterVal.y;
// }

void main(){
    vec2 blurRadius = 1.0 / textureSize(depthTexture, 0);
    float pixelDepth = texture(depthTexture, texCoord).r;

    float ratio      = screenHeight / 2.0 / tan(zoom / 2.0);
    float K          = -filterSize * ratio * particleRadius * 0.03;
    int   filterSize_pixel = min(MaxFilterSize, int(ceil(K / pixelDepth)));
    float sigma      = filterSize_pixel / 3.0f;
    float two_sigma2 = 2.0f * sigma * sigma;

    float threshold       = particleRadius * thresholdRatio;
    float sigmaDepth      = threshold / 3.0f;
    float two_sigmaDepth2 = 2.0f * sigmaDepth * sigmaDepth;

    vec4 f_tex = texCoord.xyxy;
    vec2 r     = vec2(0, 0);
    vec4 sum4  = vec4(pixelDepth, 0, 0, 0);
    vec4 wsum4 = vec4(1, 0, 0, 0);
    vec4 sampleDepth;
    vec4 w4_r;
    vec4 w4_depth;
    vec4 rDepth;
    for(int x = 1; x <= filterSize_pixel; ++x) {
        r.x     += blurRadius.x;
        f_tex.x += blurRadius.x;
        f_tex.z -= blurRadius.x;
        vec4 f_tex1 = f_tex.xyxy;
        vec4 f_tex2 = f_tex.zwzw;

        for(int y = 1; y <= filterSize_pixel; ++y) {
            r.y += blurRadius.y;

            f_tex1.y += blurRadius.y;
            f_tex1.w -= blurRadius.y;
            f_tex2.y += blurRadius.y;
            f_tex2.w -= blurRadius.y;

            sampleDepth.x = texture(depthTexture, f_tex1.xy).r;
            sampleDepth.y = texture(depthTexture, f_tex1.zw).r;
            sampleDepth.z = texture(depthTexture, f_tex2.xy).r;
            sampleDepth.w = texture(depthTexture, f_tex2.zw).r;

            rDepth     = sampleDepth - vec4(pixelDepth);
            // w4_r       = vec4(compute_weight2D(blurRadius * r, two_sigma2));
            w4_r       = vec4(1);
            // w4_r       = vec4(compute_weight2D(blurRadius, two_sigma2));
            // w4_r       = vec4(compute_weight2D(r, two_sigma2));
            // w4_r       = vec4(compute_weight2D(vec2(x, y), two_sigma2));
            w4_depth.x = compute_weight1D(rDepth.x, two_sigmaDepth2);
            w4_depth.y = compute_weight1D(rDepth.y, two_sigmaDepth2);
            w4_depth.z = compute_weight1D(rDepth.z, two_sigmaDepth2);
            w4_depth.w = compute_weight1D(rDepth.w, two_sigmaDepth2);

            sum4  += sampleDepth * w4_r * w4_depth;
            wsum4 += w4_r * w4_depth;
            // sum4  += sampleDepth * w4_depth;
            // wsum4 += w4_depth;
        }
    }

    vec2 filterVal;
    filterVal.x = dot(sum4, vec4(1, 1, 1, 1));
    filterVal.y = dot(wsum4, vec4(1, 1, 1, 1));

	smoothDepth = filterVal.x / filterVal.y;
}

// void main(){
// 	// gets size of single texel.
//     vec2 tex_offset = 1.0 / textureSize(depthTexture, 0);
//     vec2 blur_dir_offset = blur_dir * tex_offset;

//     float two_sigma_d2 = 2 * sigma_d * sigma_d;
//     float two_sigma_r2 = 2 * sigma_r * sigma_r;
    
// 	float sum = 0.0f;
// 	float wsum = 0.0f;
// 	float value = texture(depthTexture, texCoord).r;

//     for(float x = -filterSize;x <= filterSize;x += 1.0f)
//     {
//         float sample = texture(depthTexture, texCoord + x * blur_dir_offset).r;
        
//         // spatial domain.
//         float dist = length(x);
//         // float w = compute_weight1D(dist, two_sigma_d2);
//         float w = 1.0;
//         // range domain.
//         float pixelValueDiff = sample - value;
//         float g = compute_weight1D(pixelValueDiff, two_sigma_r2);
        
//         sum += sample * w * g;
//         wsum += w * g;
//     }

// 	if(wsum >= 0.0f)
// 		sum /= wsum;

// 	smoothDepth = sum;
// }