#version 330 core

#define FIX_OTHER_WEIGHT
#define RANGE_EXTENSION

#define PI_OVER_8 0.392699082f

uniform sampler2D depthTexture;
uniform float     particleRadius;
uniform float     zoom;
uniform float     near;
uniform float     far;
uniform int       filterSize;
uniform int       MaxFilterSize;
uniform int       screenWeight;
uniform int       screenHeight;

// doFilter1D = 1, 0, and -1 (-1 mean filter2D with fixed radius)
uniform int doFilter1D;
uniform int filterDirection;

in  vec2  texCoord;
out float outDepth;

//-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
const int   fixedFilterRadius = 4;
const float thresholdRatio    = 10.5;
const float clampRatio        = 1;
// const float clampRatio        = 0.7;

//-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
float compute_weight1D(float r, float two_sigma2)
{
    return exp(-r * r / two_sigma2);
}

float compute_weight2D(vec2 r, float two_sigma2)
{
    return exp(-dot(r, r) / two_sigma2);
}

//-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
void ModifiedGaussianFilter1D(inout float sampleDepth, inout float weight, inout float weight_other, inout float upper, inout float lower, float lower_clamp, float threshold)
{
    if(sampleDepth > upper) {
        weight = 0;
#ifdef FIX_OTHER_WEIGHT
        weight_other = 0;
#endif
    } else {
        if(sampleDepth < lower) {
            sampleDepth = lower_clamp;
        }
#ifdef RANGE_EXTENSION
        else {
            upper = max(upper, sampleDepth + threshold);
            lower = min(lower, sampleDepth - threshold);
        }
#endif
    }
}

void ModifiedGaussianFilter2D(inout float sampleDepth, inout float weight, inout float weight_other, inout float upper, inout float lower, float lower_clamp, float threshold)
{
    if(sampleDepth > upper) {
        weight = 0;
#ifdef FIX_OTHER_WEIGHT
        weight_other = 0;
#endif
    } else {
        if(sampleDepth < lower) {
            sampleDepth = lower_clamp;
        }
#ifdef RANGE_EXTENSION
        else {
            upper = max(upper, sampleDepth + threshold);
            lower = min(lower, sampleDepth - threshold);
        }
#endif
    }
}

//-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
float filter1D(float pixelDepth)
{
    if(filterSize == 0) {
        return pixelDepth;
    }

    // 纹素的大小
    vec2  blurRadius = vec2(1.0 / screenWeight, 1.0 / screenHeight);
    float threshold  = particleRadius * thresholdRatio;
    float ratio      = screenHeight / 2.0 / tan(zoom / 2.0);
    // float K          = -filterSize * ratio * 0.001f;
    float K          = -filterSize * ratio * particleRadius * 0.1f;
    int   pixelFilterSize = min(MaxFilterSize, int(ceil(K / pixelDepth)));

    // 钳位函数, 上边界与下边界 以及 小于下边界时深度修正值lower_clamp
    float upper       = pixelDepth + threshold;
    float lower       = pixelDepth - threshold;
    float lower_clamp = pixelDepth - particleRadius * clampRatio;

    float sigma      = pixelFilterSize / 3.0f;
    float two_sigma2 = 2.0f * sigma * sigma;

    vec2 sum2  = vec2(pixelDepth, 0);
    vec2 wsum2 = vec2(1, 0);
    // 过滤方向, x 或者 y 方向, 同时对一个方向的正负进行采样 xy 为+x, zw为 -x
    vec4 dtc   = (filterDirection == 0) ? vec4(blurRadius.x, 0, -blurRadius.x, 0) : vec4(0, blurRadius.y, 0, -blurRadius.y);

    // 要采样的纹理坐标, 同时对 x 与 -x 采样
    vec4  f_tex = texCoord.xyxy;
    // 采样坐标 与 当前过滤坐标的欧式距离
    float r     = 0;
    // 相邻纹素坐标的欧式距离
    float dr    = dtc.x + dtc.y;

    float upper1 = upper;
    float upper2 = upper;
    float lower1 = lower;
    float lower2 = lower;

    // x 与 -x 过滤像素的深度值
    vec2  sampleDepth;
    vec2  w2;

    for(int x = 1; x <= pixelFilterSize; ++x) {
        f_tex += dtc;
        r     += dr;

        sampleDepth.x = texture(depthTexture, f_tex.xy).r;
        sampleDepth.y = texture(depthTexture, f_tex.zw).r;

        // 对于正负方向来说, 其是关于过滤元素对称的, 故其权重是一样的
        w2 = vec2(compute_weight1D(x, two_sigma2));
        // w2 = vec2(compute_weight1D(r, two_sigma2));
        // 修正高斯权重
        ModifiedGaussianFilter1D(sampleDepth.x, w2.x, w2.y, upper1, lower1, lower_clamp, threshold);
        ModifiedGaussianFilter1D(sampleDepth.y, w2.y, w2.x, upper2, lower2, lower_clamp, threshold);

        sum2  += sampleDepth * w2;
        wsum2 += w2;
    }

    vec2 filterVal = vec2(sum2.x, wsum2.x) + vec2(sum2.y, wsum2.y);
    return filterVal.x / filterVal.y;
}

