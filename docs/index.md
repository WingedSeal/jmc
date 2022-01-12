# Documentation

Welcome! This is the official documentation for JMC.
JavaScript-like Minecraft functions

- [Warnings](warnings.md)
- [Syntax](syntax.md)
- [Features](features.md)

## Example Code

```JavaScript
function deathMessage() {
    tellraw @a [{"text":"Someone died again!", "color": "gold"}];
    tellraw @a $deathCount.toString(color="red", bold=true);
}

function kill() {
    $deathCount += 1;
    kill @s;
    deathMessage();
}

function __tick__() {
    // Anything here will be called every tick
    execute
        as entity @a[tag=my_tag]
        run kill();
}

# Hastag comments still works
// Anything here will be called on load
$deathCount = 0; // You can also put comment here
```

Will be compiled to:

**__load__.mcfunction**

```elixir
scoreboard objectives add __variable__ dummy
scoreboard objectives add __int__ dummy
scoreboard players set 1 __int__ 1

scoreboard players set $deathCount __variable__ 0
```

**__tick__.mcfunction**

```elixir
execute as entity @a[tag=my_tag] run function <namespace>:kill
```

**kill.mcfunction**

```elixir
scoreboard players operation $deathCount __variable__ += 1 __int__
kill @s
function <namespace>:deathmessage
```

**deathmessage.mcfunction**

```elixir
tellraw @a [{"text":"Someone died again!", "color": "gold"}]
tellraw @a {"score":{"name":"$deathCount","objective":"__variable__"}, "color":"red", "bold":"true"}
```
