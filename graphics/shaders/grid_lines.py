VERTEX_SHADER = """
#version 120

attribute float a_value; // y coordinate of the position.

attribute vec3 a_index; // row, col, and time index.
varying vec3 v_index;

uniform vec2 u_scale; // 2D scaling factor (zooming).
uniform vec2 u_size; // Size of the table.
uniform float u_n; // Number of samples per signal.

attribute vec3 a_color; // Color.
varying vec4 v_color; // Varying variables used for clipping in the fragment shader.

varying vec2 v_position;
//varying vec4 v_ab;

void main() {
    float nrows = u_size.x;
    float ncols = u_size.y;
    // Compute the x coordinate from the time index.
    float x = -1 + 2*a_index.z / (u_n-1);
    vec2 position = vec2(x - (1 - 1 / u_scale.x), a_value);
    // Find the affine transformation for the subplots.
    vec2 a = vec2(1./ncols, 1./nrows)*.9;
    vec2 b = vec2(-1 + 2*(a_index.x+.5) / ncols,
                  -1 + 2*(a_index.y+.5) / nrows);
    // Apply the static subplot transformation + scaling.
    v_position = u_scale*position; // added this

    gl_Position = vec4(a*v_position+b, 0.0, 1.0);
    v_color = vec4(a_color, 1.);

    v_index = a_index;
    // For clipping test in the fragment shader.
    // v_position = gl_Position.xy;
    // v_ab = vec4(a, b);

}
"""

FRAGMENT_SHADER = """
#version 120
varying vec4 v_color;
varying vec3 v_index;
varying vec2 v_position;
//varying vec4 v_ab;
void main() {
    gl_FragColor = v_color;
    // Discard the fragments between the signals (emulate glMultiDrawArrays).
    if ((fract(v_index.x) > 0.) || (fract(v_index.y) > 0.)) // like what is this for ?
        discard;


    // Clipping test.
    //vec2 test = abs((v_position.xy-v_ab.zw)/v_ab.xy);
    if ((v_position.x > 1) || (v_position.y > 1))
        discard;
}
"""
