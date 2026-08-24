# Cardmarket — precios de mercado de tu propio inventario

Cardmarket, el marketplace europeo de Magic: The Gathering, no tiene una vista que
conteste a la única pregunta que importa cuando vendes: *¿cuáles de mis cartas están mal
valoradas ahora mismo?* Con cien o doscientas referencias, mirarlo a mano es una tarde
perdida. Este script lo hace solo.

Se loguea con Selenium, recorre el inventario paginado, saca de cada artículo la carta y
sus metadatos, busca el precio de mercado actual y monta un DataFrame comparando tu precio
listado con el mínimo y la mediana del mercado.

## Uso

```bash
pip install -r requirements.txt
```

Credenciales en un `.env` en la raíz:

```bash
CM_USERNAME=tu_usuario
CM_PASSWORD=tu_contraseña
```

Y a correr:

```bash
python scraper_cardmarket.py
```

Si no encuentra las variables de entorno, las pide por consola.

## La parte que da guerra

La normalización de nombres concentra casi toda la casuística del proyecto. Para consultar
el precio de una carta hay que construir su URL, y la URL exige la forma exacta que
Cardmarket espera: acentos, caracteres especiales, y las *split cards* —esas que llevan
dos nombres separados por barras— con su propio formato aparte. Un fallo aquí no lanza
una excepción: devuelve una página de resultados vacía, en silencio, y te quedas sin
precio para esa carta sin enterarte. Media `normalize_card_name()` está escrita por eso.

El otro detalle con enjundia es la mediana. El precio mínimo del mercado suele venir de
cartas en mal estado o de vendedores extracomunitarios, y arrastra la media hacia abajo.
La mediana aguanta mejor esos extremos, así que la comparación seria se hace contra ella
y el mínimo queda como referencia.

También se leen edición, estado de conservación, idioma y si es *foil*: los cuatro mueven
el precio, y comparar sin ellos es comparar otra carta.

## Uso responsable

Es una herramienta personal, sobre la propia cuenta y el propio inventario. Las
credenciales van por variables de entorno con `python-dotenv`, el `.env` está en el
`.gitignore` y nunca se ha versionado. Entre peticiones hay pausas aleatorias para no
machacar el servidor.

```text
├── scraper_cardmarket.py   # Lógica ETL y scraping
├── requirements.txt        # Dependencias
├── .gitignore              # Excluye .env, datos y artefactos
└── README.md
```

Python, Selenium, BeautifulSoup4, pandas, NumPy.
