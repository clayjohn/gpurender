#version 130
precision highp float;

in vec2 fragPos;

uniform sampler2D scene;
uniform float passes;
out vec4 Color;

void main() {
  vec4 col = texture2D(scene, fragPos*0.5+0.5);
  col /= passes;
  col.rgb = pow(col.rgb, vec3(1.0/2.2));
  col.a = 1.0;
  Color = col;
}
