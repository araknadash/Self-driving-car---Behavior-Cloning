from flask import Flask
import socketio
import eventlet
from keras.models import load_model
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import cv2

sio = socketio.Server()
app = Flask(__name__)
speed_limit = 10
def pre_processing(image):
    image = image[60:135,:,:]
    image = cv2.cvtColor(image, cv2.COLOR_RGB2YUV) #luminosity and chromiums
    image = cv2.GaussianBlur(image, (3,3), 0)
    image = cv2.resize(image, (200,66))
    image = image/255
    return image

@sio.on('telemetry')
def telemetry(sid, data):
    speed = float(data['speed'])
    image = Image.open(BytesIO(base64.b64decode(data['image'])))
    image = np.asarray(image)
    image = pre_processing(image)
    image = np.array([image])
    steering_angle = float(model.predict(image))
    throttle = 1.0 - speed/speed_limit
    print('{}, {}, {}'.format(steering_angle, throttle, speed))
    send_control(steering_angle, 1.0)

#Check connection status
@sio.on('connect')
def connect(sid, environment):
    print('Good to go!')
    send_control(0, 0) #0 steering angle and 1 throttle

def send_control(steering_angle, throttle):
    sio.emit('steer', data = {'steering_angle': steering_angle.__str__(),
    'throttle': throttle.__str__()})

if __name__ == '__main__':
    model = load_model('arc_model.h5')
    app = socketio.Middleware(sio, app)
    eventlet.wsgi.server(eventlet.listen(('', 4567)), app)
