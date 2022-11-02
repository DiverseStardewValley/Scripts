# <a href="https://github.com/DiverseStardewValley"><img src="https://avatars.githubusercontent.com/u/116469492" width=24></a> DSV - Scripts

[![Release](https://img.shields.io/github/v/tag/DiverseStardewValley/Scripts?label=Release&style=flat-square)](https://github.com/DiverseStardewValley/Scripts/tags)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-blue?style=flat-square)](https://github.com/DiverseStardewValley/Scripts/blob/main/pyproject.toml)
[![Build](https://img.shields.io/github/workflow/status/DiverseStardewValley/Scripts/CI?label=Build&style=flat-square)](https://github.com/DiverseStardewValley/Scripts/actions/workflows/ci.yml)
[![CodeQL](https://img.shields.io/github/workflow/status/DiverseStardewValley/Scripts/CodeQL?label=CodeQL&style=flat-square)](https://github.com/DiverseStardewValley/Scripts/actions/workflows/codeql.yml)
[![CodeFactor](https://img.shields.io/codefactor/grade/github/DiverseStardewValley/Scripts/main?label=CodeFactor&style=flat-square)](https://www.codefactor.io/repository/github/diversestardewvalley/scripts)

Various Python scripts to help manage the Diverse Stardew Valley mod and its
many files.

While these scripts are/were developed primarily with DSV's use cases in mind,
they can be quite handy for general purposes too - and they're fairly easy for
anyone to set up and use!

## Requirements

- `git` - https://git-scm.com/downloads
- `python` (version **3.10** or higher) - https://www.python.org/downloads/
- `pip` (usually auto-installed with Python) -
  https://pip.pypa.io/en/stable/installation/
- Basic familiarity with the
  [terminal or "command line"](https://developer.mozilla.org/en-US/docs/Learn/Tools_and_testing/Understanding_client-side_tools/Command_line#welcome_to_the_terminal)
  on your system

## Installation

If you just want to **use** these scripts, this command will work for initial
installation as well as subsequent updates:

```
pip install -U git+https://github.com/DiverseStardewValley/Scripts.git
```

<details>
<summary>
However, if you want to play around with the code (and maybe contribute your own
script!) - you'll most likely want to use these steps instead...
<i>(click to expand)</i>
</summary>

### Editable/Development Installation

1. First,
   [clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)
   this repository (i.e. download the code).

   ```
   git clone https://github.com/DiverseStardewValley/Scripts.git
   ```

2. Then,
   [change directory](https://tutorials.codebar.io/command-line/introduction/tutorial.html#cd-or-change-directory)
   into the one you just cloned.

   ```
   cd Scripts
   ```

3. Lastly,
   [install](https://packaging.python.org/en/latest/tutorials/installing-packages/#installing-from-a-local-src-tree)
   the Python package contained in that directory.

   ```
   pip install -e .
   ```

**Note:** The `-e` flag indicates an
[editable install](https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs),
which means that any changes you make to the code will immediately take effect
when you run the program locally.

</details>

## Usage

Once you've installed this package, you can view its help menu by using this
command from any directory:

```
dsv-scripts
```

<details>
<summary>
If everything was set up correctly, you should see something like this...
<i>(click to expand)</i>
</summary><br>

```
┌────────────────────────────────────────────────────────────────────┐
│              _                            _       _                │
│           __| |_____   __   ___  ___ _ __(_)_ __ | |_ ___          │
│          / _` / __\ \ / /__/ __|/ __| '__| | '_ \| __/ __|         │
│         | (_| \__ \\ V /___\__ \ (__| |  | | |_) | |_\__ \         │
│          \__,_|___/ \_/    |___/\___|_|  |_| .__/ \__|___/         │
│                                            |_|   v0.1.3            │
│                                                                    │
│   Various scripts to help manage the Diverse Stardew Valley mod.   │
│                                                                    │
│  Command              Description                                  │
│  minify-json          Saves minified copies of JSON/JSON5 files.   │
│  remove-blank-lines   Removes blank lines in text-based files.     │
│  tinify-pngs          Saves compressed copies of PNG images.       │
└────────────────────────────────────────────────────────────────────┘
```

</details>

Just like the primary `dsv-scripts` command, all of the additional listed
commands can be used from any directory. To see more information about a command
or script, use its `-h` option (for example, `minify-json -h`).

## Git Hooks

Most of these scripts can also be installed as
[pre-commit](https://github.com/pre-commit/pre-commit) hooks for seamless
integration into your workflow. (If you're unfamiliar with pre-commit, here's
its [quickstart](https://pre-commit.com/index.html#quick-start) guide. Highly
recommend it for any project!)

When your `.pre-commit-config.yaml` is ready, simply add this repo and the hooks
you want to use. For example:

```yaml
- repo: https://github.com/DiverseStardewValley/Scripts
  rev: 0.1.3
  hooks:
    - id: minify-json
      args: ["--input=src", "--output=pkg"]
    - id: remove-blank-lines
      files: ^src/.+\.json$
```

## Contributing

Contributions to this repository are always encouraged and very much
appreciated! If you think something in the documentation should be clarified, or
if you have an idea for a script that would be useful, you're more than welcome
to open a pull request. 💗

For general information about contributing to DSV, check out our
[contributing guidelines](https://github.com/DiverseStardewValley/.github/blob/main/.github/contributing.md).

## License

Copyright © 2022 [The DSV Team](https://github.com/DiverseStardewValley).
Released under the
[BSD 3-Clause License](https://github.com/DiverseStardewValley/Scripts/blob/main/LICENSE).
