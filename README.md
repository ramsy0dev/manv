# ManV

ManV (Manipulate Variable) is a programming language designed for high-performance computing, GPU-accelerated workloads, and machine learning pipelines. It combines a fast interpreter path for iterative development with a structured compilation pipeline for production-grade performance.

## Design Values

**Explicit semantics.** The compiler pipeline is structured to keep every transformation inspectable. The language does not hide what happens to data during execution. Operations that move, copy, or transform values are visible at the language surface and traceable through the IR stages.

**Hybrid execution.** A program can run in interpreter mode for fast feedback and in compiled mode for optimized, native execution. Both paths share the same semantic representation, so behavior does not diverge between development and production.

**GPU as a first-class target.** GPU execution is not an afterthought. The compilation pipeline is designed to identify eligible computation regions, lower them to kernel form, and dispatch them to the appropriate hardware backend — automatically, without requiring the programmer to manage device boundaries manually in the common case.

**Low-level control, high-level ergonomics.** ManV exposes pointer-like semantics, memory layout control, and backend-specific tuning when needed, but keeps the common case free of that complexity.

---

## Compilation Pipeline

ManV source lowers through four explicit stages before reaching a backend:

```
Source → AST → HLIR → Graph IR → Kernel IR → Backend
```

**AST** captures syntax and structure. It is the input to all downstream passes and is inspectable via `manv compile --emit ast`.

**HLIR** (High-Level Intermediate Representation) is the semantic authority of the compiler. It encodes execution semantics as an explicit control-flow graph: basic blocks, exception-handling edges, effect annotations on every instruction, and stable source provenance. Both the interpreter and the compiled path consume HLIR — this is what guarantees behavioral parity between the two execution modes. Inspectable via `manv compile --emit hlir`.

**Graph IR** restructures the HLIR control-flow graph into a data dependency graph. This form enables GPU region detection (identifying loop shapes that can be lifted to kernels), optimization passes, and CUDA graph planning. Inspectable via `manv compile --emit graph`.

**Kernel IR** is the final architecture-independent representation of a compute kernel. It encodes the kernel's parameter signature, per-thread operations, type information (bit widths, vector lanes), and memory class annotations (global, shared, local). It is the input to backend-specific emitters (PTX, SPIR-V, WGSL). Inspectable via `manv compile --emit kernel`.

Each stage has a defined input/output contract. Adding a new backend requires implementing a consumer of an existing IR stage — not a consumer of the source language.

---

## Execution Model

ManV supports two execution paths that share the same semantic definition at HLIR:

**Interpreter mode** evaluates HLIR directly. It is the default for `manv run` and the REPL. It supports the full language surface and integrates with the DAP debugger.

**Compiled mode** lowers HLIR through Graph IR and Kernel IR to native code or GPU kernels. The compiled path must produce the same observable behavior as the interpreter. Divergence is a compiler bug, not an intended design difference.

---

## CPU and GPU Execution

Functions execute on CPU by default. GPU execution is enabled explicitly at the function level via decoration, or inferred by the compiler for eligible computation regions within a CPU function.

GPU eligibility is determined by the Graph IR pass. Requirements: the computation must be a regular, bounded loop over a dataset; no I/O or unresolvable dynamic dispatch; memory accesses must target buffers that can be placed in device memory. Ineligible regions fall back to CPU execution silently.

When GPU execution is targeted, the compiler selects the hardware backend in priority order:

1. CUDA (NVIDIA)
2. AMD ROCm (HIP)
3. Intel oneAPI
4. Vulkan Compute
5. DirectX Compute
6. WebGPU

The programmer can override this selection explicitly. The fallback chain ensures code written for GPU execution runs correctly on any supported hardware without source changes.

---

## Memory Model

The current implementation provides automatic management for heap-allocated values in interpreter mode and explicit stack allocation for primitive values and fixed-size arrays. Deterministic GC controls are available via CLI flags for testing GC-sensitive behavior.

Planned additions, to be introduced incrementally:

- **Ownership and move semantics** — value transfer without copying; explicit lifetime at call boundaries.
- **Borrow semantics** — temporary, non-transferring access; compiler-verified alias safety.
- **Manual allocation regions** — arenas and pools for allocation-pattern-sensitive code.
- **GPU memory classes** — first-class language representation of global, shared, and local address spaces for kernel code.

