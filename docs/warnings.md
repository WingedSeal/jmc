# Warnings

- At the moment, JMC does **not** have any syntax checking, which mean any syntax error will result in broken datapacks

- `jmc_tick.mcfunction` and `jmc_load.mcfunction` are reserved for compiled code.
- Following scoreboard objectives are reserved for compiled JMC only. If you use one of these objective names something might break.
  1. `__int__`
  2. `__variable__`
  3. `__tmp__`
