import streamlit as st
import requests
from bs4 import BeautifulSoup

# ---- Función para buscar productos en Carrefour ----
def buscar_en_carrefour(termino):
    productos = []
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    url = f"https://www.carrefour.es/search?query={termino}"
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    items = soup.select("article[data-test='search-grid-result']")
    for i, item in enumerate(items):
        try:
            nombre = item.select_one("a[data-test='result-title']").text.strip()
            precio = item.select_one("div[data-test='result-current-price']").text.strip()
            imagen = item.select_one("img[data-test='result-picture-image']")
            img_url = imagen['src'] if imagen else "https://via.placeholder.com/100"

            productos.append({
                "id": i,
                "Producto": nombre,
                "Precio": precio,
                "Imagen": img_url,
                "Supermercado": "Carrefour"
            })
        except Exception:
            continue
    return productos

# ---- Función para buscar productos en Mercadona vía API no oficial ----
def buscar_en_mercadona(termino):
    productos = []
    url = f"https://tienda.mercadona.es/api/search/?query={termino}"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        items = data.get("results", [])
        for i, item in enumerate(items):
            nombre = item.get("display_name", "Producto sin nombre")
            precio = f"{item.get('price_instructions', {}).get('unit_price', 0):.2f} €"
            imagen = item.get("thumbnail", "https://via.placeholder.com/100")

            productos.append({
                "id": i,
                "Producto": nombre,
                "Precio": precio,
                "Imagen": imagen,
                "Supermercado": "Mercadona"
            })
    return productos

# --------------------- STREAMLIT APP ---------------------
st.title("🛒 Comparador de precios Mercadona & Carrefour")

# Estados iniciales
if "lista_compra" not in st.session_state:
    st.session_state.lista_compra = []

if "resultados" not in st.session_state:
    st.session_state.resultados = []

if "termino_guardado" not in st.session_state:
    st.session_state.termino_guardado = ""

# Pestañas
tab1, tab2 = st.tabs(["🔍 Buscar productos", "📝 Mi lista de la compra"])

# -------- TAB 1: Buscador -------------
with tab1:
    termino = st.text_input("¿Qué producto quieres buscar?", value=st.session_state.termino_guardado)

    if st.button("Buscar"):
    if termino.strip():
        st.session_state.resultados = []
        st.session_state.termino_guardado = termino.strip()

        with st.spinner("🔍 Buscando productos en Mercadona y Carrefour..."):
            try:
                productos_mercadona = buscar_en_mercadona(termino.strip())
                productos_carrefour = buscar_en_carrefour(termino.strip())

                resultados = productos_mercadona + productos_carrefour

                if resultados:
                    resultados.sort(key=lambda x: float(x["Precio"].replace("€", "").replace(",", ".").split()[0]))
                    st.session_state.resultados = resultados
                    st.success(f"✅ Se encontraron {len(resultados)} productos.")
                else:
                    st.info("No se encontraron productos con ese término.")

            except Exception as e:
                st.error(f"❌ Error al buscar productos: {str(e)}")

    else:
        st.warning("⚠️ Introduce un término de búsqueda.")

    resultados = st.session_state.resultados
    if resultados:
        st.success(f"Se encontraron {len(resultados)} productos:")
        for i, producto in enumerate(resultados):
            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])
            with col1:
                st.image(producto["Imagen"], width=100)
            with col2:
                st.write(f"**{producto['Producto']}**")
                st.write(f"**{producto['Precio']}**")
            with col3:
                st.write(f"🛒 **Supermercado:** {producto.get('Supermercado', 'Desconocido')}")
            with col4:
                cantidad = st.number_input("Cantidad", min_value=1, value=1, key=f"cantidad_{i}")
            with col5:
                if st.button("➕ Añadir", key=f"add_{i}"):
                    producto["Cantidad"] = cantidad
                    st.session_state.lista_compra.append(producto)
                    st.success(f"Añadido: {producto['Producto']} x {cantidad}")

# -------- TAB 2: Lista de la compra -------------
with tab2:
    st.subheader("📝 Mi lista de la compra")

    if st.session_state.lista_compra:
        total_general = 0
        for i, producto in enumerate(st.session_state.lista_compra):
            st.markdown("---")
            col1, col2, col3 = st.columns([2, 4, 3])
            with col1:
                st.image(producto["Imagen"], width=80)
            with col2:
                st.write(f"**{producto['Producto']}**")
                st.write(f"🛒 **Supermercado:** {producto['Supermercado']}")
                precio_unitario = float(producto["Precio"].replace("€", "").replace(",", ".").split()[0])
                cantidad = st.number_input("Cantidad", min_value=1, value=producto["Cantidad"], key=f"cantidad_lista_{i}")
                producto["Cantidad"] = cantidad
            with col3:
                total_producto = cantidad * precio_unitario
                total_general += total_producto
                st.write(f"💳 **Total:** {total_producto:.2f} €")
        st.markdown("---")
        st.write(f"**Total general de la compra: {total_general:.2f} €**")
    else:
        st.warning("Tu lista de compra está vacía.")
