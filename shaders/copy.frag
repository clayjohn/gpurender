# version 130

in vec2 fragPos;

uniform sampler2D scene;

out vec4 Color;

void main() {
  Color = texture2D(scene, fragPos);
}
