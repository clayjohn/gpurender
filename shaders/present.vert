# version 130

in vec2 position;

out vec2 fragPos;

void main() {
  gl_position = vec4(position, 0.0, 1.0);
  fragPos = position;
}