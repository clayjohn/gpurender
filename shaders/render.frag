# version 330
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
const int DISK = 5;

const int DIFFUSE = 1;
const int METAL = 2;
const int DIALECTRIC = 3;
const int LIGHT = 4;
const int ISOTROPIC = 5;

const int TRUE = 1;
const int FALSE = 0;

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
  int volume;
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
uniform int BVH_DEPTH;
const int MAX_OBJECTS = 36;
uniform Hitable hitables[MAX_OBJECTS];
uniform Material materials[MAX_OBJECTS];
uniform Camera camera;
const int MAX_DEPTH = 10;
vec3 estack[MAX_DEPTH + 1];
vec3 cstack[MAX_DEPTH + 1];

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
  return (fract((p.x+p.y)*p.z));
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

/*bool hit_triangle(Hitable t, Ray ray, float t_min, float t_max, inout Hit_record rec) {
  vec3 perp = cross(t.dir, vec3(1.0, 0.0, 0.0));
  vec3 a = t.pos + vec3();
  vec3 b = t.pos + vec3();
  vec3 c = t.pos + vec3();
  float3 edge1 = b - a;
	float3 edge2 = c - a;

	float3 pvec = cross(ray.dir, edge2);
	float det = dot(edge1, pvec);
	if(det == 0.0) {
		return false;
  }
	float inv_det = 1.0f / det;

	float3 tvec = ray.pos - a;
	out_bary1 = dot(tvec, pvec) * inv_det;

	float3 qvec = cross(tvec, edge1);
	out_bary2 = dot(d, qvec) * inv_det;
	//out_lambda = dot(edge2, qvec) * inv_det;

	bool hit = (out_bary1 >= 0.0 && out_bary2 >= 0.0 && (out_bary1 + out_bary2) <= 1.0);
	return hit;

}*/

bool hit_disk(Hitable h, Ray ray, float t_min, float t_max, inout Hit_record rec) {
  float denom = dot(h.dir, ray.dir);
  if (abs(denom) > 0.0001) // your favorite epsilon
  {
    float t = dot((h.pos - ray.pos),h.dir) / denom;
    if (t<t_min || t>t_max) {
      return false;
    }
    vec3 pos = ray.pos + ray.dir*t;
    if (distance(pos, h.pos)>h.size) {
      return false;
    }

    if (t >= 0) {
      rec.t = t;
      rec.p = ray.pos + ray.dir*t;
      rec.normal = h.dir;
      return true;
    }  // you might want to allow an epsilon here too
  }
  return false;
}

bool hit_plane(Hitable h, Ray ray, float t_min, float t_max, inout Hit_record rec) {
  float denom = dot(h.dir, ray.dir);
  if (abs(denom) > 0.0001) // your favorite epsilon
  {
    float t = dot((h.pos - ray.pos),h.dir) / denom;
    if (t<t_min || t>t_max) {
      return false;
    }
    vec3 pos = ray.pos + ray.dir * t;
    if (h.size != 0.0) {
      if ((pos.yz-h.pos.yz).x>h.size || (pos.yz-h.pos.yz).x<-h.size || 
          (pos.xy-h.pos.xy).x>h.size || (pos.xy-h.pos.xy).x<-h.size || 
          (pos.xz-h.pos.xz).x>h.size || (pos.xz-h.pos.xz).x<-h.size || 
          (pos.yz-h.pos.yz).y>h.size || (pos.yz-h.pos.yz).y<-h.size || 
          (pos.xy-h.pos.xy).y>h.size || (pos.xy-h.pos.xy).y<-h.size || 
          (pos.xz-h.pos.xz).y>h.size || (pos.xz-h.pos.xz).y<-h.size ) {
        return false;
      }
    }
    if (t >= 0) {
      rec.t = t;
      rec.p = pos;
      rec.normal = h.dir;
      return true;
    }  // you might want to allow an epsilon here too
  }
  return false;
}

bool hit_cube(Hitable h, Ray ray, float t_min, float t_max, inout Hit_record rec) {
  //use six planes may be horrible but should work
  vec3 planes[6] = vec3[6](vec3(1.0, 0.0, 0.0), vec3(-1.0, 0.0, 0.0), 
                           vec3(0.0, 1.0, 0.0), vec3(0.0, -1.0, 0.0), 
                           vec3(0.0, 0.0, 1.0), vec3(0.0, 0.0, -1.0));
  Hitable temp = Hitable(h.pos, h.size, vec3(0.0, 1.0, 0.0), PLANE, 0);
  Hit_record temp_rec = rec;
  float closest = t_max;
  bool hit_anything = false;
  for (int i = 0; i<6;i++) {
    temp.pos = h.pos + planes[i] * h.size;
    temp.dir = planes[i];
    if (hit_plane(temp, ray, t_min, closest, temp_rec)) {
      closest = temp_rec.t;
      hit_anything = true;
    } //do this for every plane
  }
  if (hit_anything) {
    rec = temp_rec;
  }
  return hit_anything;
}

bool hit(const Hitable s, const Ray ray, const float t_min, float t_max, inout Hit_record rec) {
  if (s.type == SPHERE) {
    return hit_sphere(s, ray, t_min, t_max, rec);
  } else if (s.type == PLANE) {
    return hit_plane(s, ray, t_min, t_max, rec);
  } else if (s.type == DISK) {
    return hit_disk(s, ray, t_min, t_max, rec);
  } else if (s.type == CUBE) {
    return hit_cube(s, ray, t_min, t_max, rec);
  }
  return false;
}

