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

### 1. Variable Declaration
- Initialize a variable (Set to 0, if doesn't exist)

```javascript
let $<variable>;
```

Output: 

```elixir
scoreboard players add $<variable> __variable__ 0
```

### 2. Variable Assignment
- You are allowed to assign variable without declaring.

```javascript
$<variable> = <integer>;
```

Output: 

```elixir
scoreboard players set $<variable> __variable__ <integer>
```

### 3. Variable Operations
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

### 4. Incrementation/Decrementation
- `$<variable>++` is `$<variable> += 1`
- `$<variable>--` is `$<variable> -= 1`

## Function

### 1. Function Definition
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
**Example:**

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

### 2. Function Calling
- You **can't** pass any argument.
- Any capital letter (which is invalid for minecraft function name) will be automatically be turn into lower case, which means it is not case sensitive. For example, `deathMessage()` is the same as `deathmessage()`

```javascript
[<directory>.]<file_name>();
```

Output:

```javascript
function namespace:[<directory>/]<file_name>
```

**Example:**

```javascript
execute as @a run utils.chat.spamChat();
```

Output:

```javascript
execute as @a run function namespace:utils/chat/spamchat
```

### 3. Function Grouping
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

## Flow controlling

### 1. Condition
- Use for other flow controls / `execute if`
- Can replace any `<condition>`
- `==` and `=` do exactly the same thing

```javascript
$<variable> (>=|<=|=|==|>|<) <integer>
$<variable> (>=|<=|=|==|>|<) <variable> 
$<variable> (==|=) [<integer>]..[<integer>]
```

**Example:**

```javascript
if ($deathCount>5) {
    say "Too many death!"
}
```

### 2. If, Else
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

**Example:**

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



### 3. While loop
- You can accidentally cause infinite recursion in while loop. Be extremely aware of that.

```javascript
while (<condition>) {
    <command>;
    <command>;
    ...
} 
```

Output:
`__load__.mcfunction`
```elixir
execute if <condition> run function namespace:__private__/while_loop/0
```

`__private__/while_loop/0.mcfunction`
```elixir
<command>;
<command>;
...
execute if <condition> run function namespace:__private__/while_loop/0
```

### 4. For loop
- You can accidentally cause infinite recursion in for loop. Be extremely aware of that.
- `let $<variable> = <integer>` is executed (one time) before the execution of the code block.
    - The first statement **must be** variable declaring and nothing else.
- `<condition>` defines the condition for executing the code block.
- `<statement>` is executed (every time) after the code block has been executed.
- `$<variable>` is no local scope. You cannot access this outside the loop, and global variable with the same name will get overridden.

```javascript
for (let $<variable> = <integer>; <condition>; <statement>) {
  <command>;
  <command>;
  ...
}
```

Output:

`__load__.mcfunction`
```elixir
scoreboard players set $__private__.<variable> __variable__ <integer>
execute if <condition> run function namespace:__private__/for_loop/0
```
`__private__/for_loop/0.mcfunction`
```elixir
<command>;
<command>;
...
<statement>
execute if <condition> run function namespace:__private__/for_loop/0
```

**Example:**

```javascript
for (let $i=1; $i<=10; $i++) {
    tellraw @a $i.toString(color="gold");
}
```

Output:

`__load__.mcfunction`
```elixir
scoreboard players set $__private__.i __variable__ 1
execute if score $__private__.i __variable__ matches ..10 run function namespace:__private__/for_loop/17
```

`__private__/for_loop/17.mcfunction`
```elixir
tellraw @a {"score":{"name":"$__private__.i","objective":"__variable__"},"color":"gold"}
scoreboard players operation $__private__.i __variable__ += 1 __int__
execute if score $__private__.i __variable__ matches ..10 run function namespace:__private__/for_loop/17
```

This will cause the minecraft to tellraw 1 to 10 in chat.

## Built-in functions

### 1. toString
    - Turn variable into json for display (tellraw, title, etc.)
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

### ~~2. Timer~~ (Not done)
- Automatically make a scoreboard timer for you. (If you need global timer, `/schedule` is a better option)
- `Timer.add(name, runMode, function, entity = @a)`
    - Only call this outside a function
    - Create new timer
    - name:
        - Name of the timer. It exists so that you can access the timer
        - Be less than or equal to 11 characters long
        - Word charactors or underscores `_` only

    - runMode:
        - `None` Doesn't do anything after timer is over
        - `runOnce` Run exactly once after timer is over
        - `runTick`  Run every tick after timer is over
    - function:
        - `<execute_arguments>` is optional, it's for `as`, `if`, `at` etc.
        - function is automatically run as the entity that its timer is over
        ```javascript
        <execute_arguments> {
            <command>;
            <command>;
            ...
        }
        ```
    - entity:
        - An optional target selector for timer, defaults at `@a`
        - Can add extra keys and arguments

    Output:

    `__load__.mcfunction`
    ```elixir
    scoreboard objectives add timr.<name> dummy
    ```

    `__tick__.mcfunction` if `runMode` is `runTick`
    ```elixir
    scoreboard players remove <entity>[scores={timr.<name>=1..}] 1
    execute as <entity>[scores={timr.<name>=0}] <execute_arguments> run function namespace:__private__/timer/0
    ```

    `__tick__.mcfunction` if `runMode` is `runOnce`
    ```elixir
    scoreboard players remove <entity>[scores={timr.<name>=0..}] 1
    execute as <entity>[scores={timr.<name>=0}] <execute_arguments> run function namespace:__private__/timer/0
    ```

    `__tick__.mcfunction` if `runMode` is `None`
    ```elixir
    scoreboard players remove <entity>[scores={timr.<name>=1..}] 1
    ```
    `__private__/timer/0.mcfunction` if `runMode` is `runTick` or `runOnce`
    ```elixir
    <command>;
    <command>;
    ...
    ```

- `Timer.set(name, tick, target)`
    - Set entity's timer
    - name:
        - Name of the timer when you did `Timer.add`
    - tick:
        - Amount of tick before timer is over.
    - target:
        - Target selector that you want to set its timer

    Output:

    ```elixir
    scoreboard players set <target> timr.<name> <tick>
    ```

- `Timer.isOver(name, target)`
    - A condition, must be used after `execute if` or anything that compiles down to `execute if`

    Output:

    ```elixir
    score <target> timr.<name> matches ..0
    ```

- `Timer.selector(name)`

    Output:

    ```
    scores={timr.<name>=..0}
    ```

- `Timer.toSecond(name, $variable, target)`

    - Store timer left into a variable
    Output:

    ```elixir
    scoreboard players operation __tmp__ __variable__ = <target> timr.<name>
    scoreboard players operation __tmp__ /= 20 __int__
    scoreboard players operation $variable __variable__ = __tmp__ __variable__
    ```

***Example:***

```javascript
function useAbility() {
    if (Timer.isOver(cooldown, @s)) {
        ability();
        tellraw @s "You used your ability";
        Timer.set(cooldown, 100, @s);
    } else {
        Timer.toSecond(cooldown, $timer.cooldown, @s);
        tellraw @s [$timer.cooldown.toString(color="red"), "text":" seconds left"];
    }
}

Timer.add(cooldown, runOnce, @a[team=A] {
    tellraw @s "Your ability is ready!";
}, @a[tag=A])
```

Output:

`__load__.mcfunction`
```elixir
scoreboard objectives add timr.cooldown dummy
```

`__tick__.mcfunction`
```elixir
scoreboard players remove @a[tag=A,scores={timr.cooldown=0..}] 1
execute as @a[team=A,scores={timr.cooldown=0}] run function namespace:__private__/timer/0
```

`__private__/timer/0.mcfunction`
```elixir
tellraw @s "Your ability is ready!"
```

`useability.mcfunction`
```elixir
scoreboard players set __tmp__ __variable__ 0
execute if score @s timr.cooldown matches ..0 run function namespace:__private__/if_else/0
execute if score __tmp__ __variable__ matches 0 run function namespace:__private__/if_else/1
```

`__private__/if_else/0.mcfunction`
```elixir
scoreboard players set __tmp__ __variable__ 1
function namespace:ability
tellraw @s "You used your ability"
scoreboard players set @s timr.cooldown 100
```

`__private__/if_else/1.mcfunction`
```elixir
scoreboard players set __tmp__ __variable__ 1
scoreboard players operation __tmp__ __variable__ = @s timr.cooldown
scoreboard players operation __tmp__ /= 20 __int__
scoreboard players operation $timer.cooldown __variable__ = __tmp__ __variable__
tellraw @s [{"score":{"name":"$timer.cooldown","objective":"__variable__"},"color":"red"},"text":"seconds left"]
```

### ~~3. RightClickDetection~~ (Not done)
- `RCdetect.init()`

### ~~4. HitboxDetection~~ (Not done)
- `Hibox.detect(size, target_selector)`
- `execute as Hixbox.detect(0.01, @a)`

### ~~5. Raycast~~ (Not done)
```javascript
Raycast.entity.setUp()
```
```javascript
Raycast.block.setUp()
```
```
Raycast.cast(name)
```

### ~~6. EntityLauncer~~ (Not done)