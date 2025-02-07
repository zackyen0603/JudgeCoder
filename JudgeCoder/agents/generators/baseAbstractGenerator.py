from abc import ABC, abstractmethod

class CommandGenerator(ABC):
    """
    Abstract base class for all command generators.
    """

    @abstractmethod
    def generate(self, instruction: str, max_tokens: int = 100) -> str:
        """
        Generate output based on the given instruction.
        
        :param instruction: The instruction or prompt to generate output for.
        :param max_tokens: The maximum number of tokens to generate.
        :return: Generated output as a string.
        """
        pass
