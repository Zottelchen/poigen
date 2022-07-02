class FilterResult:
    def __init__(self, result_type: str, hint: str | None = None):
        self.result_type = result_type
        self.hint = hint

    def __str__(self):
        return f"{self.result_type}"

    def long_output(self):
        return f"{self.result_type}{': '+self.hint if self.hint is not None else ''}"


class EmptyFilterResult:
    def __init__(self):
        pass
