# JMC &middot; [![license-mit](https://badgen.net/badge/license/MIT/blue/)](https://github.com/WingedSeal/jmc/blob/main/LICENSE) [![release](https://badgen.net/badge/release/v1.2.16-alpha.1/blue/)](https://github.com/WingedSeal/jmc/releases/latest) [![build-passing](https://badgen.net/badge/build/passing/green/)](https://wingedseal.github.io/jmc/#/) [![discord-invite](https://badgen.net/badge/discord/Official-Server/blue/?icon=discord)](https://discord.gg/PNWKpwdzD3)

## (JavaScript-like Minecraft Function)

JMC (JavaScript-like Minecraft Function) is a mcfunction extension language for making Minecraft Datapack.

![JMC-icon](https://github.com/WingedSeal/jmc/blob/webpage/src/assets/image/jmc_icon192.png?raw=true)

### Code example:

```js
Text.tellraw(@a, "everything outside the function");
say "just goes into the load function";

function myFunc() { // function
    execute as @a at @s run {
        Text.tellraw(@a, "&<green,bold> this text is green and bold");
        say "this is a function executed through execute as @a";
    }
}
function varOperations() {
    // this variable x is equal to the number of items in hand ;
    $x = data get entity @s SelectedItem.Count;
    $y = 100; // this is the second variable
    $random_int = Math.random($x, $y);
    Text.tellraw(@a, "random number from &<$x> to 100: &<$random_int>");
}
class folder {
    function funcInFolder() {
        if ($x < $y && $random_int <= 50) {
            printf("X is less than Y and random number is less than or equal to 50");
        } else if ($y > $x || $x == 69) {
            printf("X is greater than Y or X is equal to 69");
        } else {
            printf("X and Y are equal"); // "printf" is shortcut for "tellraw @a"
        }
    }
}
function folder.switchCase() {
    folder.funcInFolder();
    switch ($random_int) { // optimized with binary search trees
        case 1:
            printf("$random_int is equal to 1");
        case 55:
            printf("$random_int is equal to 55");
    }
}
```

**Documentation:** <https://jmc.wingedseal.com>

**Trailer:** <https://www.youtube.com/watch?v=cFgvCScpirw&ab_channel=WingedSeal>

---

## Why use JMC?

-   Avoid repetitive tasks
-   Superior Syntax
-   Low learning curve
-   Many more features

JMC allows you to write minecraft functions in a better language (.jmc) which is more readable and easier to write.

## Documentation

Everything you need to know about JMC can be found at <https://jmc.wingedseal.com>

## Installation

-   **Executable**

In "datapacks" folder of your world file (Usually `.minecraft/saves/world_name/datapacks`). Create a new datapack folder. And put JMC.exe in that folder then run it.

![Installation](https://github.com/WingedSeal/jmc/blob/webpage/src/assets/image/installation/file_location.png?raw=true)

-   **Python 3.10+**

```bash
pip install jmcfunction --pre
```

## Build

### Executable

If you would like to build the executable yourself (on Windows).

1. Install [Python 3.10](https://www.python.org/downloads/release/python-3108/)
2. Install [GNU compiler](https://gcc.gnu.org)
3. Open command prompt as administrator
4. Go to repository directory using `cd`
5. Run `pip install -r build_requirements.txt`
6. Run `build`

### Python

If you would like to use latest unreleased feature, you can install jmc directly from github repository.

1. Install [Python 3.10](https://www.python.org/downloads/release/python-3108/)
2. Open a terminal (command prompt as administrator on Windows)
3. Go to repository directory using `cd`
4. Run `cd ./src`
5. Run `pip install setuptools`
6. Run `python setup.py install`

## License

[MIT](https://github.com/WingedSeal/jmc/blob/main/LICENSE)
