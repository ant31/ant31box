# Contributing: Coding Style

This document outlines the coding conventions to be followed in this project. Adhering to these conventions ensures consistency, readability, and maintainability of the codebase.

## Python Style

-   **Version**: Write code compatible with Python 3.12 features and style.
-   **Formatting & Linting**: We use `ruff` for all formatting, linting, and import sorting. Adhere to the configurations defined in `pyproject.toml` and `ruff.toml`.
    -   To format your code, run: `make format`
    -   To sort imports, run: `make isort`
    -   To check for issues, run: `make check`
    -   Most issues can be fixed automatically by running: `make fix`
-   **Naming**:
    -   Use `snake_case` for variables, functions, methods, and modules.
    -   Use `PascalCase` for classes.
    -   Use `UPPER_SNAKE_CASE` for constants.
-   **Docstrings**: Write clear and concise docstrings for all public modules, classes, functions, and methods. Google style docstrings are preferred.
-   **Import conditions**: Do not safeguard imports to check if a library is not installed. If it's not installed then the program will fail as expected. This is part of dependency management.
-   **Code organization**: Split code into modules and packages for various features. Aim for short, focused Python files.

### Don't Safeguard Imports
*  **Bad:**
   ```python
   try:
       import pydot
   except ImportError:
       pydot = None
   ```
* **Good:**
   ```python
   import pydot
   ```

## Code Comments

-   **Focus**: Comments should explain the *why* behind the code, clarify complex logic, or document non-obvious decisions. They should not just describe *what* the code is doing.
-   **Timelessness**: Write comments that will remain true and relevant over time. Avoid comments that refer to the development process, specific points in time, or temporary states.
-   **Avoid Redundancy**: Do not comment on obvious code. Good code should be largely self-documenting.

## Type Hinting

-   **Mandatory**: All function signatures, method signatures, and variables where the type isn't immediately obvious should have type hints.
-   **Style**: Use Python 3.10+ style type hints:
    -   Use built-in generic types (e.g., `list[int]`, `dict[str, float]`) instead of importing from `typing` (`List`, `Dict`) where possible.
    -   Use the `|` operator for unions (e.g., `int | str`) instead of `typing.Union`.
    -   Use `X | None` for optional types (e.g., `str | None`) instead of `typing.Optional`.

## Pydantic (v2)

-   **Usage**: Use Pydantic models for data validation, serialization/deserialization, API request/response models, and complex configuration structures.
-   **Field Definitions**:
    -   Always initialize fields using `Field()`.
    -   Provide a `default=` value or `default_factory=` for optional fields within `Field()`.
    -   Use `Field(..., description="...")` for required fields.
    -   Include a `description=` for all fields to improve clarity.
-   **Methods**: Use `model_validate()` for parsing/validation and `model_dump()` for serialization instead of the deprecated V1 methods.
