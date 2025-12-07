import os
import time
import math
import random
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURACIÓN ---
# Recupera credenciales de variables de entorno para seguridad.
# Si no están configuradas, el script las pedirá por consola.
CM_USERNAME = os.getenv("CM_USERNAME")
CM_PASSWORD = os.getenv("CM_PASSWORD")

def init_driver():
    """Inicializa el navegador Chrome con opciones básicas."""
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Descomentar si quieres ejecutarlo sin ver el navegador
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def login_cardmarket(driver, username, password):
    """Inicia sesión de forma segura en Cardmarket."""
    if not username or not password:
        print("Credenciales no configuradas. Introdúcelas manualmente.")
        username = input("Usuario: ")
        password = input("Contraseña: ")

    print("Iniciando sesión...")
    driver.get("https://www.cardmarket.com/es/Magic/Login")
    
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "username")))
        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "userPassword").send_keys(password)
        driver.find_element(By.XPATH, "//input[@type='submit' and @value='Iniciar sesión']").click()
        
        # Esperar a que cargue la dashboard para confirmar login
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//h2[@class='ps-1 m-0' and text()='Tareas']"))
        )
        print("Login correcto.")
        return True
    except Exception as e:
        print(f"Error en login: {e}")
        return False

def get_my_inventory(driver):
    """
    Descarga el inventario propio escrapeando la sección 'Stock/Offers/Singles'.
    Devuelve un DataFrame con las cartas listadas.
    """
    print("--- 1. Obteniendo lista de expansiones con stock ---")
    driver.get("https://www.cardmarket.com/en/Magic/Stock/Offers/Singles?")
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    select_element = soup.find("select", {"name": "idExpansion"})
    
    expansiones = []
    if select_element:
        for opcion in select_element.find_all("option"):
            valor = opcion.get("value")
            texto = opcion.text.strip()
            
            # Parsear formato: "Nombre Expansión (Cantidad)"
            if "(" in texto:
                nombre, cartas = texto.rsplit("(", 1)
                nombre = nombre.strip()
                cartas = cartas.strip(")").strip()
            else:
                nombre, cartas = texto, "0"
            
            try:
                num_cartas = int(cartas)
            except ValueError:
                num_cartas = 0
                
            if num_cartas > 0:
                expansiones.append({"codigo": valor, "nombre": nombre, "cartas": num_cartas})
    
    print(f"Detectadas {len(expansiones)} expansiones con cartas.")

    # Escrapeo iterativo
    data_list = []
    
    print("--- 2. Descargando inventario detallado ---")
    for expansion in expansiones:
        print(f"Procesando: {expansion['nombre']} ({expansion['cartas']} cartas)")
        total_pages = math.ceil(expansion['cartas'] / 20)

        for site in range(1, total_pages + 1):
            # Pausa aleatoria para simular comportamiento humano (rate limiting)
            time.sleep(random.uniform(1.5, 3.0)) 
            
            url = f"https://www.cardmarket.com/en/Magic/Stock/Offers/Singles?idExpansion={expansion['codigo']}&site={site}"
            try:
                driver.get(url)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="UserOffersTable"]'))
                )
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                offers = soup.find_all('div', class_='article-row')
                
                for offer in offers:
                    try:
                        card_name = offer.find('a').text.strip()
                        
                        price_el = offer.find('span', class_='color-primary')
                        price = price_el.text.strip().replace("€", "").replace(",", ".") if price_el else "0.0"
                        
                        qty_el = offer.find('span', class_='item-count')
                        quantity = qty_el.text.strip() if qty_el else '0'

                        # Extraer metadatos extra
                        condition_el = offer.find('a', class_='article-condition')
                        condition = condition_el.text.strip() if condition_el else "N/A"
                        
                        lang_el = offer.find('span', class_='icon')
                        language = lang_el.get('data-bs-original-title', 'N/A') if lang_el else "N/A"
                        
                        is_foil = True if offer.find('span', class_='st_SpecialIcon') else False
                        
                        data_list.append({
                            "Card Name": card_name,
                            "My Price": float(price),
                            "Quantity": quantity,
                            "Expansion": expansion['nombre'],
                            "Condition": condition,
                            "Language": language,
                            "Foil": is_foil
                        })
                        
                    except Exception as e:
                        continue 
                        
            except Exception as e:
                print(f"Error en página {site} de {expansion['nombre']}: {e}")

    return pd.DataFrame(data_list)

