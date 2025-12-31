# Architecture

## Guiding principles

The architecture uses the principles from Robert C. Martin's _Clean Architecture_ and [SOLID](https://en.wikipedia.org/wiki/SOLID), in particular:

- [Single-Responsibility Principle](https://en.wikipedia.org/wiki/Single-responsibility_principle) (SRP) for classes, and the Common Closure Principle (CCP) for components.
- [Dependency-inversion principle](https://en.wikipedia.org/wiki/Dependency_inversion_principle)
- [Open-Closed Principle](https://en.wikipedia.org/wiki/Open%E2%80%93closed_principle) (OCP)
- Common-Reuse Principle (CRP), a generalized version of [Interface-Segregation Principle](https://en.wikipedia.org/wiki/Interface_segregation_principle) (ISP)

## Modules

The modules are organized according to the dependency inversion principle, thus model cannot depend on any higher layers, and use-case can only depend on modules in the entity layer. In order to allow a lower layer to use elements of a higher layer, it has to define a protocol to be implemented by the higher layer.

### Controller
- `cli` contains the command line interface.
- `ui` contains the view code for setup and display user interfaces.
- `trainer` contains the trainer handling code.
- `config` contains the configuration.

### Use-case
- `workout` contains the core business logic for our use-cases.
- `bootstrap` contains code for assembling and starting the application.

### Entity
- `model` contains the data models such as workout plans, intervals, and current workout state.

## Demo mode

The application should support a functional demo mode available with the `--demo` command line toggle. This allows testing the application without a trainer available. This also benefits testing.

## Testing

All code should have unit tests, but care should be taken not to bloat the test suite with redundant tests. The test data should as a rule be _generated_, and not provided statically.
