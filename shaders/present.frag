# version 130

in vec2 fragPos;

uniform sampler2D image;

out vec4 Color;

void main() {
  Color = texture2D(image, fragPos);
}
