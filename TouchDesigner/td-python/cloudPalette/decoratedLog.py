class DecoratedLog:

    def __init__(self, logDecorator: str):
        self.display = True
        self._log_decorator = logDecorator

    def log_to_textport(self, msg: str, includeDecorator: bool = True) -> None:
        if self.display:
            if includeDecorator:
                print(f'{self._log_decorator} | {msg}')
            else:
                print(f'{msg}')

        else:
            pass
