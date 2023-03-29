#shader vertex
#version 330 core

layout(location = 0) in vec4 a_Position;
out vec4 vertexColor;

uniform float level_offset;

void main(){
    gl_Position = a_Position;
    gl_Position.x = gl_Position.x + level_offset;
    gl_Position.y = -gl_Position.y;
    vertexColor = a_Position;
};

#shader fragment
#version 330 core

out vec4 a_Color;

in vec4 vertexColor;

void main(){
    a_Color = vertexColor;
};
