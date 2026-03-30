from datetime import datetime


class DecoratedLog:

    def __init__(self, logDecorator: str):
        self.display = True
        self._log_decorator = logDecorator

    # NOTE gemini generated function

    def get_pretty_timestamp(self):
        """Returns the current time formatted as YYYY-MM-DD | HH:MM:SS"""
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")

    def log_to_textport(self, msg: str, includeDecorator: bool = True) -> None:
        if self.display:
            if includeDecorator:
                print(
                    f'{self.get_pretty_timestamp()} | {self._log_decorator} | {msg}')
            else:
                print(f'{msg}')

        else:
            pass
