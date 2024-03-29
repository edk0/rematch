from functools import lru_cache
import re as python_re


__all__ = ['Re', 'Match', 'Search', 'FullMatch', 'Sub', 'Group', 'G', 'Text', 'Num', 'N']


class ReBinder:
    def __init__(self, kind, re):
        self._kind = kind
        self._re = re

    def __eq__(self, other):
        if not isinstance(other, (str, python_re.Pattern)):
            raise TypeError
        return self._re._bind(self._kind, other)


class ReplBinder:
    def __init__(self, re):
        self._re = re

    def __eq__(self, other):
        if not isinstance(other, str):
            raise TypeError
        return self._re._bind_repl(other)


class ReGroup:
    def __init__(self, re, group):
        self._re = re
        self._group = group

    def __eq__(self, other):
        raise TypeError

    @property
    def _rematch_group_value_(self):
        return self._re._rematch_match_.group(self._group)


class ReSub:
    def __init__(self, re):
        self._re = re

    def __eq__(self, other):
        raise TypeError

    @property
    def _rematch_sub_text_(self):
        return self._re._rematch_sub_[0]

    @property
    def _rematch_sub_n_(self):
        return self._re._rematch_sub_[1]


class GetterType(type):
    def __new__(metacls, name, bases, namespace, *, key, class_):
        cls = type.__new__(metacls, name, bases, namespace)
        cls.__match_args__ = key,
        cls._rematch_class_ = class_
        return cls

    def __instancecheck__(self, instance):
        return isinstance(instance, self._rematch_class_)

    def __call__(self, *a, **kw):
            raise TypeError("You don't want to do that")


class Group(metaclass=GetterType, key='_rematch_group_value_', class_=ReGroup):
    pass

G = Group


class Text(metaclass=GetterType, key='_rematch_sub_text_', class_=ReSub):
    pass


class Num(metaclass=GetterType, key='_rematch_sub_n_', class_=ReSub):
    pass

N = Num


@lru_cache(maxsize=None)
def _re_compile(pattern):
    if isinstance(pattern, python_re.Pattern):
        return pattern
    return python_re.compile(pattern)


class MatcherType(type):
    def __new__(metacls, name, bases, namespace, kind):
        cls = type.__new__(metacls, name, bases, namespace)
        if '__match_args__' not in namespace:
            cls.__match_args__ = (
                f"_rematch_bind_{kind}",
                *(f"_rematch_item_{k}" for k in range(1, 1000))
            )
        return cls

    def __instancecheck__(self, instance):
        return super().__instancecheck__(instance) or isinstance(instance, Re)

    def __call__(self, *a, **kw):
        raise TypeError("You don't want to do that")


class Match(metaclass=MatcherType, kind='match'):
    pass
class Search(metaclass=MatcherType, kind='search'):
    pass
class FullMatch(metaclass=MatcherType, kind='fullmatch'):
    pass


class Sub(metaclass=MatcherType, kind='sub'):
    __match_args__ = (
        f"_rematch_bind_sub",
        "_rematch_repl_",
        *("_rematch_sub_result_" for _ in range(2))
    )


class Re:
    def __init__(self, s):
        self._s = s
        self._rematch_match_ = None
        self._rematch_subre_ = None

    def _bind(self, kind, pattern):
        self._rematch_match_ = self._rematch_subre_ = None
        if kind == 'match':
            m = _re_compile(pattern).match(self._s)
        elif kind == 'search':
            m = _re_compile(pattern).search(self._s)
        elif kind == 'fullmatch':
            m = _re_compile(pattern).fullmatch(self._s)
        elif kind == 'sub':
            self._rematch_subre_ = _re_compile(pattern)
            return True
        else:
            assert False
        if not m:
            return False
        self._rematch_match_ = m
        return True

    def _bind_repl(self, repl):
        if self._rematch_subre_ is None:
            raise TypeError
        sub, n = self._rematch_sub_ = self._rematch_subre_.subn(repl, self._s)
        return n != 0

    @property
    def _rematch_repl_(self):
        return ReplBinder(self)

    @property
    def _rematch_sub_result_(self):
        return ReSub(self)

    def __getattr__(self, k):
        if k.startswith('_rematch_bind_'):
            kind = k.removeprefix('_rematch_bind_')
            return ReBinder(kind, self)
        if k.startswith('_rematch_item_'):
            k = int(k.removeprefix('_rematch_item_'))
        return ReGroup(self, k)
