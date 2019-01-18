"""
This module provides a convenient dict subclass that is capable of
transforming dicts in many ways.  Most operations have "immutable-like"
behaviour, returning new dict instances rather than modifying the original
dict.
"""
from __future__ import absolute_import, division

import itertools
import operator
from collections import defaultdict
from functools import partial
from inspect import isfunction
from operator import itemgetter

from six import iteritems, string_types

from .vendored.more_itertools import unique_everseen


def dottedgetter(keypath):
    steps = keypath.split('.')

    def _getter(value):
        for step in steps:
            if not isinstance(value, dict):
                raise TypeError('Expected a dict, got: {!r}'.format(value))
            value = value[step]
        return value

    return _getter


def walk_nested(iterable_of_kvpairs, max_depth=None, currpath=None):
    if currpath is None:
        currpath = tuple()

    for k, v in iterable_of_kvpairs:
        keypath = currpath + (k,)
        if isinstance(v, dict) and (max_depth is None or max_depth > 0):
            # Recurse
            for k2, v2 in walk_nested(iteritems(v),
                                      max_depth=max_depth - 1 if max_depth else None,
                                      currpath=keypath):
                yield (k2, v2)
        else:
            # Simply return
            yield (keypath, v)


class LazyVector(object):
    """
    Helper object that allows for more efficient chained Vector
    implementations.  It really is a class to help manipulating (key, value)
    pair streams.

    This avoids the need for materialization of all the intermediate dicts in
    the process.  Also, these methods return the current LazyVector instance
    for easy chaining.

    The data only gets materialized when it's iterated over.
    """
    def __init__(self, iterable):
        self.iterable = iter(iterable)

    @staticmethod
    def _set(iterable, new_key, new_value):
        for k, v in iterable:
            if k != new_key:
                yield (k, v)
        yield (new_key, new_value)

    def set(self, new_key, new_value):
        self.iterable = self._set(self.iterable, new_key, new_value)
        return self

    def unset(self, key):
        self.iterable = ((k, v) for k, v in self.iterable if k != key)
        return self

    def mapkv(self, mapper):
        self.iterable = (mapper(k, v) for k, v in self.iterable)
        return self

    def mapk(self, mapper):
        self.iterable = ((mapper(k), v) for k, v in self.iterable)
        return self

    def mapv(self, mapper):
        self.iterable = ((k, mapper(v)) for k, v in self.iterable)
        return self

    @staticmethod
    def _remap(iterable, mapping):
        mappers = {
            k: dottedgetter(v)
            for k, v in iteritems(mapping)
        }

        doc = dict(iterable)
        for k, getter in iteritems(mappers):
            yield (k, getter(doc))

    def remap(self, mapping):
        self.iterable = self._remap(self.iterable, mapping)
        return self

    def rename(self, old_key, new_key):
        self.iterable = ((new_key if k == old_key else k, v)
                         for k, v in self.iterable)
        return self

    def select(self, keys_or_pred):
        if isinstance(keys_or_pred, string_types):
            keys_or_pred = (keys_or_pred,)

        if isfunction(keys_or_pred):
            pred = keys_or_pred
        else:
            keys = set(keys_or_pred)
            pred = keys.__contains__
        self.iterable = ((k, v) for k, v in self.iterable if pred(k))
        return self

    def walk_nested(self, max_depth=None):
        self.iterable = walk_nested(self.iterable, max_depth=max_depth)
        return self

    def unnest(self, sep='.', key=None, max_depth=None):
        if key is None:
            key = partial(sep.join)

        self.iterable = ((key(keypath), v) for keypath, v in self.walk_nested(max_depth))
        return self

    def drop_keys(self, keys_or_pred):
        if isinstance(keys_or_pred, string_types):
            keys_or_pred = (keys_or_pred,)

        if isfunction(keys_or_pred):
            pred = keys_or_pred
        else:
            keys = set(keys_or_pred)
            pred = keys.__contains__
        self.iterable = ((k, v) for k, v in self.iterable if not pred(k))
        return self

    def compact(self):
        self.iterable = ((k, v) for k, v in self.iterable if v)
        return self

    def merge(self, *dicts, **kwargs):
        all_dicts = [iteritems(kwargs)]
        all_dicts += [iteritems(d) for d in dicts]
        all_dicts += [self.iterable]
        self.iterable = unique_everseen(itertools.chain(*all_dicts),
                                        key=itemgetter(0))
        return self

    def __iter__(self):
        return self.iterable

    def to_vector(self):
        return Vector(self)


