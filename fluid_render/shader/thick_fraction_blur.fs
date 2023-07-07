#version 330 core

uniform sampler2D thickTexture;
uniform sampler2D fluidFracTexture;
uniform int       filterSize;
uniform int       screenWeight;
uniform int       screenHeight;

uniform int filterDirection;

in  vec2  texCoord;
layout (location = 0) out float outThick;
layout (location = 1) out vec2  outFrac;


//-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
float compute_weight1D(float r, float two_sigma2)
{
    return exp(-r * r / two_sigma2);
}

//-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
void main()
{
    vec2  blurRadius = vec2(1.0 / screenWeight, 1.0 / screenHeight);
    float sigma      = float(filterSize) / 3.0;
    float two_sigma2 = 2.0 * sigma * sigma;

    vec4  dtc = (filterDirection == 0) ? vec4(blurRadius.x, 0, -blurRadius.x, 0) : vec4(0, blurRadius.y, 0, -blurRadius.y);
    float dr  = dtc.x + dtc.y;
    float r   = 0;

    float pixelThcik = texture(thickTexture, texCoord).r;
    vec2  pixelFrac  = texture(fluidFracTexture, texCoord).rg;
    vec4  f_tex      = texCoord.xyxy;
    vec2  sampleFrac1;
    vec2  sampleFrac2;
    vec2  frac1_sum2 = vec2(pixelFrac.r, 0);
    vec2  frac2_sum2 = vec2(pixelFrac.g, 0);
    vec2  sampleThick;
    vec2  thick_sum2 = vec2(pixelThcik, 0);
    vec2  w2;
    vec2  wsum2      = vec2(1, 0);


    for(int x = 1; x <= filterSize; ++x) {
        f_tex += dtc;
        r     += dr;
        sampleFrac1.x = texture(fluidFracTexture, f_tex.xy).r;
        sampleFrac1.y = texture(fluidFracTexture, f_tex.zw).r;
        sampleFrac2.x = texture(fluidFracTexture, f_tex.xy).g;
        sampleFrac2.y = texture(fluidFracTexture, f_tex.zw).g;
        sampleThick.x = texture(thickTexture, f_tex.xy).r;
        sampleThick.y = texture(thickTexture, f_tex.zw).r;
        
        // w2          = vec2(1);
        w2          = vec2(compute_weight1D(r, two_sigma2));
        frac1_sum2 += sampleFrac1 * w2;
        frac2_sum2 += sampleFrac2 * w2;
        thick_sum2 += sampleThick * w2;
        wsum2      += w2;
    }
    vec2 filterFrac1 = vec2(frac1_sum2.x, wsum2.x) + vec2(frac1_sum2.y, wsum2.y);
    vec2 filterFrac2 = vec2(frac2_sum2.x, wsum2.x) + vec2(frac2_sum2.y, wsum2.y);
    outFrac          = vec2(filterFrac1.x / filterFrac1.y, filterFrac2.x / filterFrac2.y);
    vec2 filterThcik = vec2(thick_sum2.x, wsum2.x) + vec2(thick_sum2.y, wsum2.y);
    outThick         = filterThcik.x / filterThcik.y;
}