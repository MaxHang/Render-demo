#shader vertex
#version 330 core
layout (location = 0) in vec3 aPos;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec4 aColor;

void main()
{
	gl_Position = projection * view * model * vec4(aPos, 1.0f);
	aColor = vec4(clamp(aPos, 0.0, 1.0), 1.0);
}


#shader fragment
#version 330 core
in vec4 aColor;

out vec4 FragColor;

void main()
{
	// linearly interpolate between both textures (80% container, 20% awesomeface)
	FragColor = aColor;
}
