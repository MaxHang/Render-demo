#shader vertex
#version 330 core

layout(location = 0) in vec4 a_Position;
out vec4 vertexColor;

void main(){
    gl_Position = a_Position;
    vertexColor = vec4(0.5, 0.0, 0.0, 1.0);
};

#shader fragment
#version 330 core

layout(location = 0) out vec4 a_Color;

in vec4 vertexColor;

void main(){
    a_Color = vertexColor;
};
