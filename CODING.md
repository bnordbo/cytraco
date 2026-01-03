# How to develop Cyctraco

## Code style

Use the code style specified in [PEP8](https://peps.python.org/pep-0008/) as a basis, but with the following modifications and addendums:

- The maximum line length is 100 characters
- Always use [type hints](https://peps.python.org/pep-0484/) for method argument and return values.
- Prefer [union types](https://peps.python.org/pep-0604/) to `Optional` for type hints.
- Only import frequently used members.
- Prefer simple list comprehensions to for loops for constructing collections.
- Import modules for context, e.g. `import asyncio`.
- Import commonly used names, e.g. `from dataclasses import dataclass`. 
- Use import aliases as appropriate, e.g. `import numpy as np`. 
- Always use a trailing comma in function calls, function definitions, literals, etc.
- Test data should be generated, _not_ literals.
- Only comment complex or unusual code.
- Don't declare variables that are only used once, and whose name does not add anything.
- Use vertical whitespace inside methods sparingly, and only to separate logical sections.
- Alias import to shorter names, e.g. config -> cfg. Module aliases are documented on the first line of each module.
