from serializable import Serializable
import time


class EventBase(Serializable):
    """Base class for all events definition"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.eventType = self.event_type()
        self.mark_begin_timestamp()
        self.endTimestamp = self.beginTimestamp

    def event_type(self):
        return self.__class__.__name__

    def mark_begin_timestamp(self):
        self.beginTimestamp = time.time()

    def mark_end_timestamp(self):
        self.endTimestamp = time.time()

    def to_dict(self):
        return self._traverse_dict(self.__dict__)

    def serialize(self):
        self._validate_serializable()
        return super().serialize()

    def _validate_serializable(self):
        assert hasattr(self, 'eventType')
        assert hasattr(self, 'beginTimestamp')
        assert hasattr(self, 'endTimestamp')

        if self.beginTimestamp > self.endTimestamp:
            raise ValueError("Invalid timestamps. begin: {}, end: {}"
                             .format(self.beginTimestamp, self.endTimestamp))
