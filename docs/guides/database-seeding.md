# Guide: Database Seeding

Database seeding is the process of populating a database with an initial set of data, such as lookup table values (`Roles`, `Statuses`) or default administrative users. `ant31box` provides a standardized CLI command to make this process easy to integrate into your application.

## Step 1: Create a Seeder Function

The core of the seeding process is an `async` function that accepts a SQLAlchemy `AsyncSession` object. This function will contain your application-specific logic for creating initial data.

It's a good practice to organize your seeding logic into modules by feature.

**Example:**
File: `my_app/seed/main.py`
```python
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from my_app.seed.auth import seed_roles

logger = logging.getLogger(__name__)

async def seed_all(session: AsyncSession):
    """
    Orchestrates seeding of all application features.
    """
    logger.info("Seeding all features...")
    await seed_roles(session)
    # ... call other seeders
    logger.info("All features seeded.")
```

File: `my_app/seed/auth.py`
```python
from sqlalchemy.ext.asyncio import AsyncSession
from my_app.models import Role
from my_app.repositories import RoleRepository

async def seed_roles(session: AsyncSession):
    """Seed the default user roles."""
    repo = RoleRepository(session)
    if not await repo.find_by(name="admin"):
        await repo.save(Role(name="admin"))
```

## Step 2: Configure the Seeder Path

Next, you need to tell `ant31box` where to find your main seeder function. You do this by setting the `app.seeder` property in your `config.yaml` file. The value should be an "import string" in the format `path.to.module:function_name`.

**Example:**
File: `config.yaml`
```yaml
app:
  env: "dev"
  # This points to the seed_all function in my_app/seed/main.py
  seeder: "my_app.seed.main:seed_all"

# ... other configurations
```

## Step 3: Run the Seeding Command

With the configuration in place, you can now use the built-in `seed db` command to run your seeder. The command will handle:
1.  Loading your application's configuration.
2.  Initializing the database engine.
3.  Creating a database session.
4.  Importing and calling your seeder function with the session.
5.  Committing the transaction upon successful completion.

Run the command from your terminal:
```bash
# Assuming your CLI entry point is 'my-cli'
my-cli seed db

# You can also specify a config file
my-cli seed db --config config.prod.yaml
```
