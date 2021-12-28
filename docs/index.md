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
    tellraw @a $deathCount.toString(color=red, bold=true);
}

function kill() {
    $deathCount += 1;
    kill @s;
    deathMessage();
}

function __tick__() {
    # Anything here will be called every tick
}

# Hastag comments still works
// Anything here will be called on load
$deathCount = 0; // You can also put comment here
execute as entity @a[tag=my_tag] run kill();
```
