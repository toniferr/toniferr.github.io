# Portfolio · Antonio Ferreiro

Portfolio personal publicado en **https://toniferr.github.io/**, en español (por defecto), inglés y gallego.

Su estética es la de un plano técnico vivo: el hero es un diagrama de arquitectura interactivo que hace de mapa del sitio,
cada sección es una "hoja" del plano y los proyectos se explican con su propio diagrama, que se dibuja al hacer scroll.

- **Sin frameworks ni dependencias.** HTML, CSS y JavaScript propios, desarrollados con IA (Claude Code). El generador (`build.py`) usa solo la
  biblioteca estándar de Python 3.10+.
- **Contenido separado de la presentación.** Todo el texto vive en `content/` como JSON. Para añadir un proyecto basta
  con añadir un fichero.
- **Datos reales de GitHub.** Estrellas, lenguajes, repos recientes y calendario de contribuciones se obtienen en cada
  publicación, y una ejecución semanal programada los mantiene al día.
- **Seguro por defecto.** CSP estricta (solo recursos propios, sin JavaScript inline), fuentes servidas en local, sin CDN
  ni analítica, y las actions del workflow fijadas por SHA.

## Arrancar en local

```powershell
python build.py --serve        # genera dist/ y lo sirve en http://127.0.0.1:8000
```

| Opción | Qué hace |
| --- | --- |
| `--refresh-github` | Descarga datos frescos de GitHub a `data/github.json` (usa `GITHUB_TOKEN` si existe; sin token, la API anónima basta) |
| `--release` | Modo estricto, el que usa CI: falla si hay entradas `draft` o traducciones incompletas |
| `--base /ruta/` | Ruta base si el sitio no se sirve desde la raíz del dominio |

El build valida que `es`, `en` y `gl` tengan exactamente las mismas claves y avisa si la etiqueta de un nodo de diagrama
no cabe en su caja.

## Estructura

```text
content/
├── profile.json          nombre, enlaces, año de inicio profesional, repos excluidos de "actividad reciente"
├── i18n/{es,en,gl}.json  textos de la interfaz (deben tener las mismas claves)
├── projects/*.json       un fichero por proyecto (destacado o no)
├── career.json           trayectoria, en orden de aparición
├── skills.json           capas del stack + columna transversal de arquitectura
└── hero.json             diagrama del hero (cada servicio enlaza a una sección)
data/github.json          snapshot de la API de GitHub (se regenera en CI)
src/                      plantilla, CSS, JS, fuentes, imágenes
build.py                  generador → dist/, dist/en/, dist/gl/
```

## Añadir, quitar o reordenar proyectos

Crea `content/projects/<id>.json`; para quitarlo, borra el fichero. Campos principales:

```jsonc
{
  "id": "mi-proyecto",
  "featured": true,                 // true: bloque grande con diagrama; false: tarjeta en "Otros proyectos"
  "order": 4,                       // posición entre los destacados
  "repo": "toniferr/mi-proyecto",   // de aquí salen estrellas, fechas, licencia y lenguajes
  "title": "Mi proyecto",
  "links": { "demo": "https://…", "download": "https://…" },
  "tagline":    { "es": "…", "en": "…", "gl": "…" },
  "summary":    { "es": "…", "en": "…", "gl": "…" },   // admite **negrita**, *cursiva* y `código`
  "highlights": { "es": ["…"], "en": ["…"], "gl": ["…"] },
  "stack": ["Java", "Kubernetes"],
  "related": ["toniferr/otro-repo"],                   // se enlazan y se excluyen de "actividad reciente"
  "diagram": { … }                                     // opcional, ver abajo
}
```

Cualquier texto puede ser una cadena simple (igual en los tres idiomas) o un objeto `{ "es", "en", "gl" }`.

### Diagramas

Rejilla de 20 px: `x`, `y`, `w` y `h` van en celdas (`h` vale 3 por defecto). Las aristas se trazan solas, con
recorrido ortogonal de borde a borde; `"mid"` fija la coordenada del tramo intermedio si hace falta.

```jsonc
{
  "cols": 34, "rows": 20,
  "groups": [{ "x": 0, "y": 0, "w": 12, "h": 19, "label": "GitHub" }],
  "nodes": [
    { "id": "a", "x": 1, "y": 2, "w": 10, "kind": "repo", "label": "repo-a", "sub": { "es": "guía", "en": "guide", "gl": "guía" } },
    { "id": "b", "x": 17, "y": 2, "w": 9, "kind": "service", "label": "api", "accent": true }
  ],
  "edges": [{ "from": "a", "to": "b", "label": "pull" }]
}
```

Tipos de nodo (`kind`): `service`, `repo`, `db`, `external`, `controller`, `browser`, `lock`, `doc`, `cube`, `user`,
`gateway`.

## Trayectoria

`content/career.json` se pinta en el orden del fichero (lo más reciente arriba). `track` es `work`, `oss` o `edu`;
`current: true` muestra "actualidad". Una entrada con `"draft": true` se ve en local con la etiqueta *borrador*, pero
**hace fallar `--release`**, así que nada a medias llega a publicarse.

## Publicación

El workflow `.github/workflows/deploy.yml` construye con `--release --refresh-github` y publica en GitHub Pages en cada
push a `main`, cada lunes (para refrescar los datos de GitHub) o a mano desde *Actions*.

### Migración desde el portfolio anterior (una sola vez)

El repo `toniferr/toniferr.github.io` publica hoy el portfolio Vue desde `master`. El plan es conservarlo en la rama
`legacy-portfolio` y publicar este proyecto desde `main`:

```powershell
cd C:\Users\ferre\Workspace\portfolio
git init -b main
git add .
git commit -m "new portfolio: living-blueprint design, es/en/gl, data-driven projects"

git remote add origin https://github.com/toniferr/toniferr.github.io.git
git fetch origin
git push origin origin/master:refs/heads/legacy-portfolio   # copia del portfolio antiguo
git push -u origin main                                     # historia nueva, no sobrescribe nada
```

Después, en GitHub (*Settings* del repo):

1. *General → Default branch*: cambiar a `main`.
2. *Pages → Build and deployment → Source*: **GitHub Actions**.
3. *Actions → Deploy to GitHub Pages → Run workflow* (el primer push puede fallar si se hizo antes de los pasos 1–2).
4. Cuando la web nueva esté verificada, la rama `master` puede borrarse; su contenido sigue en `legacy-portfolio`.
