# 🃏 Cardmarket Price Tracker & Inventory Manager

Herramienta de **Ingeniería de Datos y Automatización** desarrollada en Python para la gestión eficiente de inventario en el marketplace de Magic: The Gathering (Cardmarket).

Este proyecto implementa un pipeline **ETL (Extract, Transform, Load)** que extrae datos de inventario propio, realiza scraping de precios de mercado en tiempo real y calcula métricas de competitividad para optimizar estrategias de venta.

## 🚀 Funcionalidades Clave

* **Extracción Segura de Datos:** Automatización de login y navegación mediante **Selenium** gestionando sesiones y cookies.
* **Web Scraping Robusto:** Uso de **BeautifulSoup4** para el parseo eficiente del DOM y extracción de metadatos (edición, condición, foil, idioma).
* **Limpieza de Datos (Data Wrangling):** Normalización compleja de nombres de cartas y ediciones para asegurar la correspondencia exacta en las URLs de búsqueda (manejo de caracteres especiales, split cards, etc.).
* **Análisis de Mercado:** Comparativa automática entre el precio listado y las tendencias del mercado (Mínimo y Mediana) usando **Pandas** y **NumPy**.
* **Seguridad y Ética:** * Gestión de credenciales mediante variables de entorno (`.env`).
    * Implementación de `Time Delays` aleatorios para respetar los servidores y evitar bloqueos (Rate Limiting).

## 🛠️ Stack Tecnológico

* **Lenguaje:** Python 3.x
* **Automatización:** Selenium WebDriver
* **Parsing:** BeautifulSoup4
* **Análisis de Datos:** Pandas, NumPy
* **Gestión de Entorno:** Python-dotenv, Webdriver-manager

## ⚙️ Instalación y Uso

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/tu-usuario/cardmarket_pricing_tool.git](https://github.com/tu-usuario/cardmarket_pricing_tool.git)
    cd cardmarket_pricing_tool
    ```

2.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configurar Variables de Entorno:**
    Crea un archivo `.env` en la raíz del proyecto para proteger tus credenciales:
    ```bash
    CM_USERNAME=tu_usuario
    CM_PASSWORD=tu_contraseña
    ```

4.  **Ejecutar el Script:**
    ```bash
    python scraper_cardmarket.py
    ```

## 📂 Estructura del Proyecto

```text
├── scraper_cardmarket.py   # Script principal (Lógica ETL y Scraping)
├── requirements.txt        # Dependencias del proyecto
├── .env                    # Credenciales (No incluido en el repo por seguridad)
├── .gitignore              # Configuración de exclusión de Git
└── README.md               # Documentación
