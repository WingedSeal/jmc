from ..tokenizer import TokenType, Tokenizer, Token
from ..exception import JMCSyntaxException

NEW_LINE = '\n'


def parse_condition(token: Token, tokenizer: Tokenizer) -> tuple[str, str]:
    """Return `if ...` and pre-commands with newline
Example:
```py
condition1, precommands1 = parse_condition(...)
condition2, precommands2 = parse_condition(...)
commands = [
    f"{precommands1}execute {condition1} run {datapack.add_private_function("if_else", token, tokenizer)}",
    f"{precommands2}execute unless ... {condition2} run {datapack.add_private_function("if_else", token, tokenizer)}",
]
return datapack.add_raw_private_function("if_else", commands)
```
"""

    #TODO: IMPLEMENT
"""
[(entity @s&&(entity @e || entity @a))]
// replace `&&` outside string with ` && `
[(entity @s && (entity @e || entity @a))]
// tokenize parenthesis
[entity, @s, &&, (entity @e || entity @a)]
// find `||`
// find `&&`
[entity, @s] , [(entity @e || entity @a)]
// left : found nothing -> turns into string
// right: recursion
"entity @s" , [(entity @e || entity @a)]

[(entity @e || entity @a)]
[entity, @e, ||, entity, @a]
// left : found nothing -> turns into string
// right : found nothing -> turns into string
{
    "operator": "&&",
    "left": "entity @s",
    "right": {
        "operator": "||",
        "left": "entity @e",
        "right": "entity @a"
    }
}

"""
