import itertools
from collections import defaultdict
from collections.abc import Sequence, Set, Iterator
from typing import Any, Dict, Iterable, List, Tuple, Type, TypeVar, Union, cast

KT = TypeVar("KT")
VT = TypeVar("VT")


def dict_to_flatdict(
    dct: Dict[KT, Union[Any, Dict[KT, Any]]], _parent: Tuple[KT, ...] = None
) -> Dict[Tuple[KT, ...], Any]:
    """Converts a (nested) dictionary to a flattened representation.

    Each key of the flat dict will be a CompoundKey tuple containing the "chain of keys"
    for the corresponding value.

    Args:
        - dct (dict): The dictionary to flatten
        - _parent (Tuple, optional): The current parent for recursion

    Returns:
        - A flattened dict of the same type as dct
    """
    typ = cast(Type[Dict[Tuple[KT, ...], Any]], type(dct))
    items: List[Tuple[Tuple[KT, ...], Any]] = []
    parent = _parent or tuple()

    for k, v in dct.items():
        k_parent = tuple(parent + (k,))
        if isinstance(v, dict):
            items.extend(dict_to_flatdict(v, _parent=k_parent).items())
        else:
            items.append((k_parent, v))
    return typ(items)


def flatdict_to_dict(
    dct: Dict[Tuple[KT, ...], VT]
) -> Dict[KT, Union[VT, Dict[KT, VT]]]:
    """Converts a flattened dictionary back to a nested dictionary.

    Args:
        - dct (dict): The dictionary to be nested. Each key should be a tuple of keys
            as generated by `dict_to_flatdict`

    Returns
        - A nested dict of the same type as dct
    """
    typ = type(dct)
    result = cast(Dict[KT, Union[VT, Dict[KT, VT]]], typ())
    for key_tuple, value in dct.items():
        current_dict = result
        for prefix_key in key_tuple[:-1]:
            # Build nested dictionaries up for the current key tuple
            # Use `setdefault` in case the nested dict has already been created
            current_dict = current_dict.setdefault(prefix_key, typ())  # type: ignore
        # Set the value
        current_dict[key_tuple[-1]] = value

    return result


T = TypeVar("T")


def ensure_iterable(obj: Union[T, Iterable[T]]) -> Iterable[T]:
    if isinstance(obj, Sequence) or isinstance(obj, Set):
        return obj
    obj = cast(T, obj)  # No longer in the iterable case
    return [obj]


def listrepr(objs: Iterable, sep=" ") -> str:
    return sep.join(repr(obj) for obj in objs)


def extract_instances(
    objects: Iterable,
    types: Union[Type[T], Tuple[Type[T], ...]] = object,
) -> Union[List[T], Dict[Type[T], T]]:
    """
    Extract objects from a file and returns a dict of type -> instances

    Args:
        - objects: An iterable of objects
        - types: A type or tuple of types to extract, defaults to all objects

    Returns:
        - If a single type is given: a list of instances of that type
        - If a tuple of types is given: a mapping of type to a list of instances
    """
    types = ensure_iterable(types)

    # Create a mapping of type -> instance from the exec values
    ret = defaultdict(list)

    for o in objects:
        # We iterate here so that the key is the passed type rather than type(o)
        for type_ in types:
            if isinstance(o, type_):
                ret[type_].append(o)

    if len(types) == 1:
        return ret[types[0]]

    return ret


def batched_iterable(iterable: Iterable[T], size: int) -> Iterator[T]:
    """
    Yield batches of a certain size from an iterable

    Args:
        - iterable (Iterable): An iterable
        - size (int): The batch size to return

    Yields:
        tuple: A batch of the iterable
    """
    it = iter(iterable)
    while True:
        batch = tuple(itertools.islice(it, size))
        if not batch:
            break
        yield batch
