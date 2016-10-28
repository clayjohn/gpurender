#version 330
precision highp float;

in vec2 fragPos;

//uniform sampler2D scene;
uniform samplerBuffer buff;
uniform float passes;
out vec4 Color;

void main() {
  //vec4 col = texture2D(scene, fragPos*0.5+0.5);
  vec4 col = vec4(0.0, 0.0, 0.0, 1.0);
  col /= passes;
  col.rgb = pow(col.rgb, vec3(1.0/2.2));
  col.r = texelFetch(buff, 0).x;
  col.a = 1.0;
  Color = col;
}
