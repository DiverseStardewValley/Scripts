import sys
from importlib.util import module_from_spec, spec_from_file_location

from setuptools import setup


def get_console_scripts() -> list[str]:
    package_name = "dsv_scripts"
    console_scripts = [f"dsv-scripts = {package_name}.__main__:main"]
    module_spec = spec_from_file_location(package_name, f"{package_name}/__init__.py")

    if module_spec and module_spec.loader:
        dsv_scripts = module_from_spec(module_spec)
        sys.modules[package_name] = dsv_scripts
        module_spec.loader.exec_module(dsv_scripts)

        console_scripts.extend(
            f"{dsv_scripts.get_script_name(module_path)} = "
            f"{package_name}.{module_path.stem}:main"
            for module_path in dsv_scripts.get_script_module_paths()
        )

    return console_scripts


setup(
    entry_points={
        "console_scripts": get_console_scripts(),
    },
    install_requires=[
        "humanize >=4.4.0",
        "pyjson5 >=1.6.2",
        "rich >=12.6.0",
    ],
    url="https://github.com/DiverseStardewValley/Scripts",
)
