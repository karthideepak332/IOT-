import paho.mqtt.client as mqtt 
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import signal
import sys
import datetime as dt
import time
import re

app = Flask(__name__)
socketio = SocketIO(app)

# MQTT setup
mqtt_edge = mqtt.Client('eds_demoiot1' + str(dt.datetime.now()))

def on_message_ultrasonic_sensor(client, userdata, msg):
    global distance
    # Your existing on_message_ultrasonic_sensor logic
    print("Received a new value:", str(msg.payload.decode('utf-8')))
    mqtt_message = str(msg.payload.decode('utf-8'))
    distance_list = mqtt_message.split(":")
    # Extract distance value
    list = re.findall("\d+", distance_list[3])
    if (len(list)<=0):
     distance = 0 
    else:
      distance =  int(list[0])
      

    mqtt_edge.publish('SRMV-DEV090/OUT/LCD:00015','is the distance:LCD:00015:N/A:'+str(distance))
    # Control dc motor based on distance
    if distance  < 10:
        print("hi")
        mqtt_edge.publish('SRMV-DEV090/OUT/LCD:00012','minimum level reached:LCD:00015:N/A:'+str(distance))
        mqtt_edge.publish('SRMV-DEV082/OUT/BUZ:00011','OUT:BUZ:00013:N/A:ON')
        mqtt_edge.publish('SRMV-DEV043/OUT/SLN:00002','OUT:RLY:00002:N/A:OFF')
        mqtt_edge.publish('SRMV-DEV089/OUT/RLY:00012','OUT:RLY:00012:N/A:ON')
    else:
        mqtt_edge.publish('SRMV-DEV090/OUT/LCD:00012','maximum level  reached:LCD:00015:N/A:'+str(distance))
        mqtt_edge.publish('SRMV-DEV082/OUT/BUZ:00011','OUT:BUZ:00013:N/A:OFF')
        mqtt_edge.publish('SRMV-DEV043/OUT/SLN:00002','OUT:RLY:00002:N/A:ON')
        mqtt_edge.publish('SRMV-DEV089/OUT/RLY:00012','OUT:RLY:00012:N/A:OFF')   

def on_connect(client, userdata, flags, rc):
        if rc == 0: 
            print('connected to MQTT broker')
            mqtt_edge.message_callback_add('SRMV-DEV009/IN/ULT:00004',on_message_ultrasonic_sensor)
            mqtt_edge.on_subscribe = on_subscribe_distance
            mqtt_edge.subscribe('SRMV-DEV009/IN/ULT:00004')
        else:
            print('FaiBUZ to connect to MQTT broker, return code %d\n', rc)
    

def on_subscribe_distance(mosq, obj, mid, granted_qos):

    print("Subscribed: " + str(mid) + " " + str(granted_qos))
    time.sleep(1.3)
    mqtt_edge.on_publish = on_publish_stp_success
    mqtt_edge.publish('SRMV-DEV009/BOOT','IN:ULT:00004:CM:STP')
    time.sleep(0.5)
    mqtt_edge.publish('SRMV-DEV090/BOOT','OUT:LCD:00012:N/A:STP')
    time.sleep(0.5)
    mqtt_edge.publish('SRMV-DEV043/BOOT','OUT:SLN:00002:N/A:STP')
    time.sleep(0.5)
    mqtt_edge.publish('SRMV-DEV089/BOOT','OUT:RLY:00012:N/A:STP')
    time.sleep(0.5)
    mqtt_edge.publish('SRMV-DEV082/BOOT','OUT:BUZ:00011:N/A:STP')
   
def on_publish_stp_success(mosq, obj, mid):
# Your existing on_publish_stp_success logic
    mqtt_edge.on_publish = on_publish_srt_success
    time.sleep(0.5)
    mqtt_edge.publish('SRMV-DEV043/BOOT','OUT:SLN:00002:N/A:SRT')
    time.sleep(0.5)
    mqtt_edge.publish('SRMV-DEV009/BOOT','IN:ULT:00004:CM:SRT')
    time.sleep(0.5)
    mqtt_edge.publish('SRMV-DEV090/BOOT','OUT:LCD:00012:N/A:SRT')
    time.sleep(0.5)
    mqtt_edge.publish('SRMV-DEV089/BOOT','OUT:RLY:00012:N/A:SRT')
    time.sleep(0.5)
    mqtt_edge.publish('SRMV-DEV082/BOOT','OUT:BUZ:00011:N/A:SRT')
    

def on_publish_srt_success(mosq, obj, mid):
    print("mid:" + str(mid))

# Flask routes
@app.route('/')
def index():
    return render_template('index.html',distance=distance) 
@socketio.on('update_distance')
def handle_distance():
    emit('distance_update', {'distance': distance})


if __name__ == '__main__':
    mqtt_edge.on_connect = on_connect
    mqtt_edge.message_callback_add('SRMV-DEV009/IN/ULT:00004', on_message_ultrasonic_sensor)
    mqtt_edge.on_subscribe = on_subscribe_distance
    mqtt_edge.on_publish = on_publish_stp_success

    mqtt_edge.connect('192.168.70.13', 1883)
    mqtt_edge.loop_start()  # Start MQTT loop in a separate thread

    app.run(debug=True, host='0.0.0.0',port=5000)