from __future__ import annotations

from dataclasses import dataclass
from munch import Munch
from typing import ClassVar, Optional, Union, Mapping, Any, get_type_hints, get_origin, get_args, GenericAlias, Iterable
from types import UnionType

NoneType = type(None)


def munchclass(*args, init=False, **kwargs):
    return dataclass(*args, init=init, slots=True, **kwargs)


def resolve_type_hint(hint: type, ignore_origins: list[type] = []) -> Iterable[type]:
    origin = get_origin(hint)
    args: Iterable[type] = get_args(hint)
    if origin in ignore_origins:
        return [hint]
    if origin is Optional:
        args = set(list(args) + [NoneType])
    if origin in [Union, UnionType, Optional]:
        results: list[type] = []
        for arg in args:
            results += resolve_type_hint(arg, ignore_origins=ignore_origins)
        return results
    return [origin or hint]


class DataClass(Munch):

    _type_hints: ClassVar[dict[str, Any]]
    _strip_hidden: ClassVar[bool] = False
    _sparse: ClassVar[bool] = False

    def __init__(self, d: dict = {}, validate: bool = True, **kwargs):
        self.update(d | kwargs, validate=validate)

    @classmethod
    def transform(cls, values: Mapping[str, Any], validate: bool = True, allow_extra: bool = False) -> Any:
        results = {}
        values = dict(values)
        for key in list(values.keys()):
            value = values.pop(key)
            type_hints = cls._type_hints
            if key in type_hints:
                _classes = tuple[type](resolve_type_hint(type_hints[key]))
                optional = NoneType in _classes
                if issubclass(_classes[0], dict):
                    assert isinstance(value, dict) or optional
                    target_class = _classes[0]
                    if target_class is dict:
                        target_class = Munch
                    if not isinstance(value, target_class):
                        if not (optional and value is None):
                            assert issubclass(target_class, Munch)
                            # despite the above assert, mypy doesn't seem to understand target_class is a Munch here
                            kwargs = {'validate': validate} if issubclass(target_class, DataClass) else {}
                            value = target_class.fromDict(value, **kwargs)  # type:ignore[attr-defined]
                # handle numerics
                elif set(_classes).intersection([int, float]) and isinstance(value, str) and str not in _classes:
                    parsed_number = None
                    parsers: list[tuple[type, list]] = [(int, [10]), (int, [0]), (float, [])]
                    for _cls, args in parsers:
                        if _cls not in _classes:
                            continue
                        try:
                            parsed_number = _cls(value, *args)
                            break
                        except ValueError:
                            continue
                    if parsed_number is None:
                        if validate:
                            raise Exception(f"Couldn't parse string value {repr(value)} for key '{key}' into number formats: " +
                                            (', '.join(list(c.__name__ for c in _classes))))
                    else:
                        value = parsed_number
                if validate:
                    if not isinstance(value, _classes):
                        raise Exception(f'key "{key}" has value of wrong type! expected: '
                                        f'{" ,".join([ c.__name__ for c in _classes])}; '
                                        f'got: {type(value).__name__}; value: {value}')
            elif validate and not allow_extra:
                raise Exception(f'Unknown key "{key}"')
            else:
                if isinstance(value, dict) and not isinstance(value, Munch):
                    value = Munch.fromDict(value)
            results[key] = value
        if values:
            if validate:
                raise Exception(f'values contained unknown keys: {list(values.keys())}')
            results |= values

        return results

    @classmethod
    def fromDict(cls, values: Mapping[str, Any], validate: bool = True):
        return cls(d=values, validate=validate)

    def toDict(
        self,
        strip_hidden: Optional[bool] = None,
        sparse: Optional[bool] = None,
    ):
        return strip_dict(
            self,
            hints=self._type_hints,
            strip_hidden=self._strip_hidden if strip_hidden is None else strip_hidden,
            sparse=self._sparse if sparse is None else sparse,
            recursive=True,
        )

    def update(self, d: Mapping[str, Any], validate: bool = True):
        Munch.update(self, type(self).transform(d, validate))

    def __init_subclass__(cls):
        super().__init_subclass__()
        cls._type_hints = {name: hint for name, hint in get_type_hints(cls).items() if get_origin(hint) is not ClassVar}

    def __repr__(self):
        return f'{type(self)}{dict.__repr__(self.toDict())}'

    def toYaml(self, strip_hidden: bool = False, sparse: bool = False, **yaml_args) -> str:
        import yaml
        return yaml.dump(
            self.toDict(strip_hidden=strip_hidden, sparse=sparse),
            **yaml_args,
        )

    def toToml(self, strip_hidden: bool = False, sparse: bool = False, **toml_args) -> str:
        import toml
        return toml.dumps(
            self.toDict(strip_hidden=strip_hidden, sparse=sparse),
            **toml_args,
        )


def flatten_hints(hints: Any) -> list[Any]:
    if not isinstance(hints, (list, tuple)):
        yield hints
        return
    for i in hints:
        yield from flatten_hints(i)


def strip_dict(
    d: dict[Any, Any],
    hints: dict[str, Any],
    strip_hidden: bool = False,
    sparse: bool = False,
    recursive: bool = True,
) -> dict[Any, Any]:
    result = dict(d)
    if not (strip_hidden or sparse or result):
        print(f"shortcircuiting {d=}")
        return result
    print(f"Stripping {result} with hints: {hints}")
    for k, v in d.items():
        if not isinstance(k, str):
            print(f"skipping unknown key type {k=}")
            continue
        if strip_hidden and k.startswith('_'):
            result.pop(k)
            continue
        if sparse and (v is None and NoneType in resolve_type_hint(hints.get(k, "abc"))):
            print(f"popping empty {k}")
            result.pop(k)
            continue
        if recursive and isinstance(v, dict):
            if not v:
                result[k] = {}
                continue
            if isinstance(v, DataClass):
                print(f"Dataclass detected in {k=}")
                result[k] = v.toDict(strip_hidden=strip_hidden, sparse=sparse)
                continue
            if isinstance(v, Munch):
                print(f"Converting munch {k=}")
                result[k] = v.toDict()
            if k not in hints:
                print(f"skipping unknown {k=}")
                continue
            print(f"STRIPPING RECURSIVELY: {k}: {v}, parent hints: {hints[k]}")
            _subhints = {}
            _hints = resolve_type_hint(hints[k], [dict])
            hints_flat = list(flatten_hints(_hints))
            print(f"going over hints for {k}: {_hints=} {hints_flat=}")

            for hint in hints_flat:
                print(f"working on hint: {hint}")
                if get_origin(hint) == dict:
                    _valtype = get_args(hint)[1]
                    _subhints = {n: _valtype for n in v.keys()}
                    print(f"generated {_subhints=} from {_valtype=}")
                    break
                if isinstance(hint, type) and issubclass(hint, DataClass):
                    _subhints = hint._type_hints
                    print(f"found subhints: {_subhints}")
                    break
                else:
                    print(f"ignoring {hint=}")
            print(f"STRIPPING SUBDICT {k=} WITH {_subhints=}")
            result[k] = strip_dict(
                v,
                hints=_subhints,
                sparse=sparse,
                strip_hidden=strip_hidden,
                recursive=recursive,
            )
    return result
