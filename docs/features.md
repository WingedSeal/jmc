# Import
- [x]
Literally move context of another jmc file to the **top** of the main file.
Warning: Importing **doesn't** add extra namespace
Syntax:
```javascript
@import '[<directory>/]<file_name>';
```
Will copy the context inside [<directory>/]<file_name>.jmc to main jmc.
Example:
```javascript
@import 'lib/math';
```

# Multiline Command
- [x]
You are allowed to split a single command into multiple line, with a cost of adding semicolons (`;`) at the end of every command (required).

Example:
```elixir
execute
    as @a
    at @s
    run playsound
        entity.wither.spawn
        master
        @s
        ~ ~ ~
        1 2;
```

# Comment 
- [x]
Syntax:
- `#`
- `//`

You are allowed to put comment at the end of the line.
Example:
```elixir
#comment
function tellraw_message() {
    tellraw @a "Message"; //comment
}
```

# Load/Tick
- [x]
- Any commands outside a function will be automatically put into `__load__.mcfunction`
- Generate `load.json` with a value of `__load__.mcfunction`
- Generate `tick.json` with a value of `__tick__.mcfunction`

# Custom Syntax


## Variable
- [ ] **1. Variable Declaration** (Not done)
```javascript
$<variable>;
```
Output: 
```elixir
scoreboard players add $<variable> __variable__ 0
```

- [x] **2. Variable Assignment**
```javascript
$<variable> = <integer>;
```
Output: 
```elixir
scoreboard players set $<variable> __variable__ <integer>
```

- [x] **3. Variable Operations**
    - operations:
        - "+=" Addition: Add source's score to target's score
        - "-=" Subtraction: Subtract source's score from target's score
        - "*=" Multiplication: Set target's score to the product of the target's and source's scores
        - "/=" (Integer) Division: Divide target's score by source' scores, and the result will be rounded down to an integer.
        - "%=" Modulus: Divide target's score by source's score, and use the positive remainder to set the target score
```javascript
$<variable: target> <operations> ($<variable: source>|<integer>);
```
Output: 
```elixir
scoreboard players operations <target> __variable__ <operations> <source> __variable__
```
```elixir
scoreboard players operations <target> __variable__ <operations> <integer> __int__
```

## Function

- [x] **1. Function Definition**
    - You **can't** pass any parameter.
    - Arrow function **doesn't** work.
    - Any capital letter (which is invalid for minecraft function name) will be automatically be turn into lower case, which means it is not case sensitive. For example, `deathMessage` will override `deathmessage`
```javascript
function [<directory>.]<file_name>() {
    <command>;
    <command>;
    ...
}
```
Output:
`[<directory>/]<file_name>.mcfunction`
```javascript
<command>;
<command>;
...
```
Example:
```javascript
function utils.chat.spamChat() {
    tellraw @a "SPAM 1";
    tellraw @a "SPAM 2";
    tellraw @a "SPAM 2";
}
```
Output:
`utils/chat/spamchat.mcfunction`
```javascript
tellraw @a "SPAM 1"
tellraw @a "SPAM 2"
tellraw @a "SPAM 2"
```

- [x] **2. Function Calling**
    - You **can't** pass any argument.
    - Any capital letter (which is invalid for minecraft function name) will be automatically be turn into lower case, which means it is not case sensitive. For example, `deathMessage()` is the same as `deathmessage()`
```javascript
[<directory>.]<file_name>();
```
Output:
```javascript
function namespace:[<directory>/]<file_name>
```

Example:
```javascript
execute as @a run utils.chat.spamChat();
```
Output:
```javascript
execute as @a run function namespace:utils/chat/spamchat
```

- [x] **3. Function Grouping**
    - The syntax uses `class` but it is **not** a real "class".
    - Will add extra layers of directory/namespace to any function inside it.
    - Doesn't affect normal commands inside it.
    - Do **not** stack classes on top of each other (class inside class inside class...)
```javascript
class [<directory>.]<folder_name> {
    function [<directory>/]<file_name>() {
        <command>
        <command>
        ...
    }
    <command>
    <command>
    ....
}
```
Output:
`__load__.mcfunction`
```javascript
<command>
<command>
...
```
`[<directory>/]<folder_name>/[<directory>/]<file_name>.mcfunction`
```javascript
<command>
<command>
....
```
*For now, I don't recommend using "class".*

## Flow controlling (Not done)

- [ ] **1. If, Else**
- [ ] **2. While loop**
- [ ] **3. For loop**

## Built-in functions

- [x] **1. toString**
    - turns variable into json for display (tellraw, title, etc.)
```javascript
$<variable>.toString([<key>=(<value>|"<value>")])
```
Output
```json
{"score":{"name":"$<variable>","objective":"__variable__"},"key":(<value>|"<value>")}
```
Example:
```javascript
$deathCount.toString(color="red", bold=true)
```
Output
```json
{"score":{"name":"$deathCount","objective":"__variable__"},"color":"red","bold":true}
```

---
**BLOW THIS IS UNDER CONSTRUCTION**
- [ ] **2. Timer** (Not done)
    - addTimer(name, runMode, function)
        - None
        - runOnce
        - runTick
    - setTimer(name, tick, target)
    - isTimerOver(name, target) # Must be after `execute if`
NOTE
```
addTimer(
    name = "test",
    runMode = None
)


addTimer(
    name = "cooldown",
    runMode = runOnce,
    function = {
        say "Cooldown Over"
    }
)

setTimer(
    name = "cooldown"
    tick = 200,
    target = @s
)

tick:
execute as @a if isTimeOver(name="cooldown", taret=@s) say "EVERYTICK SINCE OVER"
```