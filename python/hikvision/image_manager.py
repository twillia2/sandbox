import uuid
import io
import logging
from event_manager import Event
from PIL import Image

#maps uuids to lists of JPEG images for each event
capture_lists = {}

def generate_uuid():
    return str(uuid.uuid4())

def add_image(uuid_key, image_data):
    if uuid_key not in capture_lists:
        capture_lists[uuid_key] = []
    capture_lists[uuid_key].append(image_data)

def convert_jpeg_images_to_gif(events: dict) -> bool:
    log = logging.getLogger('hikvision')
    log.debug(f'events len: {len(events)}')
    image_sequence = []
    e: Event
    for e in events:
        for image in e.captures():
            image_sequence.append(image)
    
        image_sequence[0].save(f'{e.timestamp()}_{e.camera_name()}_{e.uuid()}.gif',
               save_all=True, append_images=image_sequence[1:], optimize=True, duration=1000, loop=0)
        log.debug(f'generated gif: {e.uuid()}')
    
    return True

def process_event_images(event_list: dict):
    if len(event_list) > 0:
        log = logging.getLogger('hikvision')
        removed_uuids = []

        for uuid, events in event_list.items():
            if convert_jpeg_images_to_gif(events):
                removed_uuids.append(uuid)
            else:
                log.debug(f'No images to process for {uuid}')

        for uuid in removed_uuids:
            event_list.pop(uuid)

def write_jpg(e: Event, data):
    with open(f'{e.timestamp()}_{e.type()}_{e.camera_name()}.jpg', 'wb') as f:
        if data:
            f.write(data)

def write_image_jpg(event_list: list):
    if len(event_list) > 0:
        for uuid, events in event_list:
            e: Event
            for e in events:
                buf: io.BytesIO
                for buf in e.captures:
                    buf.seek(0)
                    data = buf.getvalue()
                    with open(f'{e.timestamp()}_{e.type()}_{e.camera_name()}.jpg', 'wb') as f:
                        if data:
                            f.write(data)