def normalize_card_name(name):
    """
    Normaliza nombres de cartas para generar la URL de búsqueda correcta.
    Maneja casos especiales y caracteres que rompen las URLs.
    """
    # Mapeo manual de casos conflictivos detectados
    special_cases = {
        "Galadriel of Lothlórien": "Galadriel-of-Lothlorien",
        "Éomer of the Riddermark": "Eomer-of-the-Riddermark",
        "Éowyn, Fearless Knight": "Eowyn-Fearless-Knight",
        "Tura Kennerüd, Skyknight": "Tura-Kennerued-Skyknight",
        "Bartolomé del Presidio": "Bartolome-del-Presidio"
    }
    
    if name in special_cases:
        return special_cases[name]
        
    # Limpieza estándar
    clean_name = name.replace("/", "").replace("'", " ").replace("-", "")
    clean_name = clean_name.replace("(", "").replace(",", "").replace(")", "").replace(".", "").replace("//", "")
    return "-".join(clean_name.split())

def analyze_market_prices(driver, df_inventory):
    """
    Recorre el DataFrame del inventario, busca cada carta en el mercado
    y calcula precios mínimos y medios para sugerir cambios.
    """
    print("--- 3. Analizando precios de mercado ---")
    results = []
    
    # Mapeo de idiomas a IDs de Cardmarket
    lang_map = {"Spanish": 4, "English": 1, "French": 2, "Italian": 5, "German": 3}

    # Iterar sobre cada carta del inventario
    for index, row in df_inventory.iterrows():
        try:
            time.sleep(1.0) # Pausa ética entre peticiones
            
            card_name_url = normalize_card_name(row["Card Name"])
            
            # Limpieza básica de edición para URL
            edition_url = "-".join(row["Expansion"].split()).replace(":", "").replace(".", "").replace("'", "")
            if row["Expansion"] == "Core 2021": edition_url = "Core-Set-2021"

            # Construcción de URL de búsqueda
            base_url = f"https://www.cardmarket.com/en/Magic/Products/Singles/{edition_url}/{card_name_url}"
            params = "?sellerCountry=10" # Filtro: Solo vendedores de España
            
            if row["Language"] in lang_map:
                params += f"&language={lang_map[row['Language']]}"
            
            final_url = base_url + params
            print(f"Scraping [{index+1}/{len(df_inventory)}]: {row['Card Name']}")

            driver.get(final_url)
            
            # Parsear resultados
            soup = BeautifulSoup(driver.page_source, "html.parser")
            
            # Selector CSS para precios (puede requerir mantenimiento si la web cambia)
            price_elements = soup.select("span.color-primary.small.text-end.text-nowrap.fw-bold")
            prices_float = []
            
            for idx, p in enumerate(price_elements, start=1):
                # En Cardmarket los precios a veces aparecen duplicados o en estructuras pares
                if idx % 2 == 0: 
                    try:
                        clean_price = p.text.strip().replace('€', '').replace(',', '.')
                        prices_float.append(float(clean_price))
                    except:
                        continue
            
            market_min = np.min(prices_float) if prices_float else 0.0
            market_median = np.median(prices_float) if prices_float else 0.0
            
            # Crear registro enriquecido con los datos de mercado
            row_data = row.to_dict()
            row_data.update({
                "Market Min": market_min,
                "Market Median": market_median,
                "Diff": round(row["My Price"] - market_min, 2) # Diferencia de precio
            })
            results.append(row_data)

        except Exception as e:
            print(f"Error procesando {row['Card Name']}: {e}")
            results.append(row.to_dict()) # Guardar datos originales en caso de fallo

    return pd.DataFrame(results)

# --- EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    driver = init_driver()
    try:
        # Paso 1: Login
        if login_cardmarket(driver, CM_USERNAME, CM_PASSWORD):
            
            # Paso 2: Obtener mi inventario (Scraping privado)
            print("Iniciando descarga de inventario...")
            df_inventory = get_my_inventory(driver)
            print(f"Inventario descargado: {len(df_inventory)} cartas.")
            
            # Guardado intermedio por seguridad
            df_inventory.to_csv("my_inventory_backup.csv", index=False)
            
            # Paso 3: Analizar precios de mercado (Scraping público)
            # NOTA: Para pruebas rápidas, puedes descomentar la siguiente línea:
            # df_inventory = df_inventory.head(5) 
            df_final = analyze_market_prices(driver, df_inventory)
            
            # Paso 4: Guardar reporte final
            df_final.to_csv("market_analysis_report.csv", index=False)
            print("Proceso completado. Resultados guardados en 'market_analysis_report.csv'")
            
            # Muestra rápida
            print(df_final[["Card Name", "My Price", "Market Min", "Diff"]].head())

    except Exception as e:
        print(f"Error fatal durante la ejecución: {e}")
    finally:
        driver.quit()