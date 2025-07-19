import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# Función para buscar productos en Mercadona
def buscar_en_mercadona_selenium(termino):
    opciones = Options()
    opciones.add_argument("--headless")
    opciones.add_argument("--disable-gpu")
    opciones.add_argument("--no-sandbox")
    service = Service("./chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=opciones)
    driver.get(f"https://tienda.mercadona.es/search-results?query={termino}")
    time.sleep(5)
    productos = []
    items = driver.find_elements(By.CSS_SELECTOR, ".product-cell")

    for i, item in enumerate(items):
        try:
            nombre = item.find_element(By.CSS_SELECTOR, ".product-cell__description-name").text
            precio = item.find_element(By.CSS_SELECTOR, ".product-price").text
            try:
                imagen = item.find_element(By.CSS_SELECTOR, ".product-cell img").get_attribute("src")
            except:
                imagen = "https://via.placeholder.com/100"

            productos.append({"id": i, "Producto": nombre, "Precio": precio, "Imagen": imagen, "Supermercado": "Mercadona"})
        except:
            continue

    driver.quit()
    return productos

# Función para buscar productos en Carrefour
def buscar_en_carrefour_selenium(termino):
    opciones = Options()
    opciones.add_argument("--headless")
    opciones.add_argument("--disable-gpu")
    opciones.add_argument("--no-sandbox")
    opciones.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    service = Service("./chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=opciones)
    driver.get(f"https://www.carrefour.es/?query={termino}")
    time.sleep(10)

    productos = []
    items = driver.find_elements(By.CSS_SELECTOR, "article[data-test='search-grid-result']")

    print(f"Encontrados {len(items)} productos en Carrefour")  # Depuración

    for i, item in enumerate(items):
        try:
            nombre = item.find_element(By.CSS_SELECTOR, "a[data-test='result-title']").text
            precio = item.find_element(By.CSS_SELECTOR, "div[data-test='result-current-price']").text
            try:
                imagen = item.find_element(By.CSS_SELECTOR, "img[data-test='result-picture-image']").get_attribute("src")
            except:
                imagen = "https://via.placeholder.com/100"

            productos.append({"id": i, "Producto": nombre, "Precio": precio, "Imagen": imagen, "Supermercado": "Carrefour"})
        except Exception as e:
            print(f"Error al obtener producto {i} en Carrefour: {e}")
            continue

    print(f"Total productos obtenidos de Carrefour: {len(productos)}")  # Depuración final
    driver.quit()
    return productos

# Inicializar estados
if "lista_compra" not in st.session_state:
    st.session_state.lista_compra = []

if "resultados" not in st.session_state:
    st.session_state.resultados = []

if "termino_guardado" not in st.session_state:
    st.session_state.termino_guardado = ""

st.title("🛒 Comparador de precios Mercadona & Carrefour")

# Pestañas
tab1, tab2 = st.tabs(["🔍 Buscar productos", "📝 Mi lista de la compra"])

# -------- TAB 1: Buscador -------------
with tab1:
    termino = st.text_input("¿Qué producto quieres buscar?", value=st.session_state.termino_guardado)

    if st.button("Buscar"):
        if termino.strip():
            productos_mercadona = buscar_en_mercadona_selenium(termino.strip())
            productos_carrefour = buscar_en_carrefour_selenium(termino.strip())

            resultados = productos_mercadona + productos_carrefour
            resultados.sort(key=lambda x: float(x["Precio"].replace("€", "").replace(",", ".").split()[0]))

            st.session_state.resultados = resultados
            st.session_state.termino_guardado = termino.strip()
        else:
            st.warning("Introduce un término de búsqueda.")

    resultados = st.session_state.resultados
    if resultados:
        st.success(f"Se encontraron {len(resultados)} productos:")
        for i, producto in enumerate(resultados):
            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])
            with col1:
                if producto["Imagen"]:
                    st.image(producto["Imagen"], width=100)
                else:
                    st.write("🖼️ Sin imagen")
            with col2:
                st.write(f"**{producto['Producto']}**")
                st.write(f"**{producto['Precio']}**")
            with col3:
                st.write(f"🛒 **Supermercado:** {producto.get('Supermercado', 'Desconocido')}")
            with col4:
                cantidad = st.number_input(f"**Cantidad**", min_value=1, value=1, key=f"cantidad_{i}")
            with col5:
                if st.button("➕ Añadir", key=f"add_{i}"):
                    producto["Cantidad"] = cantidad
                    st.session_state.lista_compra.append(producto)
                    st.success(f"Añadido: {producto['Producto']} x {cantidad}")


# -------- TAB 2: Mi lista de la compra -------------
with tab2:
    st.subheader("📝 Mi lista de la compra")

    if st.session_state.lista_compra:
        total_general = 0
        for i, producto in enumerate(st.session_state.lista_compra):
            st.markdown("---")
            col1, col2, col3 = st.columns([2, 4, 3])
            with col1:
                if producto["Imagen"]:
                    st.image(producto["Imagen"], width=80)
                else:
                    st.write("🖼️ Sin imagen")
            with col2:
                st.write(f"**{producto['Producto']}**")
                st.write(f"🛒 **Supermercado:** {producto.get('Supermercado', 'Desconocido')}")
                precio_unitario = float(producto["Precio"].replace("€", "").replace(",", ".").split()[0])
                st.write(f"**{precio_unitario:.2f} €/ud.**")
                cantidad = st.number_input(f"**Cantidad**", min_value=1, value=1, key=f"cantidad_lista_{i}")
                producto["Cantidad"] = cantidad  # Actualiza la cantidad en tiempo real
            with col3:
                total_producto = producto["Cantidad"] * precio_unitario
                total_general += total_producto
                st.write(f"💳 **Total:** {total_producto:.2f} €")

        st.markdown("---")
        st.write(f"**Total general de la compra: {total_general:.2f} €**")
    else:
        st.warning("Tu lista de compra está vacía.")

