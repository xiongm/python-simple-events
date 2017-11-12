import json


klass_registry = {}


def register_klass(klass):
    klass_registry[klass.__name__] = klass



def deserialize(serialized):
    data = json.loads(serialized)
    if 'klass' not in data:
        raise ValueError("klass info not found")
    name = data['klass']
    if name not in klass_registry:
        raise ValueError("Unregistered class {}. Not serializable".format(name))
    target_class = klass_registry[name]
    return target_class.deserialize(serialized)


def _deserialize_i(data):
    args = data.get('args', [])
    kwargs = data.get('kwargs', {})

    # remove meta when deserializing
    name = data.pop('klass', None)

    obj = None
    try:
        if name:
            target_class = klass_registry[name]
            obj = target_class(*args, **kwargs)
    except TypeError as e:
        raise type(e)(str(e) + '\nThis usually indicates there are'  \
                      ' constructor parameters that shoud be passed to super __init__')

    for k, v in data.items():
        if isinstance(v, dict) and 'klass' in v:
            v_data, v_obj = _deserialize_i(v)
            v_obj.__dict__ = v_data
            data[k] = v_obj
        elif isinstance(v, list):
            result = []
            for i in v:
                if isinstance(i, dict) and 'klass' in i:
                    v_data, v_obj = _deserialize_i(i)
                    v_obj.__dict__ = v_data
                    result.append(v_obj)
                else:
                    result.append(i)
            data[k] = result
    return data, obj


class RegistryMeta(type):
    def __new__(meta, name, bases, class_dict):
        cls = type.__new__(meta, name, bases, class_dict)
        register_klass(cls)
        return cls


class Serializable(metaclass=RegistryMeta):
    def __init__(self, *args, **kwargs):
        self.args = list(args)
        self.kwargs = kwargs

    def type(self):
        return self.__class__.__name__

    def _traverse_dict(self, instance_dict):
        result = {}
        for k, v in instance_dict.items():
            result[k] = self._traverse(k, v)
        return result

    def _traverse(self, k, v):
        if isinstance(v, Serializable):
            result = self._traverse_dict(v.__dict__)
            result['klass'] = v.__class__.__name__
            return result
        if isinstance(v, dict):
            return self._traverse_dict(v)
        elif isinstance(v, list):
            return [self._traverse(k, i) for i in v]
        elif isinstance(v, (set, tuple)):
            """
            set is not serializable to json, thus we don't allow it
            tuple is translated to list in json dumps, so there's no
            guarantee to deserlize it back to list, thus we explicitly
            forbids it
            """
            raise TypeError("{} Not serializable: {}".format(type(v), v))
        elif hasattr(v, "__dict__"):
            return self._traverse_dict(v.__dict__)
        else:
            return v


    def serialize(self):
        result = self._traverse_dict(self.__dict__)
        result['klass'] = self.__class__.__name__
        return json.dumps(result)

    def __repr__(self):
        return repr(self.__dict__)

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, rhs):
        return self.__dict__ == rhs.__dict__

    @classmethod
    def deserialize(cls, serialized):
        data = json.loads(serialized)
        data, obj = _deserialize_i(data)
        obj.__dict__ = data
        return obj
