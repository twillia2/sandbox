from logger import Logger
from nvr_communication_manager import NVRCommManager
from event_manager import EventManager, Event
import event_manager
import image_manager

class CallbackHandler:

    def __init__(self, nvr_ip, user, password):
        self._log = Logger('hik.log', None)
        self._nvr_handler = NVRCommManager(nvr_ip, user, password, self)
        self._event_manager = EventManager(self)

    def process_response(self, response: dict):
        for rsp_dic in response:
            self._event_manager.extract_event(rsp_dic[event_manager.EVENT_KEY])

    def get_image_snapshot(self, event: Event):
        self._nvr_handler.get_image_snapshot(event)

    def process_event_images(self, events: dict):
        image_manager.process_event_images(events)

    def go(self):
        self._nvr_handler.read_event_stream()
