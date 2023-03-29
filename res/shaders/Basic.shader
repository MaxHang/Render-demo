#shader vertex
#version 330 core

layout(location = 0) in vec4 a_Position;
layout(location = 1) in vec4 a_Color;
out vec4 vertexColor;

void main(){
    gl_Position = a_Position;
    vertexColor = a_Color;
};

#shader fragment
#version 330 core

out vec4 FragColor;

in vec4 vertexColor;

void main(){
    FragColor = vertexColor;
};
