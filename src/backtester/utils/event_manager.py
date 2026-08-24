from collections import defaultdict
from typing import Callable, Dict, List

class EventManager:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._topic_log: Dict[str, List[dict]] = defaultdict(list)

    def subscribe(self, topic: str, listener_callback: Callable):
        self._subscribers[topic].append(listener_callback)

    def publish(self, topic: str, message: dict):
        self._topic_log[topic].append(message)
        
        # Dispatch to all subscribed listeners
        if topic in self._subscribers:
            for listener in self._subscribers[topic]:
                listener(message)

    def get_topic_history(self, topic: str) -> List[dict]:
        return self._topic_log.get(topic, [])