from jmc import tokenizer
from pprint import pprint

with open("test.jmc", "r") as f:
    test = f.read()

e = tokenizer.Tokenizer(test, "test.jmc")
pprint(e.programs)
