import numpy as np
from vispy import app, gloo
from threading import Thread
from .data import FourierGesture
from .util import get_color_for_value
from vispy.visuals import TextVisual
from vispy.visuals.transforms import TransformSystem

app.use_app('PyQt5')

dist_vertex_shader = """
uniform float row_count;

attribute float row;
attribute vec2 position;
attribute vec3 color;

varying vec4 vertexColor;

void main ()
{
    float x = position.x / 4 - 1;
    float y = (position.y + row) / row_count * 2  - 1;
    gl_Position = vec4(x, y, 0.0, 1);
    vertexColor = vec4(color, 1.);
}
"""

gesture_vertex_shader = """
uniform float row_count;
uniform float column_count;

attribute float row;
attribute float column;
attribute vec2 position;
attribute vec3 color;

varying vec4 vertexColor;

void main () 
{
    float x = (position.x + column) / column_count * 1.75 - 0.75;
    float y = (position.y + row) / row_count * 2  - 1;
    gl_Position = vec4(x, y, 0.0, 1);
    vertexColor = vec4(color, 1.);
}

"""


fragment_shader = """
varying vec4 vertexColor;

void main()
{
    gl_FragColor = vertexColor;
}
"""


class MultiFourierCanvas(app.Canvas):
    def __init__(self, gesture_size, q, computation, gesture_set_config, *args, **kwargs):
        app.Canvas.__init__(self, *args, **kwargs)
        gloo.set_clear_color((1, 1, 1, 1))

        self.gesture_size = gesture_size
        self.queue = q
        self.computation = computation
        self.gesture_set_config = gesture_set_config

        self.dist_program = gloo.Program(dist_vertex_shader, fragment_shader)
        self.gesture_program = gloo.Program(gesture_vertex_shader, fragment_shader)

        self.dist_texts = []
        for i in range(len(self.gesture_set_config)):
            dist_text = TextVisual('gesture ' + str(i))
            dist_text.pos = 50, 600 - (60 + i * (600.0 / len(self.gesture_set_config)))
            self.dist_texts.append(dist_text)

        self.redraw_timer = app.Timer('auto', connect=self.on_timer, start=True)

        # We do this for the texts
        self.transform_system = TransformSystem(self)

    """ Routine used to pull data from data_store to arrays for shaders to prepare to draw"""
    def update_program_data(self):
        predictions = self.computation.prediction_state.predictions
        current_gesture_size = self.computation.prediction_state.current_gesture.gesture_size

        # Data for displaying distances from recorded gesture sets
        self.dist_program['row_count'] = len(predictions)

        dist_rows = np.empty((0, ))
        dist_positions = np.empty((0, 2))
        dist_colors = np.array([[0, 0, 0]] * (len(predictions) * current_gesture_size)).astype(np.float32)

        mapping = np.linspace(0.05, 0.95, current_gesture_size)
        for i in range(len(predictions)):
            dist_rows = np.concatenate((dist_rows, [i] * current_gesture_size))

            # TODO constant from some config
            normalised_predictions = predictions[i] / 2.0\
                / max(1, len(self.computation.prediction_state.data_store.gesture_sets[i].gestures))
            dist_positions = np.concatenate((dist_positions,
                                            np.c_[mapping, normalised_predictions]
                                            .astype(np.float32)))

            self.dist_texts[i].text = str(predictions[i][-1])
            self.dist_texts[i].color = get_color_for_value(predictions[i][-1])

        self.dist_program['position'] = dist_positions.astype(np.float32)
        self.dist_program['row'] = dist_rows.astype(np.float32)
        self.dist_program['color'] = dist_colors.astype(np.float32)

        # Data for displaying actual recorded gestures
        self.gesture_program['row_count'] = len(predictions)
        self.gesture_program['column_count'] = max([len(gesture_set.gestures)
                                                    for gesture_set in self.computation.prediction_state
                                                   .data_store.gesture_sets])

        gesture_rows = []
        gesture_columns = []
        gesture_positions = np.empty((0, 2))
        gesture_colors = np.empty((0, 3))

        for i in range(len(self.computation.prediction_state.data_store.gesture_sets)):
            gesture_set = self.computation.prediction_state.data_store.gesture_sets[i]
            gesture_rows += [i] * (current_gesture_size * len(gesture_set.gestures) * 3)

            for j in range(len(gesture_set.gestures)):
                gesture_columns += [j] * (current_gesture_size * 3)

                gesture = gesture_set.gestures[j]
                gesture_colors = np.concatenate((gesture_colors, gesture.colors.reshape(current_gesture_size*3,3)))

                for k in range(3):
                    gesture_positions = np.concatenate((gesture_positions, np.c_[
                        gesture.mapping,
                        gesture.data[k] / 10000.0  # TODO constant from some config
                    ].astype(np.float32)))

        self.gesture_program['row'] = np.array(gesture_rows).astype(np.float32)
        self.gesture_program['column'] = np.array(gesture_columns).astype(np.float32)
        self.gesture_program['position'] = gesture_positions.astype(np.float32)
        self.gesture_program['color'] = gesture_colors.astype(np.float32)

    def on_draw(self, event):
        gloo.clear(color=True)
        self.gesture_program.draw('line_strip')  # TODO use something non-continuous between gestures but not > points
        self.dist_program.draw('points')

        for dist_text in self.dist_texts:
            dist_text.draw(self.transform_system)

    def on_timer(self, event):
        self.update_program_data()
        self.update()

    def on_resize(self, event):
        gloo.set_viewport(0, 0, *event.size)

    def on_key_press(self, event):
        print('key', event.key.name, 'was pressed')
        for i in range(len(self.gesture_set_config)):
            if event.key.name == self.gesture_set_config[i]['hotkey']:
                new_gesture = FourierGesture()
                # We append the gesture first so that we can see the recording progress
                self.computation.prediction_state.data_store.gesture_sets[i].add_gesture(new_gesture)
                th = Thread(target=self.computation.record_to_gesture, args=(self.queue, new_gesture), daemon=True)
                th.start()
