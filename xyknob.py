import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.properties import StringProperty
from kivy.properties import BooleanProperty
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout

kivy.require('1.10.1')

'''
XYKnob
Created by Seth Abraham, October 22, 2018
Total rewrite October 26, 2018
A 'knob' for setting two values.  Values are on
the axises of an XY plane, and selected point indicates
the settings for X and Y.  Essentially two knobs set by
indicating a point on the XY plane.
'''

xykivystring = '''
#:kivy 1.10.1
#
# from BoxLayout
<XYKnob>
    orientation: 'vertical'
    opacity: .25 if root.disabled else 1
    id: vbox
    BoxLayout:
        orientation: 'horizontal'
        Label:
            text: ''
            width: 0.5 * ( vbox.width - mypad.width )
            size_hint_x: None
        RelativeLayout:
            #Label:
            #    id: mybackground 
            Label:
                id: mypad
                width: self.height
                size_hint_x: None
                font_size: 25
                color: [ 144/255, 228/255, 1, 1 ]
                text: str(root.value_x + root.labeloffset) + ',' + str(root.value_y + root.labeloffset)
                canvas.after:
                    Line:
                        points: root.xy_knob_trackx
                    Line:
                        points: root.xy_knob_tracky
                    Color:
                        rgba: [ 36/255, 129/255, 215/255, 1 ]
                    Line:
                        width: 2
                        circle: [root.value_x * 0.01 * self.width, root.value_y * 0.01 * self.height, 2.5]
                    Color:
                        rgba: [ 36/255, 129/255, 215/255, 1 ]
                    Line:
                        width: 1
                        points: [ 0,.5*mypad.height, mypad.width, .5*mypad.width ] if root.crosshairs else []
                    Line:
                        points: [ .5*mypad.width, 0, .5*mypad.width, mypad.width ] if root.crosshairs else []
                canvas.before:
                    Color:
                        rgba: [.4, .4 , .4, .5]
                    Line:
                        width: 2
                        rectangle: (*self.pos, *self.size)
                #end mypad
            Label:
                id: x_axis
                pos: ( mypad.center_x - .5*self.width, 0 )
                text: root.label_x
                size: self.texture_size
                size_hint: (None,None)
                font_size: 12 #int(.5 + 1.14 * mypad.width / max(len(root.ids.y_axis.text), len(self.text)) )
                color: [.4, .4 , .4, .6]
            Label:
                id: y_axis
                #pos_hint: { 'center_y':.5, 'center_x':0.08 }
                pos: ( -.3 *self.width, mypad.center_y )
                text: root.label_y
                font_size: 12 # int(.5 + 1.14 * mypad.width / max(len(root.ids.x_axis.text), len(self.text)) )
                color: [.4, .4 , .4, .6]
                size: self.texture_size
                size_hint: (None,None)
                canvas.before:
                    PushMatrix
                    Rotate
                        angle: 90
                        origin: self.center
                canvas.after:
                    PopMatrix
            #end rellay
        Label:
            width: 0.5 * ( vbox.width - mypad.width  )
            size_hint_x: None
            text: ''
    Label:
        color: 144/255, 228/255, 1, 1
        text: root.text
        #font_size: int(.5 + 1.14 * mypad.width / len(self.text) )
        font_size: 15
        size: self.texture_size
        size_hint_y: None
    #end xyknob
#-----------------------
'''


class XYKnob(BoxLayout):
    xy_knob_trackx = ListProperty([])
    xy_knob_tracky = ListProperty([])

    label_x = StringProperty('X-axis')
    value_x = NumericProperty(50)
    mouse_set_value_x = NumericProperty(0)

    label_y = StringProperty('Y-axis')
    value_y = NumericProperty(50)
    mouse_set_value_y = NumericProperty(0)

    labeloffset = NumericProperty(-50)
    text = StringProperty('Title')
    crosshairs = BooleanProperty(False)

    addresses = ListProperty([])

    def _compute_pos_and_val(self, touch):
        # determine the touch position in a mypad coordinate space
        # clamps that position to the size of mypad (overkill until until we move!)
        # and converts the coordinates into x,y values

        relative_position = list(self.ids.mypad.to_widget(*touch.pos, True))

        relative_position[0] = sorted([relative_position[0], 0, self.ids.mypad.width])[1]
        relative_position[1] = sorted([relative_position[1], 0, self.ids.mypad.height])[1]

        self.value_x = int(relative_position[0] / self.ids.mypad.width * 100.0)
        self.value_y = int(relative_position[1] / self.ids.mypad.height * 100.0)
        self.mouse_set_value_x += 1
        self.mouse_set_value_y += 1

        return relative_position

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and not self.disabled:
            if touch.button == 'left':
                touch.grab(self)
                rel_pos = self._compute_pos_and_val(touch)
                # draw tracking lines
                self.xy_knob_tracky.extend([rel_pos[0], 0, rel_pos[0], self.ids.mypad.top])
                self.xy_knob_trackx.extend([0, rel_pos[1], self.ids.mypad.right, rel_pos[1]])
            elif touch.button == 'right':
                self.value_x = 50 if self.crosshairs == True else 70
                self.value_y = 50 if self.crosshairs == True else 20
                self.mouse_set_value_x += 1
                self.mouse_set_value_y += 1
            else:
                return False
            return True
        return False

    def on_touch_move(self, touch):
        if touch.grab_current is self and not self.disabled:
            rel_pos = self._compute_pos_and_val(touch)

            # update tracking lines.
            self.xy_knob_tracky[0] = rel_pos[0]
            self.xy_knob_tracky[2] = rel_pos[0]

            self.xy_knob_trackx[1] = rel_pos[1]
            self.xy_knob_trackx[3] = rel_pos[1]

            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self and not self.disabled:
            touch.ungrab(self)

            # remove tracking lines
            del(self.xy_knob_trackx[0:])
            del(self.xy_knob_tracky[0:])

            # update values, ignore the relative position
            rel_pos = self._compute_pos_and_val(touch)

            return True
        return super().on_touch_up(touch)

    def set_knob(self, adr, value):
        if adr & 0x1:
            self.value_x = value
        else:
            self.value_y = value


Builder.load_string(xykivystring)


if __name__ == '__main__':
    kv = '''
BoxLayout:
    orientation: 'vertical'
    BoxLayout:
        size_hint_y: .1
        Button:
            text: "What an I doing here?"
        Button:
            text: "good question"
        Button:
            text: "different sort of knob"
    GridLayout:
        rows: 2
        cols: 6
        padding: 10
        spacing: 10
        
        XYKnob:
            id: primo
            #label_x: 'Cut-off'
            #label_y: "Res"
        XYKnob:
            id: two
            #size: 250,250
        XYKnob:
            id: three
            disabled: True
        XYKnob:
            id: four
        XYKnob:
        XYKnob:
        XYKnob:
            id: notme
            text: 'NotMe'
            labeloffset: 0
        XYKnob:
            crosshairs: True
        XYKnob:
        XYKnob:
            crosshairs: True
        XYKnob:
        XYKnob:
'''
    from kivy.config import Config
    Config.set('input', 'mouse', 'mouse,disable_multitouch')
    class XYKnobApp(App):
        def build(self):
            r = Builder.load_string(kv)
            print(r.ids.notme.ids.mypad.text)
            return r

    XYKnobApp().run()
