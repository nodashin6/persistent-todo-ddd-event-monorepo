import collections
import json
from typing import Dict, Deque

from ...application.message_queue import MessageQueue


class InMemoryMessageQueue(MessageQueue):
    def __init__(self):
        self._queues: Dict[str, Deque] = collections.defaultdict(collections.deque)
        self._next_msg_id = 1

    def send(self, queue_name: str, message: dict):
        # The real pgmq returns a tuple, but we only care about the message itself
        # for the worker. Here we just store the message content.
        # The in-memory version will return a simplified tuple from read().
        msg_id = self._next_msg_id
        self._queues[queue_name].append((msg_id, json.dumps(message)))
        self._next_msg_id += 1

    def read(self, queue_name: str, count: int, visibility_timeout: int):
        if not self._queues[queue_name]:
            return None

        # Simplification: Ignore count and vt. Just pop one message.
        # The real pgmq returns (msg_id, read_ct, enqueued_at, vt, message)
        # We'll simulate that with simplified values.
        msg_id, message_str = self._queues[queue_name].popleft()
        return (msg_id, 1, None, None, message_str)

    def delete(self, queue_name: str, msg_id: int):
        # In this simple in-memory version, read() is destructive (it pops the item),
        # so delete() doesn't need to do anything.
        pass
