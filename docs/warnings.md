# Warnings

- At the moment, JMC does **not** have any syntax checking, which mean any syntax error will result in broken datapacks. Make sure you don't miss any semicolon `;`.

- `__tick__` will be called every game tick.
- `__load__` will be called once on load.

- Techically, there's no real "local scope" variable, since minecraft scoreborad doesn't allow it. But you can threat the integer defined in for loop as one.

- In for loop, if you declare a local variable with the same name as global, the local one will take priority. For example:
  ```javascript
  $i = 3;
  for (let $i = 0; $i < 5; $i++) {
    tellraw @a $i.toString();
  }
  tellraw @a $i.toString();

  Output:
  1
  2
  3
  4
  5
  3
  ```


- Follwings are reserved for JMC Compiler, you may declare `__tick__` function. But unless you understand how the compiler works and what you are doing, don't change any of these values. 
  - Function
    1. `__load__`
  - Scoreboard Objectives
    1. `__int__`
    1. `__variable__`
  - Players in `__variable__`
    1. `__tmp__`
    1. Anything starting with `$__private__`
  - Directories
    1. `__private__/if_else`
    1. `__private__/for_loop`
    1. `__private__/while_loop`

- Extra information
  - You can use the `__int__`, but do not change them.
  - `__tmp__` will be reset every time it'll be used by the compiler, just don't touch it. The data inside is uselss and if you change it, it won't last long either.
  - `__private__<var>` will be used for "for loop". If you understand what you are doing you might change or access it inside loop. (`$i` will be stored in `$__private__.i` in the following)
  ```javascript
  for (let $i = 0; $i < 5; $i++) {
    tellraw @a $i.toString();
  }
  ```

  