bool hit_volume(const Hitable h,const Ray ray,const float t_min, float t_max, inout Hit_record rec) {
  Hit_record rec1, rec2;
  float inf = 10000.0;
  if (hit(h, ray, -inf, inf, rec1)) {
    if (hit(h, ray, rec1.t+0.001, inf, rec2)) {
      rec1.t = max(rec1.t, t_min);
      rec2.t = min(rec2.t, t_max);
      if (rec1.t >= rec2.t) {
        return false;
      }
      rec1.t = max(rec1.t, 0.0);
      float distance_inside_boundary = (rec2.t-rec1.t)*length(ray.dir);
      // TODO change the 0.01 to a passed in parameter
      //do this by changing volume to density
      //where a density of one (or arbitrary number) flips to a solid structure
      //100.0 should be 1.0/h.density
      float hit_distance = -(1.0) * log(hash31(vec3(rec2.t, rec1.t, rec2.t*37.91+rec1.t*12.53)));
      if (hit_distance < distance_inside_boundary) {
        rec.t = rec1.t + hit_distance / length(ray.dir);
        rec.p = ray.pos + ray.dir * rec.t;
        rec.normal = vec3(1.0, 0.0, 0.0);
        return true;
      }
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
    return false;
}

bool scatter(const Ray r,const Hit_record rec, inout vec3 attenuation, inout Ray scattered){
  if (rec.material.type == LIGHT) {
    return false;
  }
  else if (rec.material.type == DIFFUSE) {
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
  else if (rec.material.type == ISOTROPIC) {
    scattered = Ray(rec.p, hash33(rec.p));
    attenuation = rec.material.albedo;
    return true;
  }
}

bool hit_world(const Ray ray,const float t_min, float t_max, inout Hit_record rec) {
  Hit_record temp_rec;
  bool hit_anything = false;
  float closest_so_far = t_max;
  
  for (int i = 0;i<MAX_OBJECTS;i++) {
    if (i < NUM_OBJECTS){
      if (hitables[i].volume == TRUE) {
        if (hit_volume(hitables[i], ray, t_min, closest_so_far, temp_rec)) {
          closest_so_far = temp_rec.t;
          rec = temp_rec;
          rec.material = materials[i];
          hit_anything = true;
        }
      }
      else if (hit(hitables[i], ray, t_min, closest_so_far, temp_rec)) {
        closest_so_far = temp_rec.t;
        rec = temp_rec;
        rec.material = materials[i];
        hit_anything = true;
      }  
    }
  }
  return hit_anything;
}

vec3 emitter(Hit_record rec){
  return rec.material.emission;
}

bool color(inout Ray r, inout vec3 col, inout Hit_record rec, in int depth) {
  if (hit_world(r, 0.001, 10000.0, rec)) {
    Ray scattered;
    vec3 attenuation;
    vec3 emitted = emitter(rec);
    if (scatter(r, rec, attenuation, scattered)) {
      r = scattered;
      estack[depth] = emitted;
      cstack[depth] = attenuation;
      return true;
    } else {
      col = emitted;
      return false;
    }
  } else {
    vec3 unit_direction = normalize(r.dir);
    float t = 0.5*(unit_direction.y+1.0);
    col *= mix(vec3(1.0), vec3(0.5, 0.7, 1.0), t);
    //col *= 0.0;
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
  vec3 dir = camera.corner + uv.x * camera.width + uv.y*camera.height - camera.origin - offset;
  return Ray(camera.origin + offset, dir);
}

vec3 cast_ray() {
  vec2 uv = (gl_FragCoord.xy)+antia(gl_FragCoord.xy, time);
  uv /= resolution;
  Ray ray = get_ray(uv);
  bool intersect = true;
  vec3 col = vec3(1.0);
  int count = 0;
  Hit_record rec;
  while (intersect && count < MAX_DEPTH) {
    intersect = color(ray, col, rec, count);
    if (intersect) {
    count++;
    }
  }
  for (int i = count-1;i>=0;i--) {
    col *= cstack[i];
    col += estack[i];
  }
  return col;
}

void main() {
  vec3 col = cast_ray();
  //copy color from last frame
  vec3 lcol = texture2D(lastFrame, fragPos*0.5+0.5).xyz;

  if (isnan(col).x) {
    col = lcol;
  }
  vec3 fcol = col+lcol;
  Color = vec4(fcol, 1.0);
}



/*
   triangle(vec3, a, vec3 b, vec3 c, ray.dir, ray.orign)
   Triangle
   float3 edge1 = b - a;
	float3 edge2 = c - a;

	float3 pvec = cross(d, edge2);
	float det = dot(edge1, pvec);
	if(det == 0.f)
		return false;
	float inv_det = 1.0f / det;

	float3 tvec = o - a;
	out_bary1 = dot(tvec, pvec) * inv_det;

	float3 qvec = cross(tvec, edge1);
	out_bary2 = dot(d, qvec) * inv_det;
	out_lambda = dot(edge2, qvec) * inv_det;

	bool hit = (out_bary1 >= 0.0f && out_bary2 >= 0.0f && (out_bary1 + out_bary2) <= 1.0f);
	return hit;
}

*/



