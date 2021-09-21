# rematch

A hack to use [PEP 634][pep-634] to match regexps:

```pycon
>>> from rematch import Re, Match, Group
>>> match Re("hello edk"):
...   case Match(r"hello (.*)", Group(whom)):
...     print(f"Greetings, {whom}!")
...   case Match(r"goodbye (.*)", Group(whom)):
...     print(f"Sorry to see you go, {whom}!")
...
Greetings, edk!
```

`Sub` is also available, with sed-ish "match if there were any substitutions"
semantics:

```pycon
>>> from rematch import Re, Sub, Text
>>> match Re("hello edk"):
...   case Sub(r"hello", "goodbye", Text(s)):
...     print(s)
...
goodbye edk
```

You can also save the number of substitutions in `n` with `Num(n)`.

[pep-634]: https://www.python.org/dev/peps/pep-0634/
