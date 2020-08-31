from functools import lru_cache
import re as python_re


__all__ = ['Re', 'Match', 'Search', 'Group', 'G']


class ReBinder:
    def __init__(self, kind, re):
        self._kind = kind
        self._re = re

    def __eq__(self, other):
        if not isinstance(other, str):
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


@lru_cache(maxsize=None)
def _re_compile(pattern):
    return python_re.compile(pattern)


def _build_matcher(name, kind):
    class MetaMatcher(type):
        __match_args__ = (
            f"_rematch_bind_{kind}",
            *(f"_rematch_item_{k}" for k in range(1, 1000))
        )

        def __instancecheck__(self, instance):
            return super().__instancecheck__(instance) or isinstance(instance, Re)

        def __call__(self, *a, **kw):
            raise TypeError("You don't want to do that")
    MetaMatcher.__name__ = f"{name}Type"

    class Matcher(metaclass=MetaMatcher):
        pass
    Matcher.__name__ = name

    return Matcher


Match = _build_matcher('Match', 'match')
Search = _build_matcher('Search', 'search')
FullMatch = _build_matcher('FullMatch', 'fullmatch')


def _build_sub(name, kind):
    class MetaMatcher(type):
        __match_args__ = (
            f"_rematch_bind_{kind}",
            "_rematch_repl_",
            *("_rematch_sub_result_" for _ in range(1, 1000))
        )

        def __instancecheck__(self, instance):
            return super().__instancecheck__(instance) or isinstance(instance, Re)

    MetaMatcher.__name__ = f"{name}Type"
    MetaMatcher.__qualname__ = f"{__name__}.{MetaMatcher.__name__}"

    class Matcher(metaclass=MetaMatcher):
        pass

    Matcher.__name__ = name
    Matcher.__qualname__ = f"{__name__}.{Matcher.__name__}"

    return Matcher


Sub = _build_sub('Sub', 'sub')


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
