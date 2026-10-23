"""Misc utilities"""

from collections.abc import Callable, Iterable
from typing import TypeVar

E = TypeVar('E')  # Element

from boltons.iterutils import first


def foremost[E](
    iterable: Iterable[E],
    default: E | None = None,
    key: Callable[[E], bool] = lambda x: x is not None,
) -> E | None:
    """Return first non-*None* element from an iterable or *default*.

    *foremost* is a specialized version of :func:`boltons.iterutils.first`,
    with its *key* parameter defaulting to a predicate for non-*None* instead
    of *True*.

    This is especially useful with py2neo, because an entity without properties
    evaluates to *False*, whereas we usually just want the first non-*None*
    item from a result.

    :param Iterable iterable: Iterable to work on.
    :param default: Default if all elements of *iterable* are *None*. Default is *None*.
    :param Callable[[E], bool]: Predicate to determine the element of iterable should be selected.
    :return: First non-None element of Iterable.
    """
    return first(iterable, default=default, key=key)
