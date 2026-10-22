"""Genera un HTML autocontenido, sin dependencias ni conexión a Internet."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
html = (ROOT / 'plantilla.html').read_text()
for marker, name in [('ESTILOS', 'estilos.css'), ('BANCO', 'banco.js'), ('MOTOR', 'motor.js'), ('INTERFAZ', 'interfaz.js')]:
    html = html.replace(f'/* {marker} */', (ROOT / name).read_text())
(ROOT / 'index.html').write_text(html)
print(f'HTML autónomo generado: {ROOT / "index.html"} ({len(html.encode()):,} bytes)')
