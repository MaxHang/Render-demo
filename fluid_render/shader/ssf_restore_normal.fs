# version 330 core

in vec2 texCoord;

uniform float near;
uniform float far;
uniform int screenWidth;
uniform int screenHeight;
uniform mat4 inProjection;
uniform sampler2D depthTexture;

out vec3 normal;

vec3 uvToEye(vec2 texCoord, float depth){
    // back to ndc
    vec2 pos   = texCoord * 2.0 - 1.0;
    // viewSpaceZ to ndcZ
    float ndcZ = ((far + near) / (far - near) * depth + 2.0 * far * near / (far - near)) / depth;

    vec4 ndcPos  = vec4(pos.x, pos.y, ndcZ, 1.0);
    vec4 viewPos = inProjection * ndcPos;
    return viewPos.xyz / viewPos.w;
}

void setfragDepth(float viewZ){
	float ndcZ  = ((far + near) / (far - near) * viewZ + 2.0 * far * near / (far - near)) / viewZ;
	gl_FragDepth = 0.5 * (gl_DepthRange.diff * ndcZ + gl_DepthRange.far + gl_DepthRange.near);	
	// gl_FragDepth = 0.99;
}
void main(){
    float depth   = texture(depthTexture, texCoord).r;
	setfragDepth(depth);
	if(depth < -far) {
        normal = vec3(0, 1, 0);
        return;
    }
    vec2 depthTexelSize = 1.0 / textureSize(depthTexture, 0);
	// calculate eye space position.
	vec3 eyeSpacePos = uvToEye(texCoord, depth);
	// finite difference.
	vec3 ddxLeft   = eyeSpacePos - uvToEye(texCoord - vec2(depthTexelSize.x,0.0f),
					texture(depthTexture, texCoord - vec2(depthTexelSize.x,0.0f)).r);
	vec3 ddxRight  = uvToEye(texCoord + vec2(depthTexelSize.x,0.0f),
					texture(depthTexture, texCoord + vec2(depthTexelSize.x,0.0f)).r) - eyeSpacePos;
	vec3 ddyTop    = uvToEye(texCoord + vec2(0.0f,depthTexelSize.y),
					texture(depthTexture, texCoord + vec2(0.0f,depthTexelSize.y)).r) - eyeSpacePos;
	vec3 ddyBottom = eyeSpacePos - uvToEye(texCoord - vec2(0.0f,depthTexelSize.y),
					texture(depthTexture, texCoord - vec2(0.0f,depthTexelSize.y)).r);
	// vec3 dx = ddxRight;
	// vec3 dy = ddyTop;
	vec3 dx = ddxLeft;
	vec3 dy = ddyBottom;
	if(abs(ddxRight.z) < abs(ddxLeft.z))
		dx = ddxRight;
	if(abs(ddyTop.z) < abs(ddyBottom.z))
		dy = ddyTop;
	normal = normalize(cross(dx, dy));
}

// void main(){

// }

// void main(){
//     // read viewSpace depth from texture
//     float depth = texture(depthTexture, texCoord).r;
//     if (-depth > far){
//         normal = vec3(0.0, 1.0, 0.0);
//         return;
//     }
    
//     // calculate viewSpace position from depth
//     vec3 viewSpacePos = uvToEye(texCoord, depth);

//     // calculate differences
//     float pixelWidth  = 1.0 / float(screenWidth);
//     float pixelHeight = 1.0 / float(screenHeight);

//     vec2 texCoordXL = vec2(texCoord.x - pixelWidth, texCoord.y);
//     vec2 texCoordXR = vec2(texCoord.x + pixelWidth, texCoord.y);
//     vec2 texCoordYB = vec2(texCoord.x, texCoord.y - pixelHeight);
//     vec2 texCoordYT = vec2(texCoord.x, texCoord.y + pixelHeight);

//     float depthXL = texture(depthTexture, texCoordXL).r;
//     float depthXR = texture(depthTexture, texCoordXR).r;
//     float depthYB = texture(depthTexture, texCoordYB).r;
//     float depthYT = texture(depthTexture, texCoordYT).r;

//     vec3 dxL = viewSpacePos - uvToEye(texCoordXL, depthXL);
//     vec3 dxR = uvToEye(texCoordXR, depthXR) - viewSpacePos;
//     vec3 dyB = viewSpacePos - uvToEye(texCoordYB, depthYB);
//     vec3 dyT = uvToEye(texCoordYT, depthYT) - viewSpacePos;

//     vec3 dx = dxL;
//     if (abs(dxR.z) < abs(dx.z)){
//         dx = dxR;
//     }

//     vec3 dy = dyB;
//     if (abs(dyT.z) < abs(dy.z)){
//         dy = dyT;
//     }

//     vec3 N = cross(dx, dy);
//     // if(isnan(N.x) || isnan(N.y) || isnan(N.y) ||
//     //    isinf(N.x) || isinf(N.y) || isinf(N.z)) {
//     //     N = vec3(0.0, 0.0, 1.0);
//     // }
//     normal = normalize(N);
// }