# FixedInt


Custom implementation of fixed-size integer classes in Python.

A nice learning exercise on bit manipulation as well as a refresher on more advanced Python topics such as operator overloading, function closures, and the class factory and singleton design patterns.


## Setup


This package was written for Python versions 3.8+.

Create and activate a virtual environment for the project directory. Then, you can install the package in **editable mode**:

```sh
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

> **NOTE:** This project uses [`pyproject.toml`](pyproject.toml) for metadata and setup instead of the legacy `setup.py` approach. If the installation fails, you probably have an outdated version of pip:
>
>   ```sh
>   python -m pip install --upgrade pip
>   ```


## Usage


Import the `FixedInt` class factory and call it to create classes representing integers with specific bit widths.

```python
from fixedint import FixedInt, FixedSignedInt, FixedUnsignedInt

# Create FixedIntTypes.
UInt12 = FixedInt(12, signed=False)
Int8 = FixedSignedInt(8)
UInt8 = FixedUnsignedInt(8)

# Create instances of the FixedIntTypes.
foo = UInt8(5)
bar = Int8(200)  # Handles overflow
print(foo, bar)  # 5 -56
```


## Features


Easily get the zero-padded, Two's complement binary representation:

```python
>>> FixedSignedInt(8)(101).as_binary()
'01100101'
>>> FixedSignedInt(8)(-45).as_binary()
'11010011'
```

Supports operations between instances:

```python
>>> num1 = UInt8(25)
>>> num2 = UInt8(7)
>>> print(num1 + num2)
32
```

Supports operations between other `FixedIntType`s. The returned type is the type of the first operand:

```python
>>> num3 = UInt8(100)
>>> num4 = FixedSignedInt(12)(2040)
>>> num3 - num4  # Overflows
FixedInt(size=8, signed=False)(108)
>>> num4 - num3
FixedInt(size=12, signed=True)(1_940)
```

Supports operations with the built-in `int`. The returned type is the type of the first operand:

```python
>>> Int8(5) * 8
FixedInt(size=8, signed=True)(40)
>>> 8 * Int8(5)
40
>>> type(_)
<class 'int'>
```

Polymorphic inheritance checking:

```python
>>> from fixedint import FixedIntType, FixedSignedInt
>>> num1 = FixedSignedInt(10)(25)
>>> num2 = FixedSignedInt(10)(40)
>>> type(num1) is type(num2)
True
>>> isinstance(num1, FixedSignedInt(10))
True
>>> isinstance(num1, FixedIntType)
True
>>> isinstance(num1, int)
True
```

All types created by the `FixedInt()` and its factory wrapper functions are **interned** within the `FixedIntType` parent class. This class can be imported for use as a type hint but also doubles as a singleton manager. All numbers with the same (size, signed) properties are guaranteed to share the same class object in memory.


## Testing


I've included a unit test script to sanity check the behavior of `FixedIntType` instances and how they interact with each other and with the built-in `int`:

```sh
cd test
python -m unittest
```

`FixedIntType` itself subclasses the built-in `int`, allowing it to be treated as one almost anywhere a normal `int` would. Obviously, this practice is always a double-edged sword because my custom type might also break some internals of the normal `int`, causing strange bugs.


## Disclaimer


This was an afternoon hobby project by an undergraduate student with too much free time. I do not claim it to be safe or reliable for use in production-level projects.
