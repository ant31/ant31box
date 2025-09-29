# ant31box Project Improvement Plan

This document outlines the development roadmap to elevate `ant31box` into a robust, S-tier foundational library for bootstrapping Python-based microservices. The target is to achieve a quality score of 18/20 or higher, focusing on architecture, usability, and reliability.

---

## Epic 1: Architectural Refactoring & Modernization

**Goal:** Establish a rock-solid, scalable, and testable foundation by eliminating architectural flaws like global state and ensuring true asynchronicity.

-   [x] **Decouple Configuration (Introduce Dependency Injection):**
    -   [x] Refactor components that depend on `config()` (e.g., `serve()`, `DownloadClient`, CLI commands) to accept an optional configuration object via dependency injection, maintaining backward compatibility.
    -   [x] Update tests to use the new dependency injection pattern with a `test_config` fixture.
    -   [x] Update all documentation and examples to reflect the dependency injection pattern.
    -   [ ] *Future Task:* Remove the global `GConfig` singleton pattern from `ant31box/config.py` in a future major version release after a deprecation period.

-   [x] **Ensure True Asynchronicity:**
    -   [x] Add `aioboto3` as a dependency for S3 operations.
    -   [x] Rewrite `ant31box/s3.py` and the S3 methods in `ant31box/client/filedl.py` to use `aioboto3` and be fully `async/await`, removing all blocking I/O calls.
    -   [ ] Audit the entire codebase for any other hidden synchronous I/O calls within `async` functions.

---

## Epic 2: Code Unification & Cleanup

**Goal:** Improve code consistency and maintainability by removing duplication, standardizing frameworks, and simplifying the project structure.

-   [x] **Standardize on a Single CLI Framework:**
    -   [x] Chose `typer` as the official CLI framework for the project.
    -   [x] Update the `[project.scripts]` entry point in `pyproject.toml` to point to the main `typer` application.
    -   [x] Ensure all CLI-related documentation and examples use `typer`.
    -   [x] Add a separate `ant31box-click` entry point for backward compatibility and issue a `DeprecationWarning`.
    -   [ ] *Future Task:* Remove the `click`-based CLI in `ant31box/cmd` in a future major version release after a deprecation period.

-   [x] **Eliminate Code Duplication:**
    -   [x] Delete `ant31box/utilsd.py`.
    -   [x] Refactor all usages of its `import_from_string` and `deepmerge` to use the canonical versions in `ant31box/importer.py` and `ant31box/config.py`.

---

## Epic 3: Comprehensive Documentation & Developer Experience (DX)

**Goal:** Create outstanding documentation and clear usage patterns that make `ant31box` a pleasure to use.

-   [x] **Create a "Quickstart" / "Getting Started" Guide:**
    -   [x] Write a tutorial in the `README.md` that walks a developer through bootstrapping a brand new microservice, from setting up the config to creating a custom API endpoint.

-   [ ] **Write In-Depth Guides for Core Features:**
    -   [ ] **Configuration:** A detailed guide on extending `ConfigSchema`, the file and environment variable loading hierarchy, and best practices.
    -   [ ] **FastAPI Server:** Document how to add/replace middlewares and routers, how the default setup works, and how to extend the `Server` class for advanced use cases.
    -   [x] **CLI:** Explain how to add new commands and groups to the application's CLI.

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

-   [x] **Add a Database Layer (Opinionated Choice):**
    -   [x] Integrate `achemy` (or another SQLAlchemy 2.0 async toolkit) as the default database library.
    -   [x] Provide a base repository pattern and session management helpers that integrate with the FastAPI server (e.g., a `Depends` provider for sessions/repositories).
    -   [x] Add a `DatabaseConfigSchema` to the main configuration.
    -   [x] Add a generic `get_db_session` dependency provider in `ant31box.server.dependencies`.
    -   [x] Implement database engine lifecycle management within the FastAPI server.
    -   [x] Create documentation and examples for defining models and using the repository pattern.

-   [x] **Add a Database Seeding Framework:**
    -   [x] Add a `seeder` configuration option to `AppConfigSchema`.
    -   [x] Create a `seed` command in the `typer` CLI that dynamically loads and runs the seeder function.
    -   [x] The command should provide a database session to the seeder function.
    -   [x] Write a guide on how to create and use a seeder.

-   [ ] **Structured, Production-Ready Logging:**
    -   [ ] Implement a logger configuration that can easily switch between colorized console logging (for development) and structured JSON logging (for production).
    -   [ ] Ensure FastAPI access logs also follow the structured logging format.
