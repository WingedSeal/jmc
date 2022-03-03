from jmc import tokenizer

with open("test.jmc", "r") as f:
    test = f.read()

e = tokenizer.Tokenizer(test, "test.jmc")
e.parse_func_args(e.programs[0][0])
