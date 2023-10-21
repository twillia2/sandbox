import uuid
import datetime
import logging
from PIL import Image

EVENT_TYPE_VIDEOLOSS = 'videoloss'
EVENT_TYPE_MOTION = 'VMD'
EVENT_TYPE_LINE_DETECTION = 'linedetection alarm'
EVENT_TYPE_UNKNOWN = 'unknownType'

EVENT_KEY = "EventNotificationAlert"
EVENT_TYPE_KEY = "eventType"
EVENT_STATE_KEY = "eventState"
EVENT_CAMERA_KEY = "channelName"
EVENT_CAMERA_ID_KEY = "channelID"
EVENT_TIMESTAMP_KEY = 'dateTime' #2023-04-25T12:10:4500:00

EVENT_STATE_UNKNOWN = 'unknownState'
EVENT_VALUE_NONE = 'None'

EVENT_STATE_ACTIVE = 'active'
EVENT_STATE_INACTIVE = 'inactive'

TIMESTAMP_LAST_HB = ''
NVR_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
UUID_LAST_EVENT = ''

known_event_types = [
                    EVENT_TYPE_VIDEOLOSS,
                    EVENT_TYPE_MOTION,
                    EVENT_TYPE_LINE_DETECTION
                    ]


class Event:
    def __init__(self, event_uuid: uuid, event_type: str, 
                 event_camera_name: str, event_camera_id: str,
                 event_timestamp: datetime):
        self._uuid = event_uuid
        self._type = event_type
        self._camera_name = event_camera_name
        self._camera_id = event_camera_id
        self._timestamp = event_timestamp
        self._captures = []

    def __eq__(self, other):
        if other == None:
            return False
        
        if self.uuid() == None or other.uuid() == None:
            return False
        
        return self.uuid() == other.uuid()

    def __hash__(self):
        return self.uuid().int

    def uuid(self) -> uuid:
        return self._uuid
    
    def type(self) -> str:
        return self._type
    
    def camera_name(self) -> str:
        return self._camera_name
    
    def camera_id(self, camera_id: str):
        self._camera_id = camera_id
    
    def camera_id(self) -> str:
        return self._camera_id
    
    def timestamp(self) -> datetime:
        return self._timestamp
    
    def add_capture(self, capture: Image):
        self._captures.append(capture)

    def captures(self) -> dict:
        return self._captures


class EventManager:

    def __init__(self, handler):
        self._handler = handler
        self.log = logging.getLogger('hikvision')
        self._events = {}
        self._last_event = None
        self._TIMESTAMP_LAST_HB = datetime.datetime.now()

    def add_event(self, event: Event):
        if event not in self._events:
            self._events[event] = []
            print(f'Added event {event.uuid()} as new event with empty dict')

        for c in event.captures:
            self._events[event].append(c)
            print(f'Appended images from {event.uuid()} to {event.uuid()}')
        self.update_last_event(event)

    def get_events(self) -> dict:
        return self._events
            
    def delete_event(self, uuid: uuid):
        self._events.pop(uuid)
        
    def last_event(self) -> Event:
        return self._last_event
    
    def update_last_event(self, event):
        self._last_event = event

    def update_hb_timestamp(self, timestamp):
        self._TIMESTAMP_LAST_HB = timestamp

    def last_hb_timestamp(self) -> datetime:
        return self._TIMESTAMP_LAST_HB

    def generate_uuid(self) -> uuid:
        return uuid.uuid4()

    def parse_event_timestamp(self, timestamp: str) -> datetime:
        # do some stupid string manipulation because the timestamp the NVR gives is garbage
        timestamp_with_offset = timestamp[:19] + '+' + timestamp[19:]
        return datetime.datetime.strptime(timestamp_with_offset, NVR_TIMESTAMP_FORMAT)

    def is_heartbeat_event(self, event_type: str, event_state: str, 
                        event_camera_id: str, event_timestamp: datetime) -> bool:
        if (event_type == EVENT_TYPE_VIDEOLOSS and 
            event_state == EVENT_STATE_INACTIVE and 
            (event_camera_id == None or event_camera_id == EVENT_VALUE_NONE)):
            
            self.update_hb_timestamp(event_timestamp)
            return True
        
        else:
            return False

    def last_event_was_hb(self) -> bool:
        if (self.last_event().camera_id == None and self.last_event().type == EVENT_TYPE_VIDEOLOSS):
            return True
        
        return False

    '''
    An Event is considered unique if it is from the same camera and
    has the same type, within a time window not punctuated by a 'heartbeat'
    (a videoloss event with a 'None' camera)
    So event notifications and associated captured images will be combined into a single Event 
    if they share a camera and a type, and the timestamp on the event is after the last
    heartbeat. However, it should not be possible to add an alert to an Event after a heartbeat
    as the heartbeat notifications trigger a purging of the Events
    '''
    def is_new_event(self, event_type: str, event_state: str, 
                        event_camera_id: str, event_timestamp: datetime) -> bool:
        if self.last_event() == None or self.last_event_was_hb():
            return True
        
        elif (event_camera_id == self.last_event().camera_id() and
            event_type == self.last_event().type() and
            event_timestamp > self.last_hb_timestamp()):
            return False
        
        else:
            return True

    def process_event(self, event_type: str, event_state: str, event_timestamp: str) -> bool:
        if event_state == EVENT_STATE_ACTIVE:
            return True
        else:
            return False

    def extract_event(self, event: any):
        event_type = event[EVENT_TYPE_KEY]
        event_state = event[EVENT_STATE_KEY]
        event_camera_id =  event[EVENT_CAMERA_ID_KEY]
        event_camera_name = event[EVENT_CAMERA_KEY]
        raw_timestamp = event[EVENT_TIMESTAMP_KEY]
        event_timestamp = self.parse_event_timestamp(raw_timestamp)

        if self.is_heartbeat_event(event_type, event_state, event_camera_id, event_timestamp):
            # use heartbeats (aka spurious videoloss alarms) to trigger generation of 
            # the gifs from the captures
            self._handler.process_event_images(self._events)
            return

        if self.process_event(event_type, event_state, event_timestamp):
            event = None
            if (self.is_new_event(event_type, event_state, event_camera_id, event_timestamp)):
                event = Event(self.generate_uuid(), event_type, event_camera_name, event_camera_id, event_timestamp)
            else:
                event = Event(self.last_event().uuid(), event_type, event_camera_name, event_camera_id, event_timestamp)

            self._handler.get_image_snapshot(event)

            self.add_event(event)
            self.update_last_event(event)


    def process_image(event: Event, image_data):
        event.add_capture(image_data)