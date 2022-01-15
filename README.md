# JavaScript-like Minecraft functions

# (JMC)

A compiler for compiling .jmc file (custom language) to minecraft datapack.
The language is _inspired_ from JavaScript. It's not exactly like JavaScript

## Why use JMC

JMC allows you to write minecraft functions in a better language (.jmc) which is more readable and easier to write.
For example, you can declare multiple function in a single file and whitespaces no longer matter which means you can split a single command into multiple line

Normal function from .mcfunction file will not works in JMC, the syntax is almost entirely different.

## Installation

### Executable Version

1. [Download JMC-compiler.exe](https://github.com/WingedSeal/jmc/releases/download/v1.0.0-beta.1/JMC-Compiler.exe) from github
1. Put **JMC-Compiler.exe** in any directory (Preferably, your datapack directory)

### Python Version

1. Download ZIP or Clone repository / Download [Source code](https://github.com/WingedSeal/jmc/archive/refs/tags/v1.0.0-beta.1.zip)
1. Create a virtual environment for python (For example, `python -m venv venv`) and activate (For example, `venv\Scripts\activate`)
1. Install libraries from requirements.txt using `pip install -r requirements.txt`
1. Run `main.py`, This will behave exactly like Executable Version (**JMC-Compiler.exe**)

If you prefer to have main.py elsewhere without moving the entire folder.
Create a `.py` file at the desired folder then inser the following code
```python
import sys
sys.path.append('PATH_TO_FOLDER_HERE')  # noqa
import main  # type: ignore
main.main()
```
And replace `PATH_TO_FOLDER_HERE` with pure window path to `main.py`'s parent directory you downloaded.
For example, if my `main.py`'s path is `D:/Users/User/Documents/GitHub/JMC`
```python
import sys
sys.path.append('D:/Users/User/Documents/GitHub/JMC')  # noqa
import main  # type: ignore
main.main()
```

## Usage
1. Run **JMC-Compiler.exe** and it'll automatically generate **jmc.config** in the same directory it's in
1. Edit configurations in **jmc.config** 
1. Write your jmc file(s)
1. Run **JMC-Compiler.exe** again

[Documentation](docs/index.md) (Soon TM)

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

**My Discord:** WingedSeal#0795

## Features

- Function declaration (Arrow function does not work)
- Custom variable assignment, incrementation sysntax 
- Importing other .jmc files
- Multiline command
- Build-in functions for basic datapack feature
- Grouping things in a directory using "class" declaration (Note that it's not an actual class)

## License

[MIT](https://choosealicense.com/licenses/mit/)
