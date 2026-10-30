# 🧺 Mi Canastita

Lista de compras en tonos pastel, hecha para usar desde el celular como app (PWA).

- 🍎 El ícono cambia solo según el producto que escribes (más de 300 productos peruanos).
- 🔢 Cantidades de 0.10 a 0.90 y luego números enteros, en **unidades**, **kg** o **soles (S/)**.
- ☁️ Lista compartida: crea un código y ábrelo en otro celular para ver los mismos datos.
- 📶 Funciona sin internet; los cambios se envían solos cuando vuelve la conexión.

**App:** https://jme-tnc.github.io/cansasta-aiuni/

## Instalar en el celular
- **Android (Chrome):** botón "Instalar" o Menú ⋮ → "Agregar a pantalla principal".
- **iPhone (Safari):** Compartir → "Agregar a pantalla de inicio".

## Archivos
- `index.html`, `sw.js`, `manifest.webmanifest`, `icons/` → la app publicada.
- `fuente/app.html` y `fuente/build.py` → código fuente; `python3 fuente/build.py` vuelve a generar la app.

La sincronización usa una base de datos de Supabase. La clave incluida en `index.html` es pública por diseño: las listas solo se pueden leer conociendo su código secreto de 16 caracteres.
