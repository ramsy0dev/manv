# ManV

ManV (Manipulate Variable) is a modern language and runtime initiative focused on high-performance computing, machine learning workloads, and direct GPU-oriented execution.

It is designed to feel approachable while still exposing a serious compiler architecture for low-level control and future backend expansion.

## Why ManV

- Built for ML and GPU-heavy workloads from day one.
- Hybrid runtime model: fast interpreter iteration with a compiler pipeline for optimization.
- Multi-stage IR architecture that keeps semantics explicit and debuggable.
- Cross-platform toolchain and project workflow.
- Standard library strategy centered on language-authored source backed by internal intrinsics.

## Architecture Value

ManV uses a structured lowering pipeline:

`AST -> HLIR -> Graph IR -> Kernel IR -> backend boundary`

This gives ManV clear separation between:

- Language semantics
- Optimization and graph transformations
- Kernel formation
- Backend-specific code generation and dispatch

The result is a foundation that is easier to validate, test, and scale across CPU and GPU targets.

## Execution Model

ManV currently prioritizes semantic consistency:

- Interpreter mode for fast feedback loops and debugging.
- Compiled mode that remains HLIR-authoritative for parity in v1.
- Kernelization paths with safe fallback when regions are not eligible.

## Tooling

CLI surface:

- `manv init [path] [--std]`
- `manv run [file|project]`
- `manv compile [file|project]`
- `manv build [file|project]`
- `manv repl`
- `manv test [path]`
- `manv dap --transport stdio|tcp [--host 127.0.0.1 --port 4711]`
- `manv lsp --transport stdio|tcp [--host 127.0.0.1 --port 2087]`

Package and registry operations:

- `manv auth login`
- `manv auth status`
- `manv auth logout`
- `manv add <name[@version]>`
- `manv add <git-url>`

Build artifacts are emitted to `.manv/target` by default.

## Standard Library Direction

ManV is moving to a pure language-authored standard library model.

- `__intrin.*` provides the internal compiler/runtime bridge.
- Intrinsics are validated by semantic analysis and lowered through HLIR.
- Runtime behavior stays consistent between interpreter and compiled execution.
- Module imports support absolute and package-relative forms (`import a.b`, `from .x import y`, `from ..pkg import z`).
- Module resolution order is deterministic: project source root, then `MANV_PATH`, then bundled std source.
- `manv init <path> --std` scaffolds the compiler-shipped ManV `std` source.
- `syscall(...)` is available as both statement and expression form.
- `std` includes typed syscall wrappers: `std_syscall_posix(...)` and `std_syscall_windows(...)`.

## No-Foreign-Runtime Policy

ManV enforces a strict migration policy for standard library purity:

- No new stdlib modules may delegate subsystem behavior to host-language stdlib packages.
- No new broad subsystem intrinsics are allowed (for example: JSON/HTTP/regex parsers as intrinsics).
- CI includes monotonic policy gates that block newly introduced violations while existing baseline debt is removed incrementally.

Example:

```manv
fn main() -> int:
    let r = syscall("getpid")
    print(r["ok"])
    return 0
```

## Object-Oriented Programming

ManV supports a complete OOP model with Python-style operator overloading.

### Dunder protocol

Instances can implement dunder methods (and their short-form aliases) to customize language behavior:

| Dunder | Alias | Triggered by |
|---|---|---|
| `__init__` | `init` | `TypeName(args)` construction |
| `__repr__` | `repr_` | `str(obj)` / `repr(obj)` fallback |
| `__str__` | `str_` | `str(obj)` |
| `__bool__` | `bool_` | `bool(obj)`, truthiness checks |
| `__len__` | `len_` | `len(obj)` |
| `__hash__` | `hash_` | `hash(obj)` |
| `__eq__` | `eq` | `==` / `!=` |
| `__lt__` | `lt` | `<` |
| `__le__` | `le` | `<=` |
| `__gt__` | `gt` | `>` |
| `__ge__` | `ge` | `>=` |
| `__add__` | `add` | `+`, `+=` |
| `__sub__` | `sub` | `-`, `-=` |
| `__mul__` | `mul` | `*`, `*=` |
| `__truediv__` | `truediv` | `/`, `/=` |
| `__mod__` | `mod` | `%`, `%=` |
| `__pow__` | `pow` | `**`, `**=` |
| `__neg__` | `neg` | unary `-` |
| `__contains__` | `contains` | `x in obj` (right-side dispatch) |
| `__getitem__` | `getitem` | `obj[key]` |
| `__setitem__` | `setitem` | `obj[key] = val` |
| `__call__` | `call_` | `obj(args)` |
| `__iter__` | `iter_` | `for x in obj:` |
| `__next__` | `next_` | iteration step (raise `StopIteration` to stop) |
| `__enter__` | — | `with obj as x:` entry |
| `__exit__` | — | `with` exit; returning truthy suppresses exceptions |

### Multiple inheritance with C3 MRO

```manv
type A(Base1, Base2):
    fn greet(self) -> str:
        return "hello from A"
```

ManV resolves method lookup using C3 linearization, matching Python's MRO order.

### super()

```manv
type Animal:
    fn __init__(self, name):
        self.name = name

type Dog(Animal):
    fn __init__(self, name, breed):
        super().__init__(name)
        self.breed = breed
```

`super()` finds the enclosing class in the MRO and returns a proxy that walks to the next class.

### @classmethod

```manv
type Point:
    fn __init__(self, x, y):
        self.x = x
        self.y = y

    @classmethod
    fn from_tuple(cls, t) -> Point:
        return cls(t[0], t[1])
```

Classmethods receive the `TypeObject` as their first argument instead of an instance.

### Context managers

`with` statements call `__enter__` on entry and `__exit__(self, exc_type, exc_val, exc_tb)` on exit. If `__exit__` returns a truthy value the exception is suppressed.

```manv
type Timer:
    fn __enter__(self):
        self.start = 0
        return self
    fn __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        return false   # do not suppress exceptions
```

### Iteration protocol

Any object with `__iter__` and `__next__` works in `for` loops:

```manv
type CountDown:
    fn __init__(self, n):
        self.n = n
    fn __iter__(self) -> CountDown:
        return self
    fn __next__(self) -> int:
        if self.n <= 0:
            raise StopIteration("done")
        self.n = self.n - 1
        return self.n + 1

fn main() -> int:
    for i in CountDown(3):
        print(i)     # 3 2 1
    return 0
```

## Current Status

ManV is an active v1 foundation phase with emphasis on:

- Semantic correctness
- Deterministic diagnostics and testing
- Debugger integration (DAP)
- Language tooling integration (LSP via pygls)
- Backend extensibility for future native GPU execution

Debug adapter design details are documented in `DEBUGGING.md`.
