#shader vertex
#version 330 core

layout(location = 0) in vec4 a_Position;

void main(){
    gl_Position = a_Position;
};

#shader fragment
#version 330 core

out vec4 a_Color;

uniform vec4 u_Color;

void main(){
    a_Color = u_Color;
};
