import ast
import importlib
import importlib.abc
import importlib.machinery
import re
import sys
import types
import builtins
import inspect

from .gen_import import import_module, set_cache_location

original_import = builtins.__import__


def _import(module_name, *args, **kwargs):
    """Injects code into __import__ that tracks the module being imported

    Args:
        module_name: The module being imported
    Returns:
        The unmodified return value of __import__"""

    AIFinder.add_possible_import(module_name)
    return original_import(module_name, *args, **kwargs)


def activate(cache_path: str = ".cache"):
    """Activates AIImports.  After this function is called, all imports will be intercepted
    and code will be generated for ones that do not exist

    Args:
        cache_path: The path to cache the generated module code"""

    set_cache_location(cache_path)
    builtins.__import__ = _import
    if not isinstance(sys.meta_path[-1], AIFinder):
        sys.meta_path.append(AIFinder())


class AIFinder(importlib.abc.MetaPathFinder):
    """Custom finder that calls code generation logic.  Code is generated when a member is imported from a module in the form:

    `from <module>.submodule> import <member>, <member>`"""

    _DEFAULT_MODEL_NAME = "dev/human"
    possible_imports = []
    module_blacklist = []

    def __init__(self, model_name: str = _DEFAULT_MODEL_NAME):
        """
        Args:
            model_name: The name of the model to use for generation"""

        self.model_name = model_name

    def find_spec(self, fullname: str, path: str, target=None):
        """Gets the spec object for the requested module

        Args:
            fullname: The full name of the module to import
        Returns:
            The module spec"""

        spec = self._gen_source(fullname)
        return spec

    def _gen_source(self, fullname: str):
        """Creates a module spec object with code generated based on the name of the module and the imported member

        Args:
            fullname: The name of the module being imported

        Returns:
            A module spec object corresponding to the imported module"""

        # Ensure that the module is not in the blacklist
        # Blacklisted models will throw an import error like usual
        for regex_str in self.module_blacklist:
            if re.match(regex_str, fullname):
                return None

        source = ""
        source_path = None
        is_package = True
        # If the fullname is the full <module>.<submodule>... path instead of the top level module
        if fullname in self.possible_imports:
            # Since this is the bottom of the module tree, no longer look for submodules
            is_package = False
            # Get a list of all members imported
            requested_members = self._get_requested_members()
            # Generate source code given the module path and the members required
            source, source_path = import_module(fullname, self.model_name, requested_members)

        # Ensure that the generate code is valid python
        if source is None or not self._is_valid_python_source(source):
            return None

        loader = AILoader(fullname, source, source_path)
        return importlib.machinery.ModuleSpec(fullname, loader, origin=source_path, is_package=is_package)

    @classmethod
    def add_possible_import(cls, module_path: str):
        """Records all full module paths imported to be passed at once to the loader instead of
        importing one submodule at a time.  Tells the loader when the last submodule has been reached

        Args:
            module_path: The full path of the module and all submodules"""

        cls.possible_imports.append(module_path)

    @staticmethod
    def _get_requested_members():
        """Uses the call stack to get the line where the imported member was requested.  Usually,
        the member is not included in the argument for the import function so this is used to recover it

        Returns:
            The string names of each module member to be imported"""

        call_stack = inspect.stack()
        for frame in call_stack:
            ctx = frame.code_context[0] if frame.code_context and len(frame.code_context) else None
            if ctx and ctx.startswith("from"):
                members = ctx[ctx.index("import")+6:].split(",")
                members = [mem.strip() for mem in members]
                return members
        return None

    @staticmethod
    def _is_valid_python_source(code: str) -> bool:
        """Checks if the given code is valid python

        Args:
            code: The code to check
        Returns:
            Whether the code is valid"""

        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False


class AILoader(importlib.abc.Loader):
    """Loads in the source code for a module to be executed and imported"""

    def __init__(self, fullname: str, source_code: str, source_path: str):
        """
        Args:
            fullname: The full name of the module to be loaded
            source_code: The generated source code of the model
            source_path: The local file path for the source code"""

        self.fullname = fullname
        self.source_code = source_code
        self.source_path = source_path

    def create_module(self, spec):
        """Creates a module from the given spec

        Args:
            spec: The spec to use for the module
        Returns:
            The module object"""

        module = sys.modules.get(spec.name)
        if module is None:
            module = types.ModuleType(spec.name)
            sys.modules[spec.name] = module
        return module

    def exec_module(self, module):
        """Executes the module to load its code

        Args:
            module: The module to load
        Returns:
            The loaded module"""

        module.__file__ = self.source_path
        exec(self.source_code, module.__dict__)
        return module


def set_model(model_name: str):
    """Resets the model to use for code generation

    Args:
        model_name: The name of the model to use"""

    if isinstance(sys.meta_path[-1], AIFinder):
        sys.meta_path.pop(-1)
    sys.meta_path.append(AIFinder(model_name))


def blacklist_module(regex_str: str):
    """Blacklists all modules matching the given regex string.  When these modules are encountered,
    no code is generated and an error is thrown

    Args:
        regex_str: The regex string"""

    AIFinder.module_blacklist.append(regex_str)

