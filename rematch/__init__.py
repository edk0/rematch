from functools import lru_cache
import re as python_re


class ReBinder:
    def __init__(self, kind, re):
        self._kind = kind
        self._re = re

    def __eq__(self, other):
        if not isinstance(other, str):
            raise TypeError
        return self._re._bind(self._kind, other)


class ReGroup:
    def __init__(self, re, group):
        self._re = re
        self._group = group

    def __eq__(self, other):
        raise TypeError

    @property
    def _rematch_group_value_(self):
        return self._re._rematch_match_.group(self._group)


class GroupType(type):
    __match_args__ = '_rematch_group_value_',

    def __instancecheck__(self, instance):
        return isinstance(instance, ReGroup)


class Group(metaclass=GroupType):
    pass

G = Group


@lru_cache(maxsize=None)
def _re_compile(pattern):
    return python_re.compile(pattern)


class MatchType(type):
    __match_args__ = (
        '_rematch_bind_match_',
        *(f"_rematch_item_{k}" for k in range(1, 1000))
    )

    def __instancecheck__(self, instance):
        return super().__instancecheck__(instance) or isinstance(instance, Re)


class Match(metaclass=MatchType):
    pass


class SearchType(type):
    __match_args__ = (
        '_rematch_bind_search_',
        *(f"_rematch_item_{k}" for k in range(1, 1000))
    )

    def __instancecheck__(self, instance):
        return super().__instancecheck__(instance) or isinstance(instance, Re)


class Search(metaclass=MatchType):
    pass


class Re:
    def __init__(self, s):
        self._s = s
        self._rematch_match_ = None

    @property
    def _rematch_bind_match_(self):
        return ReBinder('match', self)

    def _bind(self, kind, pattern):
        if kind == 'match':
            m = _re_compile(pattern).match(self._s)
        elif kind == 'search':
            m = _re_compile(pattern).search(self._s)
        elif kind == 'fullmatch':
            m = _re_compile(pattern).fullmatch(self._s)
        else:
            assert False
        if not m:
            return False
        self._rematch_match_ = m
        return True

    def __getattr__(self, k):
        if k.startswith('_rematch_item_'):
            k = int(k.removeprefix('_rematch_item_'))
        return ReGroup(self, k)
