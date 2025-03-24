from pathlib import Path

class DirectoryManager:
    def __init__(self, start_path: str = __file__):
        self.root = self._find_project_root(Path(start_path).resolve())
        self._directories = {
            'data': self.root / 'data',
            'raw': self.root / 'data' / 'raw',
            'test': self.root / 'data' / 'test',
            'logs': self.root / 'logs',
        }
        self._ensure_directories()

    def _find_project_root(self, current: Path) -> Path:
        for parent in [current] + list(current.parents):
            if (parent / 'pyproject.toml').exists():
                return parent
        raise FileNotFoundError("Could not find pyproject.toml — is this inside a proper project?")

    def _ensure_directories(self):
        for path in self._directories.values():
            path.mkdir(parents=True, exist_ok=True)

    def data(self): return self._directories['data']
    def raw(self): return self._directories['raw']
    def test(self): return self._directories['test']
    def logs(self): return self._directories['logs']

    def custom(self, name):
        if name not in self._directories:
            path = self.root / name
            path.mkdir(parents=True, exist_ok=True)
            self._directories[name] = path
        return self._directories[name]

# 🧠 Singleton instance
directory = DirectoryManager(__file__)
