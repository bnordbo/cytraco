# How to develop Cyctraco

## Code style

Use the code style specified in [PEP8](https://peps.python.org/pep-0008/) as a basis, but with the following modifications and addendums:

- The maximum line length is 100 characters
- Always use [type hints](https://peps.python.org/pep-0484/) for method argument and return values.
- Prefer [union types](https://peps.python.org/pep-0604/) to `Optional` for type hints.
- Only import frequently used members.
