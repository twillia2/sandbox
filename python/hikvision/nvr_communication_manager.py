from hikvisionapi import Client
from event_manager import Event
from PIL import Image
import io
import logging

class NVRCommManager:
    nvr = None
    MAX_TIMEOUT = 99999999
    log = None

    def __init__(self, nvr_ip, user, password, handler):
        self._nvr_ip = nvr_ip
        self._user = user
        self._password = password
        self._handler = handler
        global log
        log = logging.getLogger('hikvision')

    def read_event_stream(self):
        self.nvr = Client(self._nvr_ip, self._user, self._password, timeout=self.MAX_TIMEOUT)

        while True:
            try:
                response = self.nvr.Event.notification.alertStream(method='get', type='stream')
                if response:
                    self._handler.process_response(response)
                    log.debug(response)
            except Exception as e:
                print(e)
                pass

    def get_image_snapshot(self, event: Event):
        channel = f'{event.camera_id()}01'
        capture = self.nvr.Streaming.channels[channel].picture(method='get', type='opaque_data')
        buf = io.BytesIO()
        for chunk in capture.iter_content(chunk_size=1024):
            if chunk:
                buf.write(chunk)
        
        buf.seek(0)
        image = Image.open(buf)

        event.add_capture(image)