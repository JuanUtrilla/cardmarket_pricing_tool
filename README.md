# Cardmarket — pipeline ETL de precios de mercado

Herramienta en Python que extrae el inventario propio de un vendedor en **Cardmarket**
(marketplace de Magic: The Gathering), obtiene por *scraping* los precios de mercado en
tiempo real de cada carta y calcula métricas de competitividad para ajustar el precio de
venta.

## Qué resuelve

Cardmarket no ofrece una vista que responda a la pregunta útil: *¿cuáles de mis cartas
están mal valoradas ahora mismo?* Revisarlo a mano en un inventario de cientos de
referencias es inviable. Este pipeline lo automatiza de extremo a extremo.

## Pipeline

**1. Extracción.** Login automatizado y navegación con **Selenium**, gestionando sesión y
cookies. Se recorre el inventario propio paginado.

**2. Parseo.** **BeautifulSoup4** sobre el DOM para extraer, de cada artículo, la carta y
sus metadatos: edición, estado de conservación, si es *foil* y el idioma. Los cuatro
influyen en el precio y no se pueden ignorar al comparar.

**3. Normalización.** La parte con más casuística real: los nombres de cartas y ediciones
deben convertirse a la forma exacta que espera la URL de búsqueda. Incluye caracteres
especiales, acentos y las *split cards* (con dos nombres separados por barras), que siguen
un formato de URL propio. Un fallo aquí no da error, da un resultado vacío silencioso.

**4. Análisis.** Con **pandas** y **NumPy**, comparación del precio listado frente al
**mínimo y la mediana** del mercado. La mediana se usa deliberadamente en lugar de la
media: el precio mínimo suele venir de artículos en mal estado o de vendedores
extracomunitarios, y arrastra la media a la baja.

## Consideraciones de uso responsable

- **Credenciales fuera del código**, mediante variables de entorno con `python-dotenv`.
  El fichero `.env` está excluido en `.gitignore` y nunca se ha versionado.
- **Retardos aleatorios entre peticiones** para no sobrecargar el servidor y respetar un
  ritmo de navegación razonable.

Es una herramienta de uso personal sobre la propia cuenta y el propio inventario.

## Instalación y uso

```bash
git clone https://github.com/JuanUtrilla/cardmarket_pricing_tool.git
cd cardmarket_pricing_tool
pip install -r requirements.txt
```

Crea un fichero `.env` en la raíz con tus credenciales:

```bash
CM_USERNAME=tu_usuario
CM_PASSWORD=tu_contraseña
```

Y ejecuta:

```bash
python scraper_cardmarket.py
```

Si no encuentra las variables de entorno, el script las pide por consola.

## Estructura

```text
├── scraper_cardmarket.py   # Lógica ETL y scraping
├── requirements.txt        # Dependencias
├── .gitignore              # Excluye .env, datos y artefactos
└── README.md
```

## Stack

Python · Selenium · BeautifulSoup4 · pandas · NumPy · python-dotenv · webdriver-manager

---

**Juan Peñas Utrilla** — [LinkedIn](https://www.linkedin.com/in/juan-penas-utrilla/) · [GitHub](https://github.com/JuanUtrilla)
