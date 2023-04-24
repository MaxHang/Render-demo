#version 330 core

in vec2 texCoord;

uniform sampler2D depthTexture;
uniform float filterSize;

// 双边过滤 https://en.wikipedia.org/wiki/Bilateral_filter
// spatial(domain) 空间: 即坐标差异 高斯函数的sigma
uniform float two_sigma_d2;
// range   范围: 像素值(这里是深度)差异 高斯函数的sigma
uniform float two_sigma_r2;

out float smoothDepth;

float compute_weight(float r, float two_sigma2){
	return exp(-r * r / two_sigma2);
}

void main(){
	// gets size of single texel.
    vec2 tex_offset = 1.0 / textureSize(depthTexture, 0);
    
	float sum = 0.0f;
	float wsum = 0.0f;
	float value = texture(depthTexture, texCoord).r;

	for(float y = -filterSize;y <= filterSize;y += 1.0f)
	{
		for(float x = -filterSize;x <= filterSize;x += 1.0f)
		{
			float sample = texture(depthTexture, texCoord + vec2(x, y) * tex_offset).r;
			
			// spatial domain.
			float dist = length(vec2(x, y));
			// float w = compute_weight(dist, two_sigma_d2);
			float w = 1.0;

			// range domain.
			float pixelValueDiff = sample - value;
			float g = compute_weight(pixelValueDiff, two_sigma_r2);
			
			sum += sample * w * g;
			wsum += w * g;
		}
	}

	if(wsum >= 0.0f)
		sum /= wsum;

	smoothDepth = sum;
}