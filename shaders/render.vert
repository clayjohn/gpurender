# version 130

in vec2 position;
in vec4 color;

out vec2 fragPos;
out vec4 fragColor;

void main() {
  gl_Position = vec4(position, 0.0, 1.0);
  fragPos = position;
  fragColor = color;
}
