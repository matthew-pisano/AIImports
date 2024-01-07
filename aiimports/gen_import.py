import os
import shutil

import torch
import universalmodels

module_cache_path = ".cache"


def set_cache_location(path: str):
    """Sets the location of the cache directory that generated files will be saved to

    Args:
        path: The path of the cache directory"""

    global module_cache_path

    module_cache_path = path


def clear_cache():
    """Removes the cache directory to allow for the re-generation of imported code"""

    shutil.rmtree(module_cache_path)
    os.mkdir(module_cache_path)


def module_has_member(module_source: str, member_name: str):
    """Given the name of a member and source code, this function checks if the member is a
    global variable, function, class, or is absent from the code

    Args:
        module_source: The source code to search for the member in
        member_name: The member to search for

    Returns:
        Whether the source code contains the member"""

    if "\n"+member_name in "\n"+module_source:
        return True
    if "\ndef"+member_name in "\n"+module_source.replace(" ", ""):
        return True
    if "\nclass"+member_name in "\n"+module_source.replace(" ", ""):
        return True

    return False


def generate_member(model_name: str, module_path: str, module_source: str, member_name: str):
    """Generates the code for a member from the member's name and the module it is a member from

    Args:
        model_name: The name of the AI model to use for generation
        module_path: The path of the module (<module>.submodule>...)
        module_source: The existing source code for the module, if any
        member_name: The name of the member to generate code for

    Returns:
        The new source code for the member"""

    model, tokenizer = universalmodels.pretrained_from_name(model_name)

    prompt = f"""You are an experienced python developer.  You specialize in writing short code snippets for functions and classes.
Do not give any explanation of the code, generate pure python code and nothing else. Please write the code to complete the following:
A class or function named `{member_name}` within a module named `{module_path}`."""
    if module_source:
        prompt += f"""The module has this code already written.  Generate your new code based on the member name, module name, and this existing code:
```{module_source}```"""
    member_source = tokenizer.decode(model.generate(torch.Tensor([tokenizer.encode(prompt+"\n")]))[0]).strip("\n")
    member_source.replace("```python", "").replace("\n```", "")

    return member_source


def import_module(import_path: str, model_name: str = None, requested_members=None):
    """Imports a module from the cache, automatically generating any code that is needed

    Args:
        import_path: The full, dot-delimited path of the module, relative to the cache root
        model_name: The name of the model to use for generation
        requested_members: The members that have been requested to import, generated as needed

    Returns:
        The updated module source code and the file system path to the module file"""

    source_file_path = os.path.join(module_cache_path, import_path.replace(".", "/")) + ".py"

    # Make the parent directories and an empty source file if the module does not yet exist in the cache
    if not os.path.isfile(source_file_path):
        if "." in import_path:
            source_parent_path = source_file_path[:source_file_path.rindex("/")]
            os.makedirs(source_parent_path, exist_ok=True)
        open(source_file_path, 'a').close()

    # Read in any existing source code for the module
    with open(source_file_path, "r") as f:
        source = f.read()

    # If the user requested members to import, generate them
    if requested_members:
        modified_source = False
        for member_name in requested_members:
            if not module_has_member(source, member_name):
                member_source = generate_member(model_name, import_path, source, member_name)
                source += "\n" + member_source
                modified_source = True

        # If the source has been modified, save the file
        if modified_source:
            with open(source_file_path, "w") as f:
                f.write(source)

    return source, source_file_path
