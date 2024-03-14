from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
import paho.mqtt.client as mqtt
import datetime as dt
from plyer import accelerometer
from functools import partial

class MotorControlApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.distance_status = Label(text="Status: ", size_hint=(1, None), height=50, valign='middle', halign='center')
        self.accelerometer_enabled = False

    def build(self):
        layout = BoxLayout(orientation='vertical', spacing=10)

        # Control mode selection
        control_mode_layout = BoxLayout(orientation='horizontal', spacing=10)
        self.control_mode_label = Label(text="Control Mode: Button")
        self.checkbox = CheckBox()
        self.checkbox.bind(active=self.on_checkbox_active)
        control_mode_layout.add_widget(self.control_mode_label)
        control_mode_layout.add_widget(Label(text="Button Control"))
        control_mode_layout.add_widget(self.checkbox)
        control_mode_layout.add_widget(Label(text="Accelerometer Control"))

        layout.add_widget(control_mode_layout)

        # Start/Stop buttons
        start_stop_layout = BoxLayout(orientation='horizontal', spacing=10)
        self.start_button = Button(text="Start", on_press=self.start_motor, background_color=(0, 1, 0, 1))
        self.stop_button = Button(text="Stop", on_press=self.stop_motor, background_color=(1, 0, 0, 1))
        start_stop_layout.add_widget(self.start_button)
        start_stop_layout.add_widget(self.stop_button)
        layout.add_widget(start_stop_layout)

        # Motor control buttons
        motor_control_layout = BoxLayout(orientation='horizontal', spacing=10)

        # Forward button
        forward_layout = BoxLayout(orientation='vertical', spacing=10)
        self.forward_speed_spinner = Spinner(text='Speed', values=('Slow', 'Medium', 'Fast'))
        self.forward_speed_spinner.bind(text=self.update_forward_speed)
        self.forward_button = Button(text="Forward", background_color=(0, 1, 0, 1))
        self.forward_button.bind(on_press=self.move_forward)
        forward_layout.add_widget(self.forward_speed_spinner)
        forward_layout.add_widget(self.forward_button)

        # Backward button
        backward_layout = BoxLayout(orientation='vertical', spacing=10)
        self.backward_speed_spinner = Spinner(text='Speed', values=('Slow', 'Medium', 'Fast'))
        self.backward_speed_spinner.bind(text=self.update_backward_speed)
        self.backward_button = Button(text="Backward", background_color=(1, 0, 0, 1))
        self.backward_button.bind(on_press=self.move_backward)
        backward_layout.add_widget(self.backward_speed_spinner)
        backward_layout.add_widget(self.backward_button)

        motor_control_layout.add_widget(forward_layout)
        motor_control_layout.add_widget(backward_layout)

        layout.add_widget(self.distance_status)
        layout.add_widget(motor_control_layout)

        return layout

    def on_checkbox_active(self, checkbox, value):
        self.accelerometer_enabled = value
        if value:
            self.control_mode_label.text = "Control Mode: Accelerometer"
        else:
            self.control_mode_label.text = "Control Mode: Button"

    def update_forward_speed(self, spinner, text):
        self.forward_speed = text.lower()
        
    def update_backward_speed(self, spinner, text):
        self.backward_speed = text.lower()

    def start_motor(self, instance):
        edge = mqtt.Client('eds_demoiot1' + str(dt.datetime.now()))
        edge.connect('20.219.125.196', 1883)
        edge.publish('SRMV-DEV080/BOOT', 'OUT:MOT:00013:N/A:SRT')
        edge.publish('SRMV-DEV080/BOOT', 'OUT:MOT:00013:N/A:SRT')
        edge.loop_start()
        self.distance_status.text = "Status: Motor Started"
        edge.loop_stop()
        edge.disconnect()

    def stop_motor(self, instance):
        edge = mqtt.Client('eds_demoiot1' + str(dt.datetime.now()))
        edge.connect('20.219.125.196', 1883)
        edge.publish('SRMV-DEV080/BOOT', 'OUT:MOT:00013:N/A:STP')
        edge.publish('SRMV-DEV080/BOOT', 'OUT:MOT:00013:N/A:STP')
        edge.loop_start()
        self.distance_status.text = "Status: Motor Stopped"
        edge.loop_stop()
        edge.disconnect()

    def move_forward(self, instance):
        if not self.accelerometer_enabled:
            edge = mqtt.Client('eds_demoiot1' + str(dt.datetime.now()))
            edge.connect('20.219.125.196', 1883)
            speed = self.forward_speed if hasattr(self, 'forward_speed') else 'medium'
            edge.publish('SRMV-DEV077/OUT/MOT:00013', f'OUT:MOT:00013:N/A:60:FWD:{speed.upper()}')
            edge.publish('SRMV-DEV080/OUT/MOT:00013', f'OUT:MOT:00013:N/A:60:FWD:{speed.upper()}')
            edge.loop_start()
            self.distance_status.text = f"Status: Moving Forward ({speed.capitalize()} speed)"
            edge.loop_stop()
            edge.disconnect()

    def move_backward(self, instance):
        if not self.accelerometer_enabled:
            edge = mqtt.Client('eds_demoiot1' + str(dt.datetime.now()))
            edge.connect('20.219.125.196', 1883)
            speed = self.backward_speed if hasattr(self, 'backward_speed') else 'medium'
            edge.publish('SRMV-DEV077/OUT/MOT:00013', f'OUT:MOT:00013:N/A:60:REV:{speed.upper()}')
            edge.publish('SRMV-DEV080/OUT/MOT:00013', f'OUT:MOT:00013:N/A:60:REV:{speed.upper()}')
            edge.loop_start()
            self.distance_status.text = f"Status: Moving Backward ({speed.capitalize()} speed)"
            edge.loop_stop()
            edge.disconnect()

    def start_accelerometer(self):
        accelerometer.enable()
        accelerometer.bind(on_acceleration=self.on_acceleration)

    def stop_accelerometer(self):
        accelerometer.disable()

    def on_acceleration(self, acceleration):
        x, y, z = acceleration
        if x > 1:
            self.move_forward(None)
        elif x < -1:
            self.move_backward(None)

    def on_start(self):
        if self.accelerometer_enabled:
            self.start_accelerometer()

    def on_stop(self):
        if self.accelerometer_enabled:
            self.stop_accelerometer()


if __name__ == '__main__':
    MotorControlApp().run()
