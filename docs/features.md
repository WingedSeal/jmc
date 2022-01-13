# Import

Literally move context of another jmc file to the **top** of the main file.
Warning: Importing **doesn't** add extra namespace
Syntax:
```javascript
@import '[<directory>/]<file_name>';
```
Will copy the context inside `[<directory>/]<file_name>.jmc` to main jmc.
Example:
```javascript
@import 'lib/math';
```

# Multiline Command

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
    
- Any commands outside a function will be automatically put into `__load__.mcfunction`
- Generate `load.json` with a value of `__load__.mcfunction`
- Generate `tick.json` with a value of `__tick__.mcfunction`

# Custom Syntax

## Variable
- [x] **1. Variable Declaration**
    - Initialize a variable (Set to 0, if doesn't exist)
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
        - "=" Assign: Set target's score to source's score *(for variable)*
        - "+=" Addition: Add source's score to target's score
        - "-=" Subtraction: Subtract source's score from target's score
        - "*=" Multiplication: Set target's score to the product of the target's and source's scores
        - "/=" (Integer) Division: Divide target's score by source' scores, and the result will be rounded down to an integer.
        - "%=" Modulus: Divide target's score by source's score, and use the positive remainder to set the target score
```javascript
$<target: variable> <operations> ($<source: variable>|<integer>);
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
        <command>;
        <command>;
        ...
    }
    <command>;
    <command>;
    ....
}
```
Output:

`__load__.mcfunction`
```javascript
<command>;
<command>;
...
```
`[<directory>/]<folder_name>/[<directory>/]<file_name>.mcfunction`
```javascript
<command>;
<command>;
....
```
*For now, I don't recommend using "class".*

## Flow controlling (Not done)

- [ ] **1. If, Else**
    - Automatically generate anonymous function(s) with integer name.
    - Allow JavaScript's if/else syntax
    - Even if the first condition is met, the rest will still need to check a scoreboard
    - If there's only `if` and no `else`, compiler will turn it into a vanilla `execute if` command.

```javascript
if (<condition>) { 
    <command>;
    <command>;
    ...
} else if (<condition>) {
    <command>;
    <command>;
    ...
} else if (<condition>) {
    <command>;
    <command>;
    ...
} else {
    <command>;
    <command>;
    ...
}
```
Output:
```elixir
scoreboard players set __tmp__ __variable__ 0
execute if <condition> run function namespace:__private__/if_else/0
execute if score __tmp__ __variable__ matches 0 if <condition> run function namespace:__private__/if_else/1
execute if score __tmp__ __variable__ matches 0 if <condition> run function namespace:__private__/if_else/2
execute if score __tmp__ __variable__ matches 0 run function namespace:__private__/if_else/3
```
`__private__/if_else/0.mcfunction`
```elixir
scoreboard players set __tmp__ __variable__ 1
<command>;
<command>;
...
```
`__private__/if_else/1.mcfunction`
```elixir
scoreboard players set __tmp__ __variable__ 1
<command>;
<command>;
...
```
`__private__/if_else/2.mcfunction`
```elixir
scoreboard players set __tmp__ __variable__ 1
<command>;
<command>;
...
```
`__private__/if_else/3.mcfunction`
```elixir
<command>;
<command>;
...
```
Example:
```javascript
function do_i_have_tag() {
    if (entity @s[tag=my_tag]) { 
        say I have tag!;
    } else {
        say I don't have tag!;
    }
}
execute as @a[team=my_team] run do_i_have_tag();
```
Output:

`__load__.mcfunction`
```elixir
execute as @a[team=my_team] run function namespace:do_i_have_tag
```
`do_i_have_tag.mcfunction`
```elixir
scoreboard players set __tmp__ __variable__ 0
execute if entity @s[tag=my_tag] run function namespace:__private__/if_else/11
execute if score __tmp__ __variable__ matches 0 run function namespace:__private__/if_else/12
```
`__private__/if_else/11.mcfunction`
```elixir
scoreboard players set __tmp__ __variable__ 1
say I have tag!
```
`__private__/if_else/12.mcfunction`
```elixir
say I don't have tag!
```



- [ ] **2. While loop**
- [ ] **3. For loop**

## Built-in functions

- [x] **1. toString**
    - turns variable into json for display (tellraw, title, etc.)
```javascript
$<variable>.toString([<key>=(<value>|"<value>")])
```
Output:
```json
{"score":{"name":"$<variable>","objective":"__variable__"},"key":(<value>|"<value>")}
```
Example:
```javascript
$deathCount.toString(color="red", bold=true)
```
Output:
```json
{"score":{"name":"$deathCount","objective":"__variable__"},"color":"red","bold":true}
```

---
# BLOW THIS IS UNDER CONSTRUCTION*
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