class Vector(dict):
    """
    This class is a dict subclass which allows us to treat regular Python
    dictionaries as Vectors, and also adds a bunch of useful (class)methods to
    work with dicts.  For example, this makes it really expressive to compute
    sums, means, and other statistical computations.

        >>> v = Vector(x=3, y=4)
        >>> v
        {'x': 3, 'y': 4}

        >>> v + v   # easy summing
        {'x': 6, 'y': 8}

        >>> v / 3   # easy math
        {'x': 1.0, 'y': 1.33333333}

        >>> sum([v, v, v])   # works with all Python functions
        {'x': 9, 'y': 12}

    Also, adds some convenience methods, like for making subselections, build
    lookup tables, transform values, etc.

        >>> v = Vector({'x': 1, 'y': 2, 'z': 3, 'bananas': 4})
        >>> v.select(['x', 'z'])  # takes a bunch of keys
        {'x': 1, 'z': 3}

        >>> v.select(lambda k: k != 'bananas')  # can also take a function
        {'x': 1, 'y': 2, 'z': 3}

        >>> Vector.index_by(range(10), key=lambda x: x % 2 == 0)
        {True: [0, 2, 4, 6, 8], False: [1, 3, 5, 7, 9]}

        >>> v.mapv(lambda value: value + 10)
        {'x': 11, 'y': 12, 'z': 13, 'bananas': 14}

    All of the methods on this class (excluding the ones inherited from dict)
    are immutable, meaning they return new Vectors.
    """

    def chain(self):
        """
        Start a lazy Vector manipulation chain.
        """
        return LazyVector(iteritems(self))

    def set(self, key, value):
        """
        Adds a new (key, value) pair to the Vector, returning a new Vector
        instance.
        """
        return self.chain().set(key, value).to_vector()

    def unset(self, key):
        """
        Returns a new Vector with the given key removed (if such key exists).
        If no such `key` exists, the new Vector will effectively be equal to
        the original.
        """
        return self.chain().unset(key).to_vector()

    def mapk(self, func):
        """
        Returns a new Vector with the same values, but where all the keys are
        transformed by applying the given function to each key.
        `func` should be a function that takes the key as the only argument.

        NOTE: If a key is emitted multiple times, it's undefined which one
        will "win" when materialized to the final dict.
        """
        return self.chain().mapk(func).to_vector()

    def mapv(self, func):
        """
        Returns a new Vector with the same keys, but where all the values are
        transformed by applying the given function to all values.
        `func` should be a function that takes the value as the only argument.
        """
        return self.chain().mapv(func).to_vector()

    def mapkv(self, func):
        """
        Returns a new Vector by applying the given function to each (k, v)
        pair.  `func` should be a function that takes the key and the value,
        and returns a new (k, v) tuple.

        NOTE: If a key is emitted multiple times, it's undefined which one
        will "win" when materialized to the final dict.
        """
        return self.chain().mapkv(func).to_vector()

    @classmethod
    def group_by(cls, iterable, key=None, keyval=None):
        """
        Builds up a lookup table, grouping the values from the iterable by the
        result of applying `key` to each item.

        For example:

        >>> Vector.group_by(['foo', 'bar', 'baz', 'qux', 'quux'],
        ...                 key=lambda s: s[0])
        {
            'b': ['bar', 'baz'],
            'f': ['foo'],
            'q': ['quux', 'qux']
        }

        For extra power, you can even change the values while building up the LUT.
        To do so, use the `keyval` function instead of the `key` arg:

        >>> Vector.group_by(['foo', 'bar', 'baz', 'qux', 'quux'],
        ...                 keyval=lambda s: (s[0], s[1:].upper()))
        {
            'b': ['AR', 'AZ'],
            'f': ['OO'],
            'q': ['UX', 'UUX']
        }

        """
        if keyval is None:
            if key is None:
                raise ValueError('Expected either a `key` or `keyval` argument')
            else:
                if isinstance(key, string_types):
                    key = itemgetter(key)
                keyval = lambda v: (key(v), v)

        lut = {}
        for value in iterable:
            print(value)
            k, v = keyval(value)
            try:
                s = lut[k]
            except KeyError:
                s = lut[k] = list()
            s.append(v)
        return cls(lut)

    @classmethod
    def index_by(cls, iterable, key=None, keyval=None):
        """
        Much like .group_by(), but will only store one item for each key,
        building up a unique index.

        >>> Vector.index_by(['foo', 'bar', 'baz', 'qux', 'quux'],
        ...                 lambda s: s[0],
        ...                 unique=True)
        {
            'b': 'baz',
            'f': 'foo',
            'q': 'quux'
        }

        """
        if keyval is None:
            if key is None:
                raise ValueError('Expected either a `key` or `keyval` argument')
            else:
                if isinstance(key, string_types):
                    key = itemgetter(key)
                keyval = lambda v: (key(v), v)

        return cls(keyval(v) for v in iterable)

    def merge(self, *dicts, **kwargs):
        """
        Returns a new Vector but with all the given dict's keys merged in.
        Example to show the priority each key gets:

            >>> v = Vector(a=1).merge({'a': 2, 'b': 2},
            ...                       {'a': 3, 'c': 3},
            ...                       a=4, d=4)
            >>> v
            {'a': 4, 'b': 2, 'c': 3, 'd': 4}

        In other words, the merged keys that show up in the final dictionary
        take priority as if they are merged in one by one into the original
        dict, left-to-right, and finally the kwargs are merged in.
        """
        return self.chain().merge(*dicts, **kwargs).to_vector()

    def remap(self, mapping):
        """
        Returns a new Vector where all keys in the mapping are present.  The
        values from the mapping define the dotted source paths for where to
        find the data in the original document.  Example:

            >>> doc = {
            ...     '_id': 1,
            ...     'info': {
            ...         'first_name': 'Vincent',
            ...         'last_name': 'Driessen',
            ...     },
            ...     'city': 'Deventer',
            ... }
            >>> doc.remap({'id': '_id', 'name': 'info.first_name'})
            {'id': 1, 'name': 'Vincent'}

        """
        return self.chain().remap(mapping).to_vector()

    def rename(self, old_key, new_key):
        """
        Renames a single key in the Vector.  The values are unaffected.  If
        the new name already exists, the behaviour is undefined.

            >>> v = Vector({
            ...     'foo': 123,
            ...     'bar': 456,
            ... })
            >>> v.rename('foo', 'qux')
            {'qux': 123, 'bar': 456}

        """
        return self.chain().rename(old_key, new_key).to_vector()

    def select(self, keys_or_pred):
        """
        Returns a new Vector dropping all key-value pairs except for the keys
        specified.
        """
        return self.chain().select(keys_or_pred).to_vector()

    def drop_keys(self, keys_or_pred):
        """
        Returns a new Vector dropping the specified keys.  Keys can be
        a single key, a list of keys, or an iterable.
        """
        return self.chain().drop_keys(keys_or_pred).to_vector()

    def compact(self):
        """
        Returns a new Vector dropping all (k, v) pairs where the value v is
        falsey.
        """
        return self.chain().compact().to_vector()

    def reindex(self):
        """
        Reindexes a nested dictionary of the form

            {A: {B: C}}

        to the form

            {B: {A: C}}

        TODO: this can be optimized by making it lazy/chainable
        """
        outputs = defaultdict(self.__class__)
        for k1, nested_doc in iteritems(self):
            for k2, v in iteritems(nested_doc):
                outputs[k2][k1] = nested_doc[k2]
        return self.__class__(outputs)

    def walk_nested(self, max_depth=None):
        """
        Walks a vector/dict structure recursively, returning a lazy iterable
        of all (keypath, value) combinations.  The `max_depth` option can be
        used to limit the recursion.
        """
        return self.chain().walk_nested(max_depth=max_depth)

    def unnest(self, sep='.', key=None, max_depth=None):
        """
        When unnest() is invoked without params, it just "flattens" any nested
        dicts, using the dotted keys paths as the new keys.
        """
        return self.chain().unnest(sep=sep, key=key, max_depth=max_depth).to_vector()

    def __neg__(self):
        return self.mapv(operator.__neg__)

    def __pos__(self):
        return self.mapv(operator.__pos__)

    @staticmethod
    def make_op(operator, operand, default=0):
        if isinstance(operand, dict):
            def transformer(k, v):
                return k, operator(v, operand.get(k, default))
            return transformer

        def transformer(k, v):
            return k, operator(v, operand)
        return transformer

    def __add__(self, other):
        op = self.make_op(operator.__add__, other)
        return self.chain().mapkv(op).to_vector()

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        op = self.make_op(operator.__sub__, other)
        return self.chain().mapkv(op).to_vector()

    def __rsub__(self, other):
        return other + -self

    def __mul__(self, other):
        op = self.make_op(operator.__mul__, other, default=1)
        return self.chain().mapkv(op).to_vector()

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        op = self.make_op(operator.__truediv__, other, default=1)
        return self.chain().mapkv(op).to_vector()

    def __rtruediv__(self, other):
        inv = self.mapv(lambda v: 1 / v)
        return inv * other
