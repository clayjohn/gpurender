# version 130
precision highp float;
in vec2 fragPos;
in vec4 fragColor;

uniform sampler2D lastFrame;
uniform vec2 resolution;
uniform float time;

out vec4 Color;

const int SPHERE = 1;
const int CUBE = 2;
const int PLANE = 3;
const int TRIANGLE = 4;

const int DIFFUSE = 1;
const int METAL = 2;
const int DIALECTRIC = 3;

struct Ray {
  vec3 pos;
  vec3 dir;
};

struct Material {
  vec3 albedo;
  vec3 specular;
  vec3 emission;
  float fuzz;
  int type;
};

struct Hit_record {
  float t;
  vec3 p;
  vec3 normal;
  Material material;
};

struct Hitable {
  vec3 pos;
  float size;
  vec3 dir;
  int type;
};

struct Camera {
  vec3 origin;
  vec3 corner;
  vec3 height;
  vec3 width;
  vec3 w;
  vec3 u;
  vec3 v;
  float lens_radius;
};

uniform int NUM_OBJECTS;
#define MAX_OBJECTS 256
uniform Hitable hitables[MAX_OBJECTS];
uniform Material materials[MAX_OBJECTS];
uniform Camera camera;

vec3 hash33(vec3 x) {
  vec3 p = x+vec3(fract(time)*46.732189);
  p = fract(p*vec3(441.897, 443.423, 437.195));
  p += dot(p, p.yzx+19.19+fract(time)*57.67);
  return vec3(-1.0)+(2.0*fract(vec3((p.x+p.y)*p.z, (p.x+p.z)*p.y, (p.z+p.y)*p.x)));
}

vec2 hash32(vec3 x) {
  vec3 p = x+vec3(fract(time)*46.732189);
  p = fract(p*vec3(441.897, 443.423, 437.195));
  p += dot(p, p.yzx+19.19+fract(time)*57.67);
  return vec2(-1.0)+2.0*fract(vec2((p.x+p.y)*p.z, (p.x+p.z)*p.y));
}

float hash31(vec3 x) {
  vec3 p = x+vec3(fract(time)*46.732189);
  p = fract(p*vec3(441.897, 443.423, 437.195));
  p += dot(p, p.yzx+19.19+fract(time)*57.67);
  return -1.0+(2.0*fract((p.x+p.y)*p.z));
}

bool hit_sphere(Hitable s, Ray ray, float t_min, float t_max, inout Hit_record rec) {
  vec3 oc = ray.pos - s.pos;
  float a = dot(ray.dir, ray.dir);
  float b = dot(oc, ray.dir);
  float c = dot(oc, oc) - (s.size*s.size);
  float discriminant = b*b - a*c;
  if (discriminant > 0.0) {
    float temp = (-b - sqrt(discriminant))/ a;
    if ((temp>t_min) && (temp<t_max)) {
      rec.t = temp;
      rec.p = ray.pos+ray.dir*temp;
      rec.normal = (rec.p-s.pos)/s.size;
      return true;
    }
    temp = (-b + sqrt(discriminant))/ a;
    if ((temp>t_min) && (temp<t_max)) {
      rec.t = temp;
      rec.p = ray.pos+ray.dir*temp;
      rec.normal = (rec.p-s.pos)/s.size;
      return true;
    }
  }
  return false;
}

float schlick(float cosine, float ref_idx) {
    float r0 = (1.0-ref_idx) / (1.0+ref_idx);
    r0 = r0*r0;
    return r0 + (1.0-r0)*pow((1.0 - cosine),5.0);
}

bool refracter(vec3 v, vec3 n, float ni_over_nt, inout vec3 refracted) {
    vec3 uv = normalize(v);
    float dt = dot(uv, n);
    float discriminant = 1.0 - ni_over_nt*ni_over_nt*(1-dt*dt);
    if (discriminant > 0.0) {
        refracted = ni_over_nt*(uv - n*dt) - n*sqrt(discriminant);
        return true;
    }
    else {
        return false;
    }
}

