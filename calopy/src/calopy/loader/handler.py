from abc import abstractmethod


class Handler:
    @abstractmethod
    def parsedData(self):
        pass

    @abstractmethod
    def handle(self, line):
        pass
