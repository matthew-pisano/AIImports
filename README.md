# AI Generated Imports

> [!CAUTION]
> This package is primarily for educational purposes involving python's `importlib`!  It executes arbitrary, untested, and AI generated code use with caution within the provided containerized environment!

This package almost completely eliminates import errors from python code.  This is done by inserting code into the python import process ([importer.py](aiimports/importer.py)).  Using the `importlib` API, a custom module finder and loader can be inserted into `sys.meta_path`.  This code then uses the text of the import statement to automatically generate new code that matches the user's specification and executes that code to successfully import a module, even if it has never existed in the first place.

## Usage

This package can be imported into any arbitrary module to generate code for any `import` statements that would usually raise an `ImportError`.  Once this importer has been activated, any imports in the form `from <module>.submodule> import <member>, <member>` will have code for each member generated and saved to disk in a cache directory.  This code will persist between runs and can be referenced until the source code is deleted by the user.

### Example

```python
import aiimports
# Activate package.  Imports will behave normally until this function is called
# Generated code will be saved to the below directory
aiimports.activate(cache_path=".cache")

# Even though this package does not currently exist, it runs perfectly well thanks to the generated code.
from halting_problem.helpers import solve

solve()
```

Further examples can be found within the [examples/](examples) directory.

## Quick Start

### Installing from Source

> [!WARNING]
> Ensure this package is installed within a virtual environment.  Even though this code does not run unless `aiimports.activate()` is called, it is still wise to isolate it to a virtual environment.

1. Clone repository
    ```bash
    git clone https://github.com/matthew-pisano/AIImports
    cd AIImports
    ```
2. Install package and run

    Install to venv
    ```bash
    python3 -m venv venv
    source ./venv/bin/activate
    python3 -m pip install -e "."
    ```

    *OR*

    Build and run a docker container after inserting a custom command into the [Dockerfile](Dockerfile)

    ```bash
    docker build -t aiimports .
    docker run -it aiimports
    ```
