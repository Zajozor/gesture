VERTEX_SHADER = """
attribute vec2 positions;
attribute vec3 colors;

varying vec4 vColor;

void main ()
{
    gl_Position = vec4(positions, 0.0, 1);
    vColor = vec4(colors, 1.);
}
"""

FRAGMENT_SHADER = """
varying vec4 vColor;
void main()
{
    gl_FragColor = vColor;
}
"""
