from abc import ABC, abstractmethod
from collections import deque
import numpy as np
from typing import TypeVar

ActType = TypeVar("ActType")
ObsType = TypeVar("ObsType")
BUFFER_SIZE = 50


class BaseAgent(ABC):
    def __init__(self, data, buffer_size=None):
        self.data = data
        if buffer_size:
            self.buffer = deque(maxlen=buffer_size)
        else:
            self.buffer = deque(maxlen=BUFFER_SIZE)

    @abstractmethod
    def take_action(self, state: ObsType):
        raise NotImplementedError("should be implemented in the derived class !")
    

    