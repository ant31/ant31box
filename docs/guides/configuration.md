# Guide: Configuration Management

`ant31box` uses a powerful and flexible configuration system built on `pydantic-settings`. This allows for type-safe configuration management from multiple sources, ensuring your application is easy to configure for different environments.

## Configuration Hierarchy

Configuration is loaded from the following sources, in order of precedence (lower numbers are overridden by higher numbers):

1.  **Default Schema Values**: Defaults defined directly in the Pydantic models in `ant31box/config.py`.
2.  **YAML Configuration File**: A YAML file can be specified to provide configuration values.
3.  **Environment Variables**: Any configuration value can be overridden by an environment variable. Environment variables take the highest precedence.

## The `ConfigSchema`

The main configuration structure is defined in `ant31box/config.py` within the `ConfigSchema` class. This class uses nested Pydantic models to organize configuration by domain (e.g., `server`, `logging`).

### Environment Variables

You can override any configuration setting using an environment variable. The variable name is constructed based on the schema structure:

-   It starts with the prefix `ANT31BOX_`.
-   Nested keys are separated by a double underscore `__`.
-   The variable name is case-insensitive.

**Examples:**

-   To set the server port: `export ANT31BOX_SERVER__PORT=8001`
-   To set the application environment: `export ANT31BOX_APP__ENV=production`

## Loading Configuration

The configuration is loaded via the `config()` function in `ant31box/config.py`. The recommended pattern is to load it once at your application's entry point and then pass the resulting config object to the components that need it.

```python
# In your main.py or application entry point
from ant31box.config import config, DefaultConfig

def main():
    # Load config from default paths (localconfig.yaml, config.yaml) or environment variables
    conf: DefaultConfig = config()

    # Load config from a specific YAML file
    conf_from_file: DefaultConfig = config(path="/path/to/my/config.yaml")

    # Use the config objects...
    print(conf.app.env)
    print(conf_from_file.app.env)

if __name__ == "__main__":
    main()
```

The CLI commands also provide an option to specify a configuration file using the `-c` or `--config` flag.

## Extending the Configuration

To add configuration for your own application, create a custom schema that inherits from `ConfigSchema`.

**1. Define your custom schema:**

```python
# my_app/config.py
from pydantic import Field, BaseModel
from ant31box.config import ConfigSchema, S3ConfigSchema

class MyServiceConfig(BaseModel):
    api_key: str = Field(..., description="API key for My Service.")
    timeout: int = Field(default=30)

class MyAppConfigSchema(ConfigSchema):
    # Add S3 configuration if you need it globally
    s3: S3ConfigSchema = Field(default_factory=S3ConfigSchema)
    # Add your custom service's configuration
    my_service: MyServiceConfig = Field(default_factory=MyServiceConfig)
```

**2. Load your custom config class:**

Tell the `config()` loader to use your new schema class.

```python
# my_app/main.py
from ant31box.config import config, Config
from .config import MyAppConfigSchema

class MyAppConfig(Config[MyAppConfigSchema]):
     __config_class__ = MyAppConfigSchema

# Load your custom configuration schema
conf: MyAppConfig = config(confclass=MyAppConfig)

# Now you can access your custom settings
print(conf.conf.my_service.api_key)
print(conf.conf.s3.bucket)
```
