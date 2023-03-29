#shader vertex
#version 330 core

layout(location = 0) in vec4 a_Position;

void main(){
    gl_Position = a_Position;
};

#shader fragment
#version 330 core

layout(location = 0) out vec4 a_Color;

void main(){
    a_Color = vec4(1.0, 1.0, 0.0, 1.0);
};