The memory model is not designed to impose a single discipline. It is designed to make the programmer's intent explicit and the compiler's enforcement verifiable.

---

## Standard Library

The ManV standard library is authored in ManV. There is no foreign-language runtime delegation. The boundary between the standard library and the compiler is the `__intrin` layer — compiler-known operations representing primitive capabilities (byte-level I/O, hardware arithmetic, system calls, memory allocation) that cannot be expressed in terms of other ManV code.

The intrinsic boundary is narrow by policy. No new broad subsystem functionality (JSON parsing, HTTP, regex) may be implemented as an intrinsic; these belong in the stdlib as ordinary ManV code that uses intrinsics for the primitives they need.

Planned stdlib modules: core language support, string operations, math, collections, I/O and filesystem, system and process, random, network, JSON, and GPU.

Intrinsics are assigned stable versioned identifiers. Existing code depending on a specific intrinsic version continues to work against its known contract as the language evolves.

---

## Tooling

The `manv` CLI provides the complete development workflow:

| Command | Purpose |
|---------|---------|
| `manv init` | Scaffold a new project |
| `manv run` | Execute in interpreter or compiled mode |
| `manv compile --emit ...` | Emit compilation artifacts |
| `manv build` | Produce a distribution artifact |
| `manv repl` | Interactive REPL |
| `manv test` | Run the end-to-end test suite |
| `manv dap` | Start a Debug Adapter Protocol server |
| `manv lsp` | Start a Language Server Protocol server |
| `manv add` | Add a package dependency |

The `--emit` flag accepts a comma-separated list of pipeline stages. Useful combinations:

- All IR stages: `ast,hir,hlir,graph,kernel`
- Native code: `asm,native_obj,native_exe`
- GPU artifacts: `ptx` (NVIDIA), `spirv` (Vulkan/AMD), `wgsl` (WebGPU)
- ABI description: `abi`

Build artifacts are written to `.manv/target` by default.

`manv dap` starts a DAP server for source-level debugging (stdio or tcp transport), integrated with the interpreter execution path and its full HLIR provenance. `manv lsp` starts an LSP server via pygls for editor integration.

---

## Use Cases

**ML training and inference.** ManV targets training pipelines and inference servers directly. The interpreter-plus-debugger path handles development and validation; the compiled path with GPU acceleration handles production runs. Both execute the same source without modification.

**Data processing pipelines.** Array and map primitives combined with GPU extraction handle compute-intensive transformation steps without explicit kernel management. The syscall interface and filesystem stdlib provide direct access to disk and network for I/O-heavy stages.

**GPU-heavy computation.** Simulation, image processing, scientific computation. Explicit kernel control is available alongside automatic extraction. Multi-backend support means code written for CUDA runs on AMD or Intel hardware without source changes.

**Mixed CPU/GPU systems.** The execution model accommodates orchestration on CPU and kernel execution on GPU within the same program. DAP and LSP support covers the full system during development.

---

## Roadmap

**LLVM backend.** HLIR-to-LLVM-IR lowering is the active development surface. It replaces the current assembly codegen with LLVM IR emission, enabling LLVM's optimization pipeline, link-time optimization, and any target LLVM supports.

**Packaging system.** The registry backend and authentication are operational. Remaining: reproducible dependency resolution with version locking, source distribution format, package signing, and scoped namespaces.

**Memory model completion.** Ownership, borrow semantics, manual allocation regions, and GPU memory class annotations — introduced incrementally.

**GPU standard library.** Higher-level kernel launch abstractions (map, reduce, scan), device memory management utilities, synchronization primitives, and profiling hooks — implemented in ManV on the Kernel IR path.

**Performance target.** The compiled path should reach memory-bandwidth-bound performance for elementwise and reduction operations over large arrays — the limiting factor is device memory throughput, not compute throughput or kernel overhead.

---

## Current Status

ManV is in active v1 foundation development. Current emphasis: semantic correctness, deterministic diagnostics, debugger integration (DAP), language server integration (LSP), and backend extensibility for native GPU execution.

Full design documentation is available in the [docs portal](../website/).
