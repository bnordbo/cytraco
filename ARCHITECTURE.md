# Architecture

Cytraco 2.0 uses a ports and adapters style architecture.

- `cli` contains the command line interface, i.e. showing options, as well as setting up and  starting the application.
- `model` contains the data models such as workout plans, intervals, and current workout state.
- `ui` contains the view code for setup and display user interfaces.
- `controller` contains the controller.
- `trainer` contains the trainer handling code.
- `config` contains the configuration.

## Demo mode

The application should support a functional demo mode available with the `--demo` command line toggle. This allows testing the application without a trainer available. This also benefits testing.

## Testing

All code should have unit tests, but care should be taken not to bloat the test suite with redundant tests. The test data should as a rule be _generated_, and not provided statically.