float filter2D(float pixelDepth)
{
    if(filterSize == 0) {
        return pixelDepth;
    }

    vec2  blurRadius = vec2(1.0 / screenWeight, 1.0 / screenHeight);
    float threshold  = particleRadius * thresholdRatio;
    float ratio      = screenHeight / 2.0 / tan(zoom / 2.0);
    // float K          = -filterSize * ratio * 0.001f;
    float K          = -filterSize * ratio * particleRadius * 0.1f;
    int   pixelFilterSize = (doFilter1D < 0) ? fixedFilterRadius : min(MaxFilterSize, int(ceil(K / pixelDepth)));

    float upper       = pixelDepth + threshold;
    float lower       = pixelDepth - threshold;
    float lower_clamp = pixelDepth - particleRadius * clampRatio;

    float sigma      = pixelFilterSize / 3.0f;
    float two_sigma2 = 2.0f * sigma * sigma;

    vec4 f_tex = texCoord.xyxy;

    vec2 r     = vec2(0, 0);
    vec4 sum4  = vec4(pixelDepth, 0, 0, 0);
    vec4 wsum4 = vec4(1, 0, 0, 0);
    vec4 sampleDepth;
    vec4 w4;

    for(int x = 1; x <= pixelFilterSize; ++x) {
        r.x     += blurRadius.x;
        f_tex.x += blurRadius.x;
        f_tex.z -= blurRadius.x;
        vec4 f_tex1 = f_tex.xyxy;
        vec4 f_tex2 = f_tex.zwzw;

        for(int y = 1; y <= pixelFilterSize; ++y) {
            f_tex1.y += blurRadius.y;
            f_tex1.w -= blurRadius.y;
            f_tex2.y += blurRadius.y;
            f_tex2.w -= blurRadius.y;

            sampleDepth.x = texture(depthTexture, f_tex1.xy).r;
            sampleDepth.y = texture(depthTexture, f_tex1.zw).r;
            sampleDepth.z = texture(depthTexture, f_tex2.xy).r;
            sampleDepth.w = texture(depthTexture, f_tex2.zw).r;

            r.y += blurRadius.y;
            w4   = vec4(compute_weight2D(vec2(x, y), two_sigma2));
            // w4   = vec4(compute_weight2D(r, two_sigma2));
            // w4   = vec4(compute_weight2D(blurRadius * r, two_sigma2));

            ModifiedGaussianFilter2D(sampleDepth.x, w4.x, w4.w, upper, lower, lower_clamp, threshold);
            ModifiedGaussianFilter2D(sampleDepth.y, w4.y, w4.z, upper, lower, lower_clamp, threshold);
            ModifiedGaussianFilter2D(sampleDepth.z, w4.z, w4.y, upper, lower, lower_clamp, threshold);
            ModifiedGaussianFilter2D(sampleDepth.w, w4.w, w4.x, upper, lower, lower_clamp, threshold);

            sum4  += sampleDepth * w4;
            wsum4 += w4;
        }
    }

    vec2 filterVal;
    filterVal.x = dot(sum4, vec4(1, 1, 1, 1));
    filterVal.y = dot(wsum4, vec4(1, 1, 1, 1));
    return filterVal.x / filterVal.y;
}

//-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
void main()
{
    float pixelDepth = texture(depthTexture, texCoord).r;

    if(pixelDepth > near || pixelDepth < -far) {
        outDepth = pixelDepth;
    } else {
        outDepth = (doFilter1D == 1) ? filter1D(pixelDepth) : filter2D(pixelDepth);
    }
}
