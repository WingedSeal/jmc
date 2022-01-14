# Documentation

Welcome! This is the official documentation for JMC.
JavaScript-like Minecraft functions.

Make sure to read the warning before coding!

- [Warnings](warnings.md)
- [Syntax](syntax.md)
- [Features](features.md)

## Example Code

```javascript
function deathMessage() {
    if (score $deathCount __variable__ matches ..5) {
        tellraw @a [{"text":"Someone died again!", "color": "gold"}];
        tellraw @a $deathCount.toString(color="red", bold=true);
    } else if (score $deathCount __variable__ matches 5..15) {
        tellraw @a "A lot of people died.";
    } else {
        tellraw @a "Too many people died.";
    }
}

function kill() {
    $deathCount += 1;
    tag @s remove dying;
    kill @s;
    deathMessage();
}

function __tick__() {
    // Anything here will be called every tick
    execute
        as @a[tag=dying]
        run kill();
}

# Hastag comments still works
// Anything here will be called on load
int $deathCount; // You can also put comment here
```

**Will be compiled to:**

`__private__/if_else/0.mcfunction`
```elixir
scoreboard players set __tmp__ __variable__ 1
tellraw @a [{"text":"Someone died again!", "color": "gold"}]
tellraw @a {"score":{"name":"$deathCount","objective":"__variable__"},"color":"red","bold":true}
```
`__private__/if_else/1.mcfunction`
```elixir
scoreboard players set __tmp__ __variable__ 1
tellraw @a "A lot of people died."
```
`__private__/if_else/2.mcfunction`
```elixir
scoreboard players set __tmp__ __variable__ 1
tellraw @a "Too many people died."

```
`__load__.mcfunction`
```elixir
scoreboard objectives add __int__ dummy
scoreboard objectives add __variable__ dummy
scoreboard players set 1 __int__ 1

scoreboard players add $deathCount __variable__ 0
```
`__tick__.mcfunction`
```elixir
execute as @a[tag=dying] run function mydatapack:kill
```
`deathmessage.mcfunction`
```elixir
scoreboard players set __tmp__ __variable__ 0
execute if score $deathCount __variable__ matches ..5 run function mydatapack:__private__/if_else/0
execute if score __tmp__ __variable__ matches 0 if score $deathCount __variable__ matches 5..15 run function mydatapack:__private__/if_else/1
execute if score __tmp__ __variable__ matches 0 run function mydatapack:__private__/if_else/2
```
`kill.mcfunction`
```elixir
scoreboard players operation $deathCount __variable__ += 1 __int__
tag @s remove dying
kill @s
function mydatapack:deathmessage
```