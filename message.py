import functools
from serializable import Serializable
from event_base import EventBase
from uuid import uuid1


class Message(Serializable):
    """tranmission unit for inter-components event notification
    Message is a serilizable class that can be used to track a sequence
    of events, and used for inter-components events notification


    A serializable event can be pushed back to Message event queue and retrieved
    via last_event() or get_event() method.

    No public api is provided to remove an event as it is intended to keep all event
    history. But there's nothing that prevents you from doing it.

    """
    def __init__(self):
        super().__init__()
        self.events = []
        self.id = str(uuid1())

    def push_event(self, event):
        if not isinstance(event, EventBase):
            raise TypeError("{} is not EventBase".format(type(event)))

        # TODO: This shoud be enforceable
        #if type(event) in self:
        #    raise TypeError("{} is already in the message".format(type(event)))

        self.events.append(event)
        return self

    def last_event(self):
        return self.events[-1] if self.count() else None

    def count(self):
        return len(self.events)

    def __contains__(self, event_klass):
        """supports in operator"""
        return self._find_event(event_klass) is not None

    def get_event(self, event_klass):
        return self._find_event(event_klass)

    def _find_event(self, event_klass):
        """
        supports both by type or by string
        """
        if isinstance(event_klass, type):
            event_klass = event_klass.__name__
        l = self.events
        first_from_back = next((l[-i] for i in range(1, len(l) + 1) if l[-i].event_type() == event_klass), None)
        return first_from_back

    def __str__(self):
        return str(self._traverse_dict(self.__dict__))

    def serialize(self):
        for event in self.events:
            event._validate_serializable()
        return super().serialize()


class MessageBatch(Serializable):
    """A batch of messages to be processed together.
    """
    def __init__(self):
        super().__init__()
        self.messages = []
        self.id = str(uuid1())

    def __len__(self):
        return len(self.messages)

    def __iter__(self):
        for msg in self.messages:
            yield msg

    def front(self):
        return self.messages[0]

    def push_back(self, msg):
        if not isinstance(msg, Message):
            raise TypeError("{} is not Message".format(type(msg)))
        self.messages.append(msg)

    def pop_front(self):
        return self.messages.pop(0)

    def __str__(self):
        return str(self._traverse_dict(self.__dict__))

    def sort(self, comparator):
        self.messages.sort(key=functools.cmp_to_key(comparator))
