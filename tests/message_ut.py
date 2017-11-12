import unittest
from event_base import EventBase
from message import Message, MessageBatch
from serializable import deserialize
import time


class TestMessage(unittest.TestCase):

    def test_basic(self):

        class Event1(EventBase):
            pass

        class Event2(EventBase):
            pass

        msg = Message()
        msg.push_event(Event1())
        msg.push_event(Event2())

        self.assertEqual(2, msg.count())
        self.assertTrue(isinstance(msg.last_event(), Event2))

        msg = Message().push_event(Event1()).push_event(Event2())
        self.assertEqual(2, msg.count())
        self.assertTrue(isinstance(msg.last_event(), Event2))

    def test_non_event_base_not_allowed(self):

        class Event1(EventBase):
            pass

        class Event2:
            pass

        msg = Message()
        msg.push_event(Event1())
        self.assertRaises(TypeError, msg.push_event, Event2())

    def test_item_getter(self):
        class Event1(EventBase):
            pass

        class Event2(EventBase):
            pass

        class Event3(EventBase):
            pass

        msg = Message()
        msg.push_event(Event1())
        msg.push_event(Event2())

        self.assertTrue(Event1 in msg)
        self.assertTrue(Event2 in msg)
        self.assertFalse(Event3 in msg)

        obj = msg.get_event(Event1)
        self.assertTrue(type(obj) == Event1)
        obj = msg.get_event(Event2)
        self.assertTrue(type(obj) == Event2)
        obj = msg.get_event(Event3)
        self.assertEqual(obj, None)

        self.assertTrue('Event1' in msg)
        self.assertTrue('Event2' in msg)
        self.assertFalse('Event3' in msg)

        obj = msg.get_event('Event1')
        self.assertTrue(type(obj) == Event1)
        obj = msg.get_event('Event2')
        self.assertTrue(type(obj) == Event2)
        obj = msg.get_event('Event3')
        self.assertEqual(obj, None)

    def test_deserialize(self):
        class Event1(EventBase):
            pass

        class Event2(EventBase):
            pass

        msg = Message()
        msg.push_event(Event1())
        msg.push_event(Event2())

        serialized = msg.serialize()
        obj = deserialize(serialized)
        self.assertTrue(isinstance(obj, Message))
        instance_dict = obj._traverse_dict(obj.__dict__)
        self.assertEqual('Event2', instance_dict['events'][-1]['eventType'])
        self.assertEqual(msg, obj)

    def test_deserialize_with_missing_field(self):
        class Event1(EventBase):
            def __init__(self, fieldOne=None):
                super().__init__(fieldOne)
                self.fieldOne = fieldOne

        class Event2(EventBase):
            def __init__(self, fieldTwo=None):
                super().__init__(fieldTwo)
                self.fieldTwo = fieldTwo

        msg = Message()
        msg.push_event(Event1('one'))
        msg.push_event(Event2('two'))

        serialized = msg.serialize()

        print(serialized)
        mangled_serialized = serialized.replace('"fieldOne": "one"', '"bogus": "bogusness"')
        print(mangled_serialized)
        self.assertNotEqual(serialized, mangled_serialized)

        obj = deserialize(mangled_serialized)
        self.assertTrue(isinstance(obj, Message))
        instance_dict = obj._traverse_dict(obj.__dict__)
        self.assertEqual('Event2', instance_dict['events'][-1]['eventType'])

        self.assertNotEqual(msg, obj)
        obj.get_event(Event1).fieldOne = 'one'
        msg.get_event(Event1).bogus = 'bogusness'
        self.assertEqual(msg, obj)

    def test_events_validation(self):
        class Event1(EventBase):
            def __init__(self):
                pass

        class Event2(EventBase):
            pass

        msg = Message()
        msg.push_event(Event1())
        msg.push_event(Event2())

        # no eventType
        self.assertRaises(AssertionError, msg.serialize)

        msg = Message()
        event = Event2()
        event.mark_end_timestamp()
        time.sleep(0.1)
        event.mark_begin_timestamp()

        msg.push_event(event)

        self.assertRaises(ValueError, msg.serialize)

    def test_message_batch_deserialize(self):
        class Event1(EventBase):
            pass

        class Event2(EventBase):
            pass

        class Event3(EventBase):
            pass

        msg = Message()
        msg.push_event(Event1())
        msg.push_event(Event2())

        msg2 = Message()
        msg2.push_event(Event2())
        msg2.push_event(Event3())

        batch = MessageBatch()
        batch.push_back(msg)
        batch.push_back(msg2)

        self.assertEqual(2, len(batch))

        serialized = batch.serialize()
        obj = deserialize(serialized)
        self.assertTrue(isinstance(obj, MessageBatch))
        instance_dict = obj._traverse_dict(obj.__dict__)
        print (instance_dict)
        self.assertEqual('Event1', instance_dict['messages'][0]['events'][0]['eventType'])
        self.assertEqual('Event3', instance_dict['messages'][-1]['events'][-1]['eventType'])
        self.assertEqual(batch, obj)

if __name__ == "__main__":
    unittest.main()
