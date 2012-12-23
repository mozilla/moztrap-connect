from json import loads
from datetime import datetime
import requests

class _Fixture(object):

    _edit_args = []
    _create_args = [_edit_args, ]
    _filter_args = []

    @classmethod
    def _verify_args(cls, actual_args, allowed_args, method):
        for arg in actual_args.keys():
            if not arg in allowed_args:
                raise Exception("%s not an allowed arguement for %s.%s." % (
                    arg, cls.__name__, method))

    def __init__(self, connect, fields={}, _data=None):
        '''Instance constructor. Use the API to create a object.

        ::Args::
        connect - an mtconnect.connect.Connect object
        fields - a dictionary of field names and values

        Also used internally to create Fixtures out of data from list methods.
        '''
        cls = self.__class__
        self.connect = connect
        if _data:
            # create object for existing record
            self.__dict__.update(_data)
        else:
            self._verify_args(fields, self._create_args, '__init__')
            r = connect.do_post(self._uri, fields)
            self.id = r.headers['location'].split('/')[-2]
            self.get()

    def __repr__(self):
        '''Instance method. String representation of fixture.'''
        return "%s with attributes %s" % (self.__class__.__name__, str(self.__dict__))

    def get(self):
        '''Instance method. Refresh the object with data from the server.'''
        r = self.connect.do_get(self._uri, self.id)
        data = loads(r.text)
        self.__dict__.update(data)

    def edit(self, fields):
        '''Instance method. Use the API to edit the object.

        ::Args::
        fields - dictionary of field names and values

        '''
        self._verify_args(fields, self._edit_args, 'edit')
        self.connect.do_put(self._uri, self.id, fields)
        self.__dict__.update(fields)

    def delete(self, permanent=False):
        '''Instance method. Use the API to delete the object.
        ::Args::
        permanent - True/False, defaults to False
        '''
        self.connect.do_delete(self._uri, self.id, params={"permanent": permanent})

    @classmethod
    def list(cls, connect, **filters):
        '''Class method. Query the API for existing object.

        ::Args::
        connect - an mtconnect.connect.Connect object.

        ::Keyword Args (filters)::

        ::Returns::
        A potentially empty list of _Fixture objects will be returned.
        '''
        cls._verify_args(filters, cls._filter_args, 'find')

        r = connect.do_get(cls._uri, params=filters)
        objects = loads(r.text)["objects"]

        return [cls(connect, _data=obj) for obj in objects]


class ProductFixture(_Fixture):
    _uri = 'product'
    _edit_args = ['description']
    _create_args = _edit_args + ['name', 'productversions']
    _filter_args = ['name']


class SuiteFixture(_Fixture):
    _uri = 'suite'
    _edit_args = ['description', 'status', 'name', 'product']
    _create_args = _edit_args
    _filter_args = ['name', 'product']


class ProductVersionFixture(_Fixture):
    _uri = 'productversion'
    _edit_args = ['version', 'codename']
    _create_args = _edit_args + ['product']
    _filter_args = ['version', 'product']
