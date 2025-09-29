# Concept: Dependency Injection

`ant31box` is moving towards a **Dependency Injection (DI)** pattern to promote cleaner, more testable, and more maintainable code. This means that instead of components relying on a hidden global state (like a global configuration object), their dependencies are "injected" into them, usually during initialization.

## The Problem with Global State

In earlier versions, many components used the global `config()` singleton to get their settings:

```python
# Old pattern (relying on global state)
from ant31box.config import config
from ant31box.s3 import S3Client

def create_s3_client():
    # This function implicitly depends on the global config.
    # It's hard to test with different configurations.
    s3_settings = config().conf.s3
    return S3Client(s3_settings)
```
This approach has several drawbacks:
-   **Hidden Dependencies**: It's not obvious what a function or class needs to operate.
-   **Difficult to Test**: You can't easily test the function with different configurations without manipulating the global state, which can lead to flaky tests.
-   **Reduced Reusability**: Components are tightly coupled to the global application environment.

## The Dependency Injection Solution

With DI, we explicitly pass dependencies (like the configuration object) to the functions or classes that need them.

```python
# New pattern (using dependency injection)
from ant31box.config import Config, S3ConfigSchema
from ant31box.s3 import S3Client

def create_s3_client(conf: Config) -> S3Client:
    # The dependency (conf) is now explicit and required.
    # It's clear what this function needs.
    # We can easily pass a test configuration during testing.
    s3_settings = conf.conf.s3 # Assuming s3 is part of the schema
    return S3Client(s3_settings)

# --- Usage ---
from ant31box.config import config

# Load config once at the application's entry point
main_config = config()

# Inject the dependency
s3_client = create_s3_client(conf=main_config)
```

### Benefits of This Approach

-   **Explicit Dependencies**: Function and class signatures clearly declare what they need to work.
-   **Improved Testability**: In tests, you can create a specific `Config` object with test settings and pass it directly, isolating the test from the global environment.
-   **Better Reusability**: Components are self-contained and can be reused in different contexts by providing the appropriate dependencies.

## Where We Use It

This pattern is now the recommended approach for all core `ant31box` components:
-   `serve(conf=...)`: The FastAPI server builder.
-   `filedl_client(conf=...)`: The download client factory.
-   All CLI commands that require configuration.

As you build your applications with `ant31box`, we strongly recommend adopting this pattern. **Load your configuration once at the top level of your application and pass it down to where it's needed.**
