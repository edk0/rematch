# rematch

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
