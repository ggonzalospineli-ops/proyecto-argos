"""Carga aislada de los proyectos hermanos `vision/` y `comms/`.

Ambos proyectos son standalone y cada uno usa internamente `import src...`
y `from config import ...` asumiendo que SU PROPIA raiz esta al principio
de sys.path (asi es como corren sus propios scripts/tests). Eso es comodo
para desarrollarlos por separado, pero si los importamos a los dos en el
mismo proceso Python, el segundo "gana" el nombre `src`/`config` en
sys.modules y el primero queda pisado.

En vez de reescribir las importaciones internas de vision/ y comms/ (que
ya estan probadas con sus propios tests), este modulo aisla cada import:
antes de entrar a un bloque `with isolated_project(root):` limpia
cualquier `src`/`config` cacheado de un proyecto hermano, y al salir hace
lo mismo, para que el siguiente proyecto importe su propia version limpia.
Los objetos ya importados (clases, funciones) quedan como referencias
normales de Python y no se ven afectados por la limpieza del cache.
"""

from __future__ import annotations

import sys
from contextlib import contextmanager
from pathlib import Path

_SHARED_TOP_LEVEL_NAMES = ("src", "config")


def _purge_cached_modules() -> None:
    for name in list(sys.modules):
        if name in _SHARED_TOP_LEVEL_NAMES or any(
            name.startswith(f"{n}.") for n in _SHARED_TOP_LEVEL_NAMES
        ):
            del sys.modules[name]


@contextmanager
def isolated_project(root: Path):
    root_str = str(root)
    _purge_cached_modules()
    sys.path.insert(0, root_str)
    try:
        yield
    finally:
        if root_str in sys.path:
            sys.path.remove(root_str)
        _purge_cached_modules()
