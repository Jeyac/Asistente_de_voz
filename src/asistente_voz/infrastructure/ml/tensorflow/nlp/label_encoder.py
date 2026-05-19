"""Codificación de etiquetas de intención."""
import json
from pathlib import Path

class LabelEncoder:
    """Mapea nombres de intención a índices numéricos."""

    def __init__(self, labels: list[str] | None=None) -> None:
        """Inicializa la instancia."""
        self._labels: list[str] = []
        self._label_to_index: dict[str, int] = {}
        if labels:
            self.fit(labels)

    @property
    def labels(self) -> list[str]:
        """Función labels."""
        return list(self._labels)

    @property
    def num_classes(self) -> int:
        """Función num classes."""
        return len(self._labels)

    def fit(self, labels: list[str]) -> None:
        """Función fit."""
        unique_labels = sorted(set(labels))
        self._labels = unique_labels
        self._label_to_index = {label: index for index, label in enumerate(unique_labels)}

    def encode(self, labels: list[str]) -> list[int]:
        """Función encode."""
        return [self._label_to_index[label] for label in labels]

    def decode(self, index: int) -> str:
        """Función decode."""
        return self._labels[index]

    def save(self, path: Path) -> None:
        """Guarda datos o artefactos en disco."""
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {'labels': self._labels}
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')

    @classmethod
    def load(cls, path: Path) -> 'LabelEncoder':
        """Carga datos o artefactos desde disco."""
        payload = json.loads(path.read_text(encoding='utf-8'))
        labels = payload.get('labels', [])
        encoder = cls()
        encoder.fit(labels)
        return encoder