bool scatter(Ray r, Hit_record rec, inout vec3 attenuation, inout Ray scattered){
  if (rec.material.type == DIFFUSE) {
    vec3 target = rec.p+rec.normal+hash33(rec.p);
    scattered = Ray(rec.p, target-rec.p);
    attenuation = rec.material.albedo;
    return true;
  }
  else if (rec.material.type == METAL) {
    vec3 reflected = reflect(normalize(r.dir), rec.normal);
    scattered = Ray(rec.p, reflected +rec.material.fuzz*hash33(rec.p));
    attenuation = rec.material.albedo;
    return (dot(scattered.dir, rec.normal) > 0.0);
  }
  else if (rec.material.type == DIALECTRIC) {
    vec3 outward_normal;
    vec3 reflected = reflect(r.dir, rec.normal);
    float ni_over_nt;
    attenuation = vec3(1.0);
    float reflect_prob;
    
    float cosine;
    if (dot(r.dir, rec.normal) > 0.0) {
      outward_normal = -rec.normal;
      ni_over_nt = rec.material.fuzz;
      //cosine = rec.material.fuzz*dot(r.dir, rec.normal)/length(r.dir);
      cosine = dot(r.dir, rec.normal) / length(r.dir); 
      cosine = sqrt(1.0 - rec.material.fuzz*rec.material.fuzz*(1.0-cosine*cosine));
            
    } else {
      outward_normal = rec.normal;
      ni_over_nt = 1.0 / rec.material.fuzz;
      cosine = -dot(r.dir, rec.normal)/length(r.dir);
    }
    vec3 refracted;
    if (refracter(r.dir, outward_normal, ni_over_nt, refracted)) {
      reflect_prob = schlick(cosine, rec.material.fuzz);
      //scattered = Ray(rec.p, refracted);
    } else {
      reflect_prob = 1.0;
    }
    if (hash31(rec.p)<reflect_prob) {
      scattered = Ray(rec.p, reflected);
    } else {
      scattered = Ray(rec.p, refracted);
    } 
    return true;
  }
}

bool hit_world(Ray ray, float t_min, float t_max, inout Hit_record rec) {
  Hit_record temp_rec;
  bool hit_anything = false;
  float closest_so_far = t_max;

  for (int i = 0;i<MAX_OBJECTS;i++) {
    if (i < NUM_OBJECTS){

      if (hitables[i].type == SPHERE) {
        if (hit_sphere(hitables[i], ray, t_min, closest_so_far, temp_rec)) {
          closest_so_far = temp_rec.t;
          rec = temp_rec;
          rec.material = materials[i];
          hit_anything = true;
        }
      }

      else if (hitables[i].type == CUBE) {
        float x = 0.0;
      }

    }
  }

   return hit_anything;
}

bool color(inout Ray r, inout vec3 col, inout Hit_record rec) {
  

  if (hit_world(r, 0.001, 1000.0, rec)) {
    Ray scattered;
    vec3 attenuation;
    if (scatter(r, rec, attenuation, scattered)) {
      r = scattered;
      col *= attenuation;
      return true;
    } else {
      col *= 0.0;
    }
  } else {
    vec3 unit_direction = normalize(r.dir);
    float t = 0.5*(unit_direction.y+1.0);
    col *= mix(vec3(1.0), vec3(0.5, 0.7, 1.0), t);
    return false;
  }
}

vec2 antia(vec2 x, float t) {
  vec3 p = vec3(x, t);
  p = fract(p*vec3(441.897, 443.423, 437.195));
  p += dot(p, p.yzx+19.19);
  return fract(vec2((p.x+p.y)*p.z, (p.x+p.z)*p.y));
}

Ray get_ray(vec2 uv) {
  vec2 rd = camera.lens_radius * hash32(vec3(uv, 1.0/time));
  vec3 offset = camera.u*rd.x + camera.v*rd.y;
  return Ray(camera.origin + offset, camera.corner + uv.x * camera.width + uv.y*camera.height - camera.origin - offset);
}

vec3 cast_ray() {
  vec2 uv = (gl_FragCoord.xy)+antia(gl_FragCoord.xy, time);
  uv /= resolution;
  //uv = 2.0*uv - 1.0;
  //uv.x *= resolution.x/resolution.y;
  //vec3 direction = vec3(uv, -1.0);
  //vec3 origin = vec3(0.0);
  Ray ray = get_ray(uv);//Ray(origin, normalize(direction));
  bool intersect = true;
  vec3 col = vec3(1.0);
  int count = 0;
  Hit_record rec;
  while (intersect && count < 10) {
    intersect = color(ray, col, rec);
    count++;
  }
  return col;
}

void main() {
  vec3 col = cast_ray();
  vec3 lcol = texture2D(lastFrame, fragPos*0.5+0.5).xyz;
  vec3 fcol = col+lcol;
  Color = vec4(fcol, 1.0);
}