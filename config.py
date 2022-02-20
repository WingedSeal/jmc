def set_configs(content: dict):
    global configs
    configs = content

class JMCSyntaxError(ValueError):
    def __init__(self, text: str, *args: object) -> None:
        self.text = text
        super().__init__(*[text, *args])