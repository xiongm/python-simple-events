import unittest
from event_base import EventBase
from serializable import deserialize
import time


class TestEventBase(unittest.TestCase):

    def test_event_type(self):
        class MyEventType(EventBase):
            def __init__(self, c):
                super().__init__(c)
                self.c = c

        event = MyEventType('c')
        event.mark_begin_timestamp()
        event.mark_end_timestamp()
        serialized = event.serialize()
        obj = deserialize(serialized)

        self.assertEqual(obj.event_type(), 'MyEventType')
        self.assertTrue(isinstance(obj, MyEventType))
        self.assertEqual(event, obj)

    def test_to_dict(self):
        class MyEventType(EventBase):
            def __init__(self, a, b, c, d):
                super().__init__(a, b, c, d)
                self.eventType = self.event_type()
                self.a = a
                self.b = b
                self.c = c
                self.d = d

        event = MyEventType(a='a', c=['a', 'b'], d={'a': 'b'}, b='b')
        event.mark_begin_timestamp()
        event.mark_end_timestamp()

        expected = {
            'args': ['a', 'b', ['a', 'b'], {'a': 'b'}],
            'kwargs': {},
            'beginTimestamp': event.beginTimestamp,
            'endTimestamp': event.endTimestamp,
            'eventType': 'MyEventType',
            'a': 'a',
            'b': 'b',
            'c': ['a', 'b'],
            'd': {'a': 'b'}
        }
        serialized = event.serialize()
        obj = MyEventType.deserialize(serialized)
        self.assertEqual(sorted(obj.to_dict().items()), sorted(expected.items()))
        self.assertEqual(obj, event)

        class MyEventType(EventBase):
            def __init__(self, a, b, c, d):
                super().__init__(a=a, b=b, c=c, d=d)
                self.eventType = self.event_type()
                self.a = a
                self.b = b
                self.c = c
                self.d = d

        event = MyEventType(a='a', c=['a', 'b'], d={'a': 'b'}, b='b')
        event.mark_begin_timestamp()
        event.mark_end_timestamp()

        expected = {
            'args': [],
            'kwargs': {'a': 'a', 'b': 'b', 'c': ['a', 'b'], 'd': {'a': 'b'}},
            'beginTimestamp': event.beginTimestamp,
            'endTimestamp': event.endTimestamp,
            'eventType': 'MyEventType',
            'a': 'a',
            'b': 'b',
            'c': ['a', 'b'],
            'd': {'a': 'b'}
        }
        serialized = event.serialize()
        obj = MyEventType.deserialize(serialized)
        self.assertEqual(sorted(obj.to_dict().items()), sorted(expected.items()))
        self.assertEqual(obj, event)

    def test_super_not_called(self):
        class MyEventType(EventBase):
            def __init__(self, a, b, c, d):
                self.eventType = self.event_type()
                self.beginTimestamp = 0
                self.endTimestamp = 0
                self.a = a
                self.b = b
                self.c = c
                self.d = d

        event = MyEventType('a', 'b', ['a', 'b'], {'a': 'b'})

        serialized = event.serialize()
        # fail to call super in constructor when it should
        self.assertRaises(TypeError, MyEventType.deserialize, serialized)

        class MyEventType(EventBase):
            def __init__(self, a, b, c, d):
                self.a = a
                self.b = b
                self.c = c
                self.d = d

        event = MyEventType('a', 'b', ['a', 'b'], {'a': 'b'})

        self.assertRaises(AssertionError, event.serialize)

    def test_mark_timestamp(self):
        # timestamp marked incorrectly
        class MyEventType(EventBase):
            def __init__(self, c):
                super().__init__(c)
                self.c = c

        event = MyEventType('c')
        event.mark_end_timestamp()
        time.sleep(0.01)
        event.mark_begin_timestamp()
        self.assertRaises(ValueError, event.serialize)


if __name__ == "__main__":
    unittest.main()
