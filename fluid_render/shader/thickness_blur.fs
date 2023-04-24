#version 330 core

// 厚度纹理使用高斯模糊

uniform float     filterSize;
uniform vec2      blur_dir;
uniform sampler2D thickTexture;

in vec2   texCoord;
out float outThickness;

//-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
void main()
{
    vec2 tex_offset = 1.0 / textureSize(thickTexture, 0);
    vec2 blur_dir_offset = blur_dir * tex_offset;
    float sum        = 0;
    float wsum       = 0;
    float sigma      = float(filterSize) / 3.0;
    float two_sigma2 = 2.0 * sigma * sigma;

    for(float x = -filterSize; x <= filterSize; x += 1.0) {
        vec2  samplep         = x * blur_dir_offset + texCoord;
        float sampleThickness = texture2D(thickTexture, samplep).r;
        float r               = length(x);
        // float w               = exp(-r * r / two_sigma2);
        float w               = 1;
        
        sum  += sampleThickness * w;
        wsum += w;
    }

    outThickness = sum / wsum;
}