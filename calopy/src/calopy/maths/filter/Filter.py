from abc import abstractmethod


class Filter:
    @property
    def type(selfs):
        pass

    @abstractmethod
    def apply(self, dataFrame):
        pass

    @abstractmethod
    def get_parameter_text(self):
        pass
