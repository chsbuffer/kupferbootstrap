from __future__ import annotations

import toml

from dataclasses import dataclass
from munch import Munch
from toml.encoder import TomlEncoder, TomlPreserveInlineDictEncoder
from typing import ClassVar, Generator, Optional, Union, Mapping, Any, get_type_hints, get_origin, get_args, Iterable
from types import UnionType, NoneType


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


def flatten_hints(hints: Any) -> Generator[Any, None, None]:
    if not isinstance(hints, (list, tuple)):
        yield hints
        return
    for i in hints:
        yield from flatten_hints(i)


def resolve_dict_hints(hints: Any) -> Generator[tuple[Any, ...], None, None]:
    for hint in flatten_hints(hints):
        t_origin = get_origin(hint)
        t_args = get_args(hint)
        if t_origin == dict:
            print(f"Yielding {t_args=}")
            yield t_args
            continue
        if t_origin in [NoneType, Optional, Union, UnionType] and t_args:
            yield from resolve_dict_hints(t_args)
        continue


class DataClass(Munch):

    _type_hints: ClassVar[dict[str, Any]]
    _strip_hidden: ClassVar[bool] = False
    _sparse: ClassVar[bool] = False

    def __init__(self, d: Mapping = {}, validate: bool = True, **kwargs):
        self.update(d | kwargs, validate=validate)

    @classmethod
    def transform(cls, values: Mapping[str, Any], validate: bool = True, allow_extra: bool = False, type_hints: Optional[dict[str, Any]] = None) -> Any:
        results = {}
        values = dict(values)
        print(f"\ntransform function:\n{values}, {type_hints=}")
        for key in list(values.keys()):
            value = values.pop(key)
            type_hints = cls._type_hints if type_hints is None else type_hints
            if key in type_hints:
                _classes = tuple[type](resolve_type_hint(type_hints[key]))
                optional = NoneType in _classes
                if issubclass(_classes[0], dict):
                    assert isinstance(value, dict) or optional
                    target_class = _classes[0]
                    if target_class in [None, NoneType, Optional]:
                        for target in _classes[1:]:
                            if target not in [None, NoneType, Optional]:
                                target_class = target
                                break
                    if target_class is dict:
                        dict_hints = list(resolve_dict_hints(type_hints[key]))
                        print(f"Got {key=} {dict_hints=}")
                        if len(dict_hints) != 1:
                            print(f"Received wrong amount of type hints for key {key}: {len(dict_hints)}")
                        if len(dict_hints) == 1 and value is not None:
                            if len(dict_hints[0]) != 2 or not all(dict_hints[0]):
                                print(f"Weird dict hints received: {dict_hints}")
                                continue
                            key_type, value_type = dict_hints[0]
                            if not isinstance(value, Mapping):
                                if validate:
                                    raise Exception(f"Got non-mapping {value!r} for expected dict type: {key_type} => {value_type}. Allowed classes: {_classes}")
                                print(f"Got non-mapping {value!r} for expected dict type: {key_type} => {value_type}. Allowed classes: {_classes}")
                                results[key] = value
                                continue
                            if isinstance(key_type, type):
                                if issubclass(key_type, str):
                                    target_class = Munch
                                else:
                                    print(f"{key=} DICT WRONG KEY TYPE: {key_type}")
                                if validate:
                                    for k in value:
                                        if not isinstance(k, tuple(flatten_hints(key_type))):
                                            raise Exception(f'Subdict "{key}": wrong type for subkey "{k}": got: {type(k)}, expected: {key_type}')
                            dict_content_hints = {k: value_type for k in value}
                            print(f"tranforming: {value=} {dict_content_hints=}")
                            value = cls.transform(value, validate=validate, allow_extra=allow_extra, type_hints=dict_content_hints)
                            print(f"tranformed: {value=}")
                    if not isinstance(value, target_class):
                        if not (optional and value is None):
                            assert issubclass(target_class, Munch)
                            # despite the above assert, mypy doesn't seem to understand target_class is a Munch here
                            kwargs = {'validate': validate} if issubclass(target_class, DataClass) else {}
                            value = target_class(value, **kwargs)  # type:ignore[attr-defined]
                    else:
                        print(f"nothing to do: '{key}' was already {target_class}")
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
                import logging
                logging.debug(f"{cls}: unknown key '{key}': {value}")
                raise Exception(f'{cls}: Unknown key "{key}"')
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
        return self.strip_dict(
            self,
            strip_hidden=strip_hidden,
            sparse=sparse,
            recursive=True,
        )

    @classmethod
    def strip_dict(
        cls,
        d: dict[Any, Any],
        strip_hidden: Optional[bool] = None,
        sparse: Optional[bool] = None,
        recursive: bool = True,
        hints: Optional[dict[str, Any]] = None,
    ) -> dict[Any, Any]:
        # preserve original None-type args
        _sparse = cls._sparse if sparse is None else sparse
        _strip_hidden = cls._strip_hidden if strip_hidden is None else strip_hidden
        hints = cls._type_hints if hints is None else hints
        result = dict(d)
        if not (_strip_hidden or _sparse or result):
            print(f"shortcircuiting {d=}")
            return result
        print(f"Stripping {result} with hints: {hints}")
        for k, v in d.items():
            type_hint = resolve_type_hint(hints.get(k, "abc"))
            print(f"Working on key {k}, type hints: {type_hint}")
            if not isinstance(k, str):
                print(f"skipping unknown key type {k=}")
                continue
            if strip_hidden and k.startswith('_'):
                result.pop(k)
                continue
            if v is None:
                if NoneType not in type_hint:
                    msg = f'encountered illegal null value at key "{k}" for typehint {type_hint}'
                    if True:
                        raise Exception(msg)
                    print(msg)
                if _sparse:
                    print(f"popping empty {k}")
                    result.pop(k)
                    continue
                print(f"encountered legal null value at {k}: {_sparse=}")
            if recursive and isinstance(v, dict):
                if not v:
                    result[k] = {}
                    continue
                if isinstance(v, DataClass):
                    print(f"Dataclass detected in {k=}")
                    result[k] = v.toDict(strip_hidden=strip_hidden, sparse=sparse)  # pass None in sparse and strip_hidden
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
                subclass = DataClass
                for hint in hints_flat:
                    print(f"working on hint: {hint}")
                    if get_origin(hint) == dict:
                        _valtype = get_args(hint)[1]
                        _subhints = {n: _valtype for n in v.keys()}
                        print(f"generated {_subhints=} from {_valtype=}")
                        break
                    if isinstance(hint, type) and issubclass(hint, DataClass):
                        subclass = hint
                        _subhints = hint._type_hints
                        print(f"found subhints: {_subhints}")
                        break
                    else:
                        print(f"ignoring {hint=}")
                print(f"STRIPPING SUBDICT {k=} WITH {_subhints=}")
                result[k] = subclass.strip_dict(
                    v,
                    hints=_subhints,
                    sparse=_sparse,
                    strip_hidden=_strip_hidden,
                    recursive=recursive,
                )
        return result

    def update(self, d: Mapping[str, Any], validate: bool = True):
        Munch.update(self, type(self).transform(d, validate))

    def __init_subclass__(cls):
        super().__init_subclass__()
        cls._type_hints = {name: hint for name, hint in get_type_hints(cls).items() if get_origin(hint) is not ClassVar}

    def __repr__(self):
        return f'{type(self)}{dict.__repr__(dict(self))}'

    def toYAML(
        self,
        strip_hidden: Optional[bool] = None,
        sparse: Optional[bool] = None,
        **yaml_args
    ) -> str:
        import yaml
        yaml_args = {'sort_keys': False} | yaml_args
        return yaml.dump(
            self.toDict(strip_hidden=strip_hidden, sparse=sparse),
            **yaml_args,
        )

    def toToml(
        self,
        strip_hidden: Optional[bool] = None,
        sparse: Optional[bool] = None,
        encoder: Optional[TomlEncoder] = TomlPreserveInlineDictEncoder()
    ) -> str:
        return toml.dumps(
            self.toDict(strip_hidden=strip_hidden, sparse=sparse),
            encoder=encoder,
        )


class TomlInlineDict(dict, toml.decoder.InlineTableDict):
    pass


def toml_inline_dicts(value: Any) -> Any:
    if not isinstance(value, Mapping):
        return value
    return TomlInlineDict({k: toml_inline_dicts(v) for k, v in value.items()})
