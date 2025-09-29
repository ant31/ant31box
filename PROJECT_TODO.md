# ant31box Project Improvement Plan

This document outlines the development roadmap to elevate `ant31box` into a robust, S-tier foundational library for bootstrapping Python-based microservices. The target is to achieve a quality score of 18/20 or higher, focusing on architecture, usability, and reliability.

---

## Epic 1: Architectural Refactoring & Modernization

**Goal:** Establish a rock-solid, scalable, and testable foundation by eliminating architectural flaws like global state and ensuring true asynchronicity.

-   [ ] **Decouple Configuration (Eliminate Singleton):**
    -   [ ] Remove the global `GConfig` singleton pattern from `ant31box/config.py`.
    -   [ ] Refactor components that depend on `config()` (e.g., `serve()`, `DownloadClient`) to accept the configuration object via explicit dependency injection.
    -   [ ] Update tests to pass configuration objects to components instead of relying on the `reset_config` fixture.
    -   [ ] Update all documentation and examples to reflect the dependency injection pattern.

-   [ ] **Ensure True Asynchronicity:**
    -   [ ] Add `aioboto3` as a dependency for S3 operations.
    -   [ ] Rewrite `ant31box/s3.py` and the S3 methods in `ant31box/client/filedl.py` to use `aioboto3` and be fully `async/await`, removing all blocking I/O calls.
    -   [ ] Audit the entire codebase for any other hidden synchronous I/O calls within `async` functions.

---

## Epic 2: Code Unification & Cleanup

**Goal:** Improve code consistency and maintainability by removing duplication, standardizing frameworks, and simplifying the project structure.

-   [ ] **Standardize on a Single CLI Framework:**
    -   [ ] Choose `typer` as the official CLI framework for the project.
    -   [ ] Port any missing functionality from the old `click` commands (`ant31box/cmd/*`) to their `typer` equivalents (`ant31box/cmd/typer/*`).
    -   [ ] Delete the `ant31box/cmd` directory and its contents.
    -   [ ] Update the `[project.scripts]` entry point in `pyproject.toml` to point to the main `typer` application.
    -   [ ] Ensure all CLI-related documentation and examples use `typer`.

-   [ ] **Eliminate Code Duplication:**
    -   [ ] Delete `ant31box/utilsd.py`.
    -   [ ] Refactor all usages of its `import_from_string` to use the canonical version in `ant31box/importer.py`.

---

## Epic 3: Comprehensive Documentation & Developer Experience (DX)

**Goal:** Create outstanding documentation and clear usage patterns that make `ant31box` a pleasure to use.

-   [ ] **Create a "Quickstart" / "Getting Started" Guide:**
    -   [ ] Write a tutorial in the `README.md` or a new `docs/getting_started.md` that walks a developer through bootstrapping a brand new microservice, from setting up the config to creating a custom API endpoint.

-   [ ] **Write In-Depth Guides for Core Features:**
    -   [ ] **Configuration:** A detailed guide on extending `ConfigSchema`, the file and environment variable loading hierarchy, and best practices.
    -   [ ] **FastAPI Server:** Document how to add/replace middlewares and routers, how the default setup works, and how to extend the `Server` class for advanced use cases.
    -   [ ] **CLI:** Explain how to add new commands and groups to the application's CLI.

-   [ ] **Generate a Complete API Reference:**
    -   [ ] Add comprehensive, Google-style docstrings to all public modules, classes, and functions.
    -   [ ] Set up a tool like `mkdocs` with `mkdocstrings` to automatically generate a hosted API reference site.

---

## Epic 4: Testing & Reliability Enhancement

**Goal:** Achieve near-complete test coverage to guarantee stability and prevent regressions.

-   [ ] **Increase Test Coverage to >95%:**
    -   [ ] Write comprehensive tests for all server middlewares (`token.py`, `errors.py`, `process_time.py`).
    -   [ ] Add tests for the server startup logic and the dynamic loading of routers/middlewares.
    -   [ ] Test edge cases in the configuration loading logic.
    -   [ ] Ensure all CLI commands are tested for correctness.

-   [ ] **Improve Test Suite Quality:**
    -   [ ] Remove the `reset_config` fixture after the singleton is removed (see Epic 1).
    -   [ ] Set up code coverage reporting (e.g., Codecov) to track coverage over time.

---

## Epic 5: Foundational Feature Expansion

**Goal:** Add critical, opinionated integrations that are essential for modern microservices.

-   [ ] **Add a Database Layer (Opinionated Choice):**
    -   [ ] Integrate `achemy` (or another SQLAlchemy 2.0 async toolkit) as the default database library.
    -   [ ] Provide a base repository pattern and session management helpers that integrate with the FastAPI server (e.g., a `Depends` provider for sessions/repositories).
    -   [ ] Add a `DatabaseConfigSchema` to the main configuration.
    -   [ ] Create documentation and examples for defining models and using the repository pattern.

-   [ ] **Structured, Production-Ready Logging:**
    -   [ ] Implement a logger configuration that can easily switch between colorized console logging (for development) and structured JSON logging (for production).
    -   [ ] Ensure FastAPI access logs also follow the structured logging format.
