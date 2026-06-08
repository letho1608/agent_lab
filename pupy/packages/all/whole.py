# -*- coding: utf-8 -*-


import sys


def to_string(x):
    if isinstance(x, (list, tuple, set, frozenset)):
        return [to_string(y) for y in x]
    elif isinstance(x, str):
        return x
    elif x is None:
        return ''
    elif isinstance(x, dict):
        return {
            to_string(k):to_string(v) for k,v in x.items()
        }
    else:
        return str(x)


def to_strings_list(function, *args, **kwargs):
    results = []
    raise_on_exception = kwargs.pop('raise_on_exception', True)

    iterator = function(*args, **kwargs)

    while True:
        try:
            result = next(iterator)
            results.append(to_string(result))

        except StopIteration:
            break

        except:
            if raise_on_exception:
                raise

    return results
