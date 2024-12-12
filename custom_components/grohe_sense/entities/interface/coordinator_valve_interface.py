from abc import abstractmethod
from typing import Dict


class CoordinatorValveInterface:
    @abstractmethod
    async def set_valve(self, data_to_set: Dict[str, any]) -> Dict[str, any]:
        raise NotImplementedError

    @abstractmethod
    async def get_valve_value(self) -> Dict[str, any]:
        raise NotImplementedError