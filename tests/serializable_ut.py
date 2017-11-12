import unittest
from serializable import Serializable, deserialize
import json


class TestSerializable(unittest.TestCase):

    def test_default_constructed(self):
        class TestMessage(Serializable):
            def __init__(self):
                self.a = 'a'
                self.b = 'b'
                self.c = 10
                self.d = 20.0

        test = TestMessage()
        serialized = test.serialize()
        self.assertEqual(TestMessage.deserialize(serialized), test)

        class TestMessage(Serializable):
            def __init__(self):
                self.a = 'a'
                self.b = 'b'
                self.c = ['a', 'b']
        test = TestMessage()
        serialized = test.serialize()
        self.assertEqual(TestMessage.deserialize(serialized), test)

        class TestMessage(Serializable):
            def __init__(self):
                self.a = 'a'
                self.b = 'b'
                self.c = ('a', 'b')
        test = TestMessage()
        # serialization of tuple not supported
        self.assertRaises(TypeError, test.serialize)

        class TestMessage(Serializable):
            def __init__(self):
                self.a = 'a'
                self.b = 'b'
                self.c = set(['a', 'b'])
        test = TestMessage()
        # serialization of set not supported
        self.assertRaises(TypeError, test.serialize)

        class TestMessage(Serializable):
            def __init__(self):
                self.a = 'a'
                self.b = 'b'
                self.c = {'a': 'b'}
        test = TestMessage()
        serialized = test.serialize()
        self.assertEqual(TestMessage.deserialize(serialized), test)

        class TestMessage(Serializable):
            def __init__(self):
                self.a = 'a'
                self.b = None
        test = TestMessage()
        serialized = test.serialize()
        self.assertEqual(TestMessage.deserialize(serialized), test)

    def test_default_constructed_and_mutated(self):
        class TestMessage(Serializable):
            def __init__(self):
                self.a = 'a'
                self.b = 'b'
                self.c = 10
                self.d = 20.0

        test = TestMessage()
        test.c = 20

        serialized = test.serialize()
        self.assertEqual(TestMessage.deserialize(serialized), test)

        class TestMessage(Serializable):
            def __init__(self):
                self.a = 'a'
                self.b = 'b'
                self.c = {'a': 'b'}
                self.d = 'd'

        test = TestMessage()
        test.c['a'] = 'c'
        test.d = None

        serialized = test.serialize()
        self.assertEqual(TestMessage.deserialize(serialized), test)

    def test_parameter_constructed(self):
        class TestMessage(Serializable):
            def __init__(self, a, b, c, d):
                super().__init__(a, b, c, d)
                self.a = a
                self.b = b
                self.c = c
                self.d = d

        test = TestMessage('a', 'b', ['a', 'b'], {'a': 'b'})

        serialized = test.serialize()
        self.assertEqual(TestMessage.deserialize(serialized), test)

        class TestMessage(Serializable):
            def __init__(self, a, b, c, d):
                super().__init__(a, b, c, d)
                self.a = a
                self.b = b
                self.c = c
                self.d = d

        test = TestMessage(a='a', c=['a', 'b'], d={'a': 'b'}, b='b')

        expected = {
            'args': ['a', 'b', ['a', 'b'], {'a': 'b'}],
            'kwargs': {},
            'a': 'a',
            'b': 'b',
            'c': ['a', 'b'],
            'd': {'a': 'b'}
        }
        serialized = test.serialize()
        obj = TestMessage.deserialize(serialized)
        self.assertEqual(sorted(obj._traverse_dict(obj.__dict__).items()), sorted(expected.items()))
        self.assertEqual(obj, test)

        class TestMessage(Serializable):
            def __init__(self, a, b, c, d):
                super().__init__(a=a, b=b, c=c, d=d)
                self.a = a
                self.b = b
                self.c = c
                self.d = d

        test = TestMessage(a='a', c=['a', 'b'], d={'a': 'b'}, b='b')

        expected = {
            'args': [],
            'kwargs': {'a': 'a', 'b': 'b', 'c': ['a', 'b'], 'd': {'a': 'b'}},
            'a': 'a',
            'b': 'b',
            'c': ['a', 'b'],
            'd': {'a': 'b'}
        }
        serialized = test.serialize()
        obj = TestMessage.deserialize(serialized)
        self.assertEqual(sorted(obj._traverse_dict(obj.__dict__).items()), sorted(expected.items()))
        self.assertEqual(obj, test)

    def test_none(self):
        class TestMessage(Serializable):
            def __init__(self, a=None, b=None):
                self.a = a
                self.b = b
        test = TestMessage(a='a')
        self.assertTrue(test.b is None)
        obj = deserialize(test.serialize())
        self.assertEqual(test, obj)
        self.assertTrue(obj.b is None)

    def test_super_not_called(self):
        class TestMessage(Serializable):
            def __init__(self, a, b, c, d):
                self.a = a
                self.b = b
                self.c = c
                self.d = d

        test = TestMessage('a', 'b', ['a', 'b'], {'a': 'b'})
        serialized = test.serialize()
        # fail to call super in constructor when it should
        self.assertRaises(TypeError, TestMessage.deserialize, serialized)

    def test_generic_deserialize(self):
        class TestMessage1(Serializable):
            def __init__(self, a, b):
                super().__init__(a, b)
                self.a = a
                self.b = b

        class TestMessage2(Serializable):
            def __init__(self, c, d):
                super().__init__(c, d)
                self.c = c
                self.d = d

        msg1 = TestMessage1('a', 'b')
        msg2 = TestMessage2('c', 'd')

        serialized1 = msg1.serialize()
        serialized2 = msg2.serialize()

        obj1 = deserialize(serialized1)
        obj2 = deserialize(serialized2)

        self.assertTrue(isinstance(obj1, TestMessage1))
        self.assertTrue(isinstance(obj2, TestMessage2))

        self.assertEqual(obj1.a, msg1.a)
        self.assertEqual(obj2.c, msg2.c)

        bad_data = {'klass': 'UNKNOWN'}
        self.assertRaises(ValueError, deserialize, json.dumps(bad_data))

    def test_nested_deserialize(self):
        class Child(Serializable):
            def __init__(self, c):
                super().__init__(c)
                self.c = c

        class Parent(Serializable):
            def __init__(self, p, child):
                super().__init__(p, child)
                self.p = p
                self.child = child

        child = Child('c')
        parent = Parent('p', child)

        self.assertTrue(isinstance(parent.child, Child))
        serialized = parent.serialize()

        obj = deserialize(serialized)
        self.assertTrue(isinstance(obj, Parent))

        self.assertTrue(isinstance(obj.child, Child))
        self.assertEqual(obj.child.c, parent.child.c)

        del Child
        del Parent

        # child is not serializable
        class Child:
            def __init__(self, c):
                self.c = c

        class Parent(Serializable):
            def __init__(self, p, child):
                super().__init__(p, child)
                self.p = p
                self.child = child

        child = Child('c')
        parent = Parent('p', child)

        self.assertTrue(isinstance(parent.child, Child))
        serialized = parent.serialize()

        obj = deserialize(serialized)
        self.assertTrue(isinstance(obj, Parent))

        # not serilizable
        self.assertFalse(isinstance(obj.child, Child))

    def test_type(self):
        class Child(Serializable):
            def __init__(self, c):
                super().__init__(c)
                self.c = c

        class Parent(Serializable):
            def __init__(self, p, child):
                super().__init__(p, child)
                self.p = p
                self.child = child

        child = Child('c')
        parent = Parent('p', child)
        serialized = parent.serialize()
        obj = deserialize(serialized)

        self.assertEqual(obj.type(), 'Parent')
        self.assertEqual(obj.child.type(), 'Child')

    def test_complext_object_deserialize(self):
        import time

        class State(Serializable):
            def __init__(self, state, timestamp):
                super().__init__(state, timestamp)
                self.state = state
                self.timestamp = timestamp

        class Query(Serializable):
            def __init__(self, query):
                super().__init__(query)
                self.query = query
                self.states = []
                self.set_state('NEW')

            def set_state(self, new_state):
                self.states.append(State(new_state, time.time()))

        query = Query('a query')

        serialized = query.serialize()

        obj = deserialize(serialized)

        self.assertTrue(isinstance(obj, Query))
        self.assertEqual(query.states[-1].state, 'NEW')

        self.assertTrue(isinstance(obj.states[-1], State))
        self.assertEqual(query.states[-1].state, obj.states[-1].state)

    def test_real_complex_object_deserialize(self):
        class Child(Serializable):
            def __init__(self, c):
                super().__init__(c)
                self.c = c

        class Parent(Serializable):
            def __init__(self, p, leader):
                super().__init__(p, leader)
                self.p = p
                self.leader = leader
                self.followers = []

            def add_follower(self, follower):
                self.followers.append(follower)

        class Parent2(Serializable):
            def __init__(self, p):
                super().__init__(p)
                self.p = p

        parent = Parent('p', Child('l'))
        parent.add_follower(Child('f1'))
        parent2 = Parent2(parent)

        serialized = parent2.serialize()
        obj = deserialize(serialized)

        self.assertTrue(isinstance(obj, Parent2))
        self.assertTrue(isinstance(obj.p, Parent))
        self.assertTrue(isinstance(obj.p.leader, Child))
        self.assertTrue(isinstance(obj.p.followers[-1], Child))
        self.assertEqual(obj, parent2)


if __name__ == "__main__":
    unittest.main()
