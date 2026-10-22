# Simulador CL3 · Compraventa internacional

## Acceso desde el celular

El enlace a un archivo interno de `/workspace` no es un enlace web para el teléfono. Para abrir el simulador directamente en Safari o Chrome se necesita alojar `index.html` por HTTPS.

Este repositorio contiene un sitio estático compatible con GitHub Pages. Después de subir la rama `main`, activar **Settings → Pages → Build and deployment → Deploy from a branch → main → /(root) → Save**. No es necesario contratar un servidor ni instalar dependencias. La dirección habitual del proyecto será `https://ravicunas.github.io/Simulador-Quizzes/`; solo debe considerarse disponible después de que GitHub complete la publicación y se compruebe una respuesta correcta del sitio.

El flujo `.github/workflows/pages.yml` publica automáticamente desde `main` cuando cambia `index.html`, `.nojekyll` o el propio flujo. También puede ejecutarse desde **Actions → Publicar simulador en GitHub Pages → Run workflow**. Usa las acciones oficiales de GitHub fijadas a sus commits y sube un artefacto que contiene únicamente `index.html` y `.nojekyll`. Es compatible con Pages configurado para la rama `main` o con GitHub Actions como origen. El resultado y la dirección de publicación aparecen en la ejecución de Actions.

El historial de cada celular se guarda en su propio navegador y no se sincroniza con el de la computadora. Las lecturas y los PPT originales están fuera del repositorio y no forman parte del sitio.

## Archivo autónomo

Abre **index.html** en un navegador actual con JavaScript. Es un archivo autónomo: incluye el diseño, las preguntas y el programa. No necesita instalar paquetes ni conectarse a Internet. En este entorno, Chromium permite la validación mediante HTTP local; la política del navegador del entorno bloquea las URL `file:`.

- Cada control: 20 preguntas, 12 de opción múltiple y 8 de verdadero/falso, 10 minutos en total.
- Cobertura: 7 preguntas del capítulo 4, 7 del 5 y 6 del 6, con mayor peso en conceptos reforzados en clase.
- Se registra la respuesta al pulsar y se avanza sin revelar la solución. Es posible dejar una pregunta sin responder o finalizar anticipadamente.
- Se otorga 1 punto por acierto y 0 por error u omisión. Al agotarse el reloj se cierra el intento.
- La revisión incluye las alternativas, la respuesta propia, la solución, explicación y archivo con página/diapositiva/sección.
- La práctica de errores usa otra pregunta del concepto fallado u omitido, sin tiempo límite y con explicación inmediata. Se basa en el último control y no cambia su puntaje.
- Historial y avance se guardan en el almacenamiento local del navegador. El reloj continúa tras recargar o cerrar: no se reinicia el plazo. La disponibilidad del almacenamiento depende del navegador, perfil y ubicación del archivo; si no está disponible se muestra un aviso.
- Los indicadores usan palabras y símbolos, además de colores.

El banco incluye **180 preguntas y 45 conceptos**. Se priorizan las preguntas aún no vistas y se evitan las del control anterior. Al agotarse variantes disponibles de una categoría, se informa de la reutilización; no se promete un banco ilimitado. La práctica siempre excluye las preguntas del control que originó los errores.

## Fuentes y discrepancias

Se revisaron los dos PPT (18 diapositivas cada uno), las 18 páginas de notas y los capítulos 4, 5 y 6 de Jiménez (2012), completos. Las tres lecturas son escaneos y se extrajeron mediante OCR en español. Los originales no se modificaron.

La sección «Material revisado y precisiones importantes» de la aplicación identifica los archivos y documenta:

1. La contradicción de la clase 18, diapositiva 6, y las notas, página PDF 4, sobre propiedad: los efectos de su transmisión no están regulados por la CISG. Se sigue el capítulo 4, páginas PDF 7–8, y el capítulo 5, página PDF 12.
2. La referencia errónea a «Tratado Nacional» en las notas, página PDF 8: la lectura presenta la CISG como tratado internacional (capítulo 4, página PDF 6).
3. La simplificación sobre fecha de rescisión en las notas, página PDF 14: el modelo concede al comprador la facultad de rescindir si falta entrega en la fecha límite, no una terminación automática incondicional (capítulo 5, página PDF 14).

Se omiten cifras históricas sobre Estados parte y reglas universales simplificadas de embarque/riesgo. Las evaluaciones anteriores no estaban adjuntas: el estilo se basa en la descripción del usuario. Los ejemplos son aplicaciones breves elaboradas a partir de los conceptos adjuntos.

## Desarrollo y validación

Usar este checkout existente; cada tarea en la nube ya está aislada. No crear worktrees salvo solicitud expresa.

Después de editar `banco.js`, `motor.js`, `interfaz.js`, `estilos.css` o `plantilla.html`, regenerar:

```sh
cd /workspace/Simulador-Quizzes
python construir.py
node verificaciones/motor.test.cjs
```

Para comprobaciones internas en navegador, iniciar en una terminal:

```sh
cd /workspace/Simulador-Quizzes
python -m http.server 8000 --bind 127.0.0.1
```

En otra terminal:

```sh
cd /workspace/Simulador-Quizzes
python verificaciones/navegador.py
```

La validación usa Playwright Python y el Chromium preinstalado en `/usr/bin/chromium`. Estos son instrumentos de comprobación; el simulador no los necesita para funcionar. Los resultados y capturas se guardan en `verificaciones/`. No se requiere un servidor externo ni credenciales.
