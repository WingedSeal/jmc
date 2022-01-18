# Changelog v1.1.0-alpha

### Add
- Add logic gate processing for condition (`!`, `&&`, `||`, `()`)
- Allowed nesting `class` and `function` (You still can't define function inside function)

### Changed
- `@import` now import at the line it's called instead of the top of the file
- `@import` will only works in the highest level (Outside function, class, etc.)
- Change configuration file name to `jmc_config.json`

### Fixed
- Fixed stuff inside strings/brackets triggering keywords
- Nested layers of flow controls now work properly
- Fixed whitespaces inside string being turned to spacebar

---

## Dev section

Refactor entire codebase

- Use recursion for parsing
- Use `config.py` instead of directly reading from config file in logging
- Put class, condition, for, function, if_else, while inside flow_control
- Change `PackGlobal` to `DataPack`
- Instead of giving a singleton object to every function, every function is now a method of `DataPack` instead (Completely another way around)
- Delete unnecessary import in `__init__.py`
- Use class instead of method for condition parsing
    - Use recursion to allow parsing condition with parenthesis
    - Condition now have power over keyword `if` (It can now change `execute if` to `execute unless`)
- Replace most of ` ?` with `\s*`
