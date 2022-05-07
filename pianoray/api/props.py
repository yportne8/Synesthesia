import os
from typing import Any, Iterable, List, Optional, Tuple, Type

import numpy as np

from .keyframe import Keyframe, Interp
from .interpolate import interpolate

__all__ = (
    "Property",
    "BoolProp",
    "IntProp",
    "FloatProp",
    "StrProp",
    "PathProp",
    "ArrayProp",
    "RGBProp",
)


class Property:
    """
    Property base class.
    """
    type: Type
    supported_interps: Iterable[str]

    name: str
    desc: str
    animatable: bool
    default: Any

    _keyframes: List[Keyframe]
    _value: Any

    def __init__(self, name: str, desc: str, default: Any,
            animatable: bool = True) -> None:
        self.name = name
        self.desc = desc
        self.default = self.type(default)
        self.animatable = animatable

        self._keyframes = []
        self._value = self.default

        if self.default is not None:
            assert self.verify(self.default)

    def set_value(self, value: Any):
        """
        Checks validity and sets self._value
        """
        assert self.verify(value)
        self._value = value

    def animate(self, keyframe: Keyframe) -> None:
        assert self.animatable
        assert keyframe.interp in self.supported_interps
        keyframe.value = self.type(keyframe.value)
        assert self.verify(keyframe.value)
        self._keyframes.append(keyframe)

    def verify(self, value: Any) -> bool:
        """
        Check whether the value can be assigned to this prop, e.g.
        min and max.

        Default implementation returns True.
        Override in subclass, if applicable.
        """
        return True

    def _get_value(self, frame: int) -> Any:
        """
        Returns the value, but not necessarily the correct type.
        Call ``self.value(frame)`` instead to convert to the prop's type.
        """
        keys = sorted(self._keyframes)

        if len(keys) == 0:
            return self._value

        elif len(keys) == 1:
            return keys[0].value

        else:
            if frame <= keys[0].frame:
                return keys[0].value
            elif frame >= keys[-1].frame:
                return keys[-1].value
            else:
                for i, k in enumerate(keys):
                    if k.frame == frame:
                        return k.value
                    if k.frame > frame:
                        break

                k1 = keys[i-1]
                k2 = keys[i]
                return interpolate(k1, k2, frame)

    def value(self, frame: int) -> Any:
        """
        Returns value at frame. Uses keyframe interpolations.

        Equivalent to ``self.type(self._get_value(frame))``
        """
        return self.type(self._get_value(frame))


class BoolProp(Property):
    """
    Boolean.
    """
    type = bool
    supported_interps = {Interp.CONSTANT}


class IntProp(Property):
    """
    Integer.
    Min and max inclusive.
    Coords: Whether this quantity is in coords.
    """
    type = int
    supported_interps = {Interp.CONSTANT, Interp.LINEAR}

    min: int
    max: int
    coords: bool

    def __init__(self, min: Optional[int] = None, max: Optional[int] = None,
            coords: bool = False, **kwargs) -> None:
        self.min = min
        self.max = max
        super().__init__(**kwargs)

    def verify(self, value: int) -> bool:
        """
        Checks min and max.
        """
        if self.min is not None and value < self.min:
            return False
        if self.max is not None and value > self.min:
            return False
        return True


class FloatProp(Property):
    """
    Float.
    Min and max inclusive.
    Coords: Whether this quantity is in coords.
    """
    type = float
    supported_interps = {Interp.CONSTANT, Interp.LINEAR}

    min: int
    max: int
    coords: bool

    def __init__(self, min: Optional[int] = None, max: Optional[int] = None,
            coords: bool = False, **kwargs) -> None:
        self.min = min
        self.max = max
        super().__init__(**kwargs)

    def verify(self, value: int) -> bool:
        """
        Checks min and max.
        """
        if self.min is not None and value < self.min:
            return False
        if self.max is not None and value > self.min:
            return False
        return True


class StrProp(Property):
    """
    String.
    Min and max inclusive.
    """
    type = str
    supported_interps = {Interp.CONSTANT}

    min: int
    max: int

    def __init__(self, min_len: Optional[int] = None, max_len: Optional[int] = None,
            **kwargs) -> None:
        self.min_len = min_len
        self.max_len = max_len
        super().__init__(**kwargs)

    def verify(self, value: str) -> bool:
        """
        Checks length min and max.
        """
        if self.min_len is not None and value < self.min_len:
            return False
        if self.max_len is not None and value > self.min_len:
            return False
        return True


class PathProp(StrProp):
    """
    Path property.
    Can verify if a path exists.
    """

    def __init__(self, isfile: bool = False, isdir: bool = False, **kwargs):
        """
        Initialize the property.

        :param isfile: Path must be a file.
        :param isdir: Path must be a directory.
        """
        self.min_len = min_len
        self.max_len = max_len
        super().__init__(**kwargs)

    def verify(self, value: str) -> bool:
        """
        Checks path isfile and isdir, if respective attributes are True.
        """
        if not super().verify(value):
            return False

        if self.isfile and not os.path.isfile(value):
            return False
        if self.isdir and not os.path.isdir(value):
            return False

        return True


class ArrayProp(Property):
    """
    Numpy array property.
    """
    type = np.array
    supported_interps = {Interp.CONSTANT, Interp.LINEAR}

    shape: Optional[Tuple[int]]

    def __init__(self, shape: Optional[Tuple[int]] = None, **kwargs) -> None:
        self.shape = shape
        super().__init__(**kwargs)

    def verify(self, value: np.ndarray) -> bool:
        """
        Checks shape.
        """
        if self.shape is not None and value.shape != self.shape:
            return False
        return True


class RGBProp(ArrayProp):
    """
    RGB color property, 0 to 255.
    """
    shape = (3,)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


if __name__ == "__main__":
    b1 = BoolProp(name="asdf", desc="desc", default=False, animatable=False)
    b2 = BoolProp(name="asdf", desc="desc", default=False, animatable=True)

    try:
        b1.animate(Keyframe(0, False, Interp.CONSTANT))
    except AssertionError as e:
        print("Cannot animate b1:", e)

    print(b2.value(0))
    b2.animate(Keyframe(0, True, Interp.CONSTANT))
    print(b2.value(0), b2.value(1))
    b2.animate(Keyframe(5, False, Interp.CONSTANT))
    print(b2.value(-1), b2.value(0), b2.value(2), b2.value(5), b2.value(6))

    i = IntProp(name="asdf", desc="desc", default=10, animatable=True)
    print(i.value(0))
    i.animate(Keyframe(0, 5, Interp.LINEAR))
    print(i.value(0))
    i.animate(Keyframe(5, 10, Interp.CONSTANT))
    i.animate(Keyframe(10, 15, Interp.CONSTANT))
    print([i.value(a) for a in range(0, 6)])
    print([i.value(a) for a in range(5, 11)])
