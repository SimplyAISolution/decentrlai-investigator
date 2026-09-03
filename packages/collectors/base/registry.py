from __future__ import annotations
from collections.abc import Iterable
from .collector import Collector
from .types import CollectorKind

class CollectorRegistry:
    def __init__(self) -> None:
        self._collectors: dict[CollectorKind, Collector] = {}

    def register(self, collector: Collector) -> None:
        if collector.kind in self._collectors:
            raise ValueError(f"Collector already registered: {collector.kind}")
        self._collectors[collector.kind] = collector

    def replace(self, collector: Collector) -> None:
        self._collectors[collector.kind] = collector

    def get(self, kind: CollectorKind) -> Collector:
        try:
            return self._collectors[kind]
        except KeyError as exc:
            raise KeyError(f"No collector registered for {kind}") from exc

    def available(self) -> tuple[CollectorKind, ...]:
        return tuple(self._collectors.keys())

    def register_many(self, collectors: Iterable[Collector]) -> None:
        for collector in collectors:
            self.register(collector)
