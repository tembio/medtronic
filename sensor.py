import time 
import random
import uuid

class Sensor:
    i=0
    def __init__(self):
        self.sensor_id = str(uuid.uuid4())
        print(f"Created sensor: {self.sensor_id}")

    def _event_type(self):
        event_types = ["nominal", "info", "warning", "error", "critical"]
        return random.choices(event_types, cum_weights=[60, 24, 10, 5, 1],k=1)[0]
    
    def do_work(self):
        Sensor.i+=1
        time.sleep(random.uniform(0.1, 1.5))

    @property
    def state(self):
        return {
            "id": self.sensor_id,
            "event": {
                "type": self._event_type(),
                "readings": [
                    random.randint(0, 100),
                    random.randint(0, 100),
                    random.randint(0, 100)
                ]
            },
            "timestamp": int(time.time())
        }
