from typing import List, TypeVar, Generic, Optional

from .events import DomainEvent

ID = TypeVar("ID")


class Entity(Generic[ID]):
    """A base class for domain entities."""

    def __init__(self, id: Optional[ID]):
        self.id = id

    def __eq__(self, other):
        if not isinstance(other, Entity):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


E = TypeVar("E", bound=DomainEvent)


class AggregateRoot(Entity[ID], Generic[ID, E]):
    """
    A base class for aggregate roots.
    It manages a list of domain events.
    """

    def __init__(self, id: Optional[ID]):
        super().__init__(id)
        self._domain_events: List[E] = []

    @property
    def domain_events(self) -> List[E]:
        return self._domain_events

    def _add_domain_event(self, domain_event: E):
        self._domain_events.append(domain_event)

    def clear_domain_events(self):
        self._domain_events = []
