# version 130

in vec2 position;

out vec2 fragPos;

void main() {
  gl_Position = vec4(position*vec2(1.0, 1.0), 0.0, 1.0);
  fragPos = position;
}
