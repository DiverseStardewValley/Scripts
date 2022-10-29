import sys
from importlib.util import module_from_spec, spec_from_file_location

from setuptools import setup


def get_console_scripts() -> list[str]:
    package_name = "dsv_scripts"
    console_scripts = [
        f"{script_name} = {package_name}.__main__:main"
        for script_name in ("dsv", "dsv-scripts")
    ]
    module_spec = spec_from_file_location(package_name, f"{package_name}/__init__.py")

    if module_spec and module_spec.loader:
        dsv_scripts = module_from_spec(module_spec)
        sys.modules[package_name] = dsv_scripts
        module_spec.loader.exec_module(dsv_scripts)

        console_scripts.extend(
            f"{dsv_scripts.get_script_name(module)} = {module.__name__}:main"
            for module in dsv_scripts.get_script_modules()
        )

    return console_scripts


setup(
    entry_points={
        "console_scripts": get_console_scripts(),
    },
    install_requires=[
        "rich >=12.6.0",
    ],
    url="https://github.com/DiverseStardewValley/Scripts",
)
