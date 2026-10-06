import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

BASE_DIR = Path(__file__).parent
DOCS_DIR = BASE_DIR / "docs"

STOPWORDS_ES = {
    "a", "al", "ante", "bajo", "con", "contra", "de", "del", "desde", "durante", "en", "entre",
    "hacia", "hasta", "para", "por", "segun", "sin", "sobre", "tras", "y", "e", "o", "u", "ni",
    "que", "como", "cuando", "donde", "quien", "el", "la", "los", "las", "un", "una", "unos", "unas",
    "mi", "tu", "su", "sus", "este", "esta", "estos", "estas", "es", "son", "ser", "fue", "eran",
    "hay", "ha", "han", "se", "lo", "le", "les", "me", "te", "nos", "para", "mas", "muy"
}

# Respaldo por si la carpeta docs/ no existe (mismo contenido que los .txt).
_DOCUMENTOS_RESPALDO = {
    "D1": "Los sistemas de recuperación de información permiten encontrar documentos relevantes en colecciones digitales.",
    "D2": "La indexación de documentos usa términos de índice para acelerar la búsqueda de información.",
    "D3": "El procesamiento de lenguaje natural elimina stopwords y reduce palabras a sus raíces mediante stemming.",
    "D4": "Las bases de datos almacenan registros y permiten consultas mediante lenguaje SQL.",
    "D5": "Un motor de búsqueda utiliza índices invertidos para recuperar documentos relacionados con una consulta.",
    "D6": "La precisión y la exhaustividad son métricas empleadas para evaluar sistemas de recuperación de información.",
    "D7": "Los algoritmos de aprendizaje automático pueden clasificar documentos y detectar temas relevantes.",
    "D8": "La biblioteca digital contiene libros, artículos científicos y recursos de investigación académica."
}
_CONSULTA_RESPALDO = "recuperacion de informacion indexacion de documentos"


def cargar_documentos(carpeta=DOCS_DIR):
    """Carga D1.txt, D2.txt... desde carpeta/docs/. ID = nombre del archivo."""
    documentos = {}
    if not carpeta.exists():
        return {}
    for ruta in sorted(carpeta.glob("D*.txt")):
        doc_id = ruta.stem.upper()  # D1.txt -> D1
        texto = ruta.read_text(encoding="utf-8").strip()
        if texto:
            documentos[doc_id] = texto
    return documentos


def cargar_consulta(carpeta=DOCS_DIR, respaldo=_CONSULTA_RESPALDO):
    """Lee docs/consulta.txt si existe, si no usa la consulta de respaldo."""
    ruta = carpeta / "consulta.txt"
    if ruta.exists():
        texto = ruta.read_text(encoding="utf-8").strip()
        if texto:
            return " ".join(texto.split())
    return respaldo


DOCUMENTOS = cargar_documentos() or dict(_DOCUMENTOS_RESPALDO)

# Juicio de relevancia conocido para la consulta propuesta.
RELEVANTES = {"D1", "D2", "D5", "D6"}
CONSULTA = cargar_consulta()

def normalizar(texto):
    texto = unicodedata.normalize("NFD", texto.lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = re.sub(r"<[^>]+>", " ", texto)  # elimina etiquetas HTML/XML
    texto = re.sub(r"[^a-z\s]", " ", texto)
    return " ".join(texto.split())

def eliminar_stopwords(tokens):
    return [t for t in tokens if t not in STOPWORDS_ES]

def stem_simple(palabra):
    for sufijo in ("amientos", "imientos", "aciones", "adores", "adoras", "acion", "mente", "idades", "idad", "ando", "iendo", "ados", "idos", "es", "os", "as", "ar", "er", "ir", "o", "a", "s"):
        if palabra.endswith(sufijo) and len(palabra) > len(sufijo) + 2:
            return palabra[:-len(sufijo)]
    return palabra

def extract_noun_groups(tokens):
    """Extrae grupos de dos palabras consecutivas (heuristica simple)."""
    return [f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens)-1)
            if len(tokens[i]) > 3 and len(tokens[i+1]) > 3]

def get_keywords(tokens, top_n=10):
    """Obtiene las keywords por frecuencia."""
    return Counter(tokens).most_common(top_n)

def procesar(texto):
    normalizado = normalizar(texto)
    tokens = normalizado.split()
    sin_stopwords = eliminar_stopwords(tokens)
    stems = [stem_simple(t) for t in sin_stopwords]
    return stems

def crear_indice_invertido(documentos):
    indice = defaultdict(set)
    for doc_id, texto in documentos.items():
        for termino in set(procesar(texto)):
            indice[termino].add(doc_id)
    return dict(indice)

def buscar(consulta, indice, documentos):
    terminos = procesar(consulta)
    puntuaciones = Counter()
    for termino in terminos:
        for doc_id in indice.get(termino, set()):
            puntuaciones[doc_id] += 1
    return [doc for doc, _ in sorted(puntuaciones.items(), key=lambda x: (-x[1], x[0]))], terminos, puntuaciones

def metricas(recuperados, relevantes, k=None):
    if k is not None:
        recuperados = recuperados[:k]
    recuperados_set = set(recuperados)
    verdaderos_positivos = len(recuperados_set & relevantes)
    precision = verdaderos_positivos / len(recuperados) if recuperados else 0.0
    exhaustividad = verdaderos_positivos / len(relevantes) if relevantes else 0.0
    f1 = 2 * precision * exhaustividad / (precision + exhaustividad) if (precision + exhaustividad) > 0 else 0.0
    return precision, exhaustividad, f1, verdaderos_positivos

def precision_at_k(recuperados, relevantes, k):
    """P@k: precision en los primeros k resultados."""
    p, _, _, _ = metricas(recuperados, relevantes, k)
    return p

def graficar(recuperados, relevantes):
    if plt is None:
        print("\nNo se generaron gráficas: instala matplotlib con 'pip install matplotlib'.")
        return

    ks = list(range(1, len(recuperados) + 1))
    precisiones, exhaustividades, f1s = [], [], []
    for k in ks:
        p, e, f1, _ = metricas(recuperados, relevantes, k)
        precisiones.append(p)
        exhaustividades.append(e)
        f1s.append(f1)

    # Métricas globales
    p_total, e_total, f1_total, _ = metricas(recuperados, relevantes)
    plt.figure(figsize=(7, 4.5))
    barras = plt.bar(["Precisión", "Exhaustividad", "F1"], [p_total, e_total, f1_total], color=["#2563eb", "#16a34a", "#f59e0b"])
    plt.ylim(0, 1.1)
    plt.ylabel("Valor de la métrica")
    plt.title("Evaluación global de la consulta")
    for barra, valor in zip(barras, [p_total, e_total, f1_total]):
        plt.text(barra.get_x() + barra.get_width()/2, valor + .03, f"{valor:.2f}", ha="center")
    plt.tight_layout()
    plt.savefig("grafica_metricas_globales.png", dpi=150)
    plt.close()

    # Curvas conforme aumenta el número de documentos recuperados
    plt.figure(figsize=(7, 4.5))
    plt.plot(ks, precisiones, marker="o", label="Precisión", color="#2563eb")
    plt.plot(ks, exhaustividades, marker="s", label="Exhaustividad", color="#16a34a")
    plt.plot(ks, f1s, marker="^", label="F1", color="#f59e0b")
    plt.xticks(ks)
    plt.ylim(0, 1.1)
    plt.xlabel("Número de documentos recuperados (k)")
    plt.ylabel("Valor de la métrica")
    plt.title("Precisión, exhaustividad y F1 acumuladas")
    plt.legend()
    plt.grid(alpha=.3)
    plt.tight_layout()
    plt.savefig("curva_precision_exhaustividad.png", dpi=150)
    plt.close()
    print("\nGráficas guardadas: grafica_metricas_globales.png y curva_precision_exhaustividad.png")

def main():
    indice = crear_indice_invertido(DOCUMENTOS)
    recuperados, terminos_consulta, puntuaciones = buscar(CONSULTA, indice, DOCUMENTOS)
    precision, exhaustividad, f1, vp = metricas(recuperados, RELEVANTES)

    print("=" * 70)
    print("RECUPERACIÓN DE INFORMACIÓN: MÚLTIPLES DOCUMENTOS Y EVALUACIÓN")
    print("=" * 70)
    print(f"\nDocumentos cargados desde {DOCS_DIR.name}/: {sorted(DOCUMENTOS)}")
    print(f"\nConsulta propuesta: {CONSULTA}")
    print(f"Términos procesados: {terminos_consulta}")
    print("\nDocumentos recuperados (ordenados por coincidencias):")
    for doc_id in recuperados:
        etiqueta = "RELEVANTE" if doc_id in RELEVANTES else "NO RELEVANTE"
        print(f"  {doc_id}: coincidencias={puntuaciones[doc_id]} - {etiqueta}")

    print(f"\nDocumentos relevantes definidos: {sorted(RELEVANTES)}")
    print(f"Verdaderos positivos: {vp}")
    print(f"Precisión = relevantes recuperados / recuperados = {vp}/{len(recuperados)} = {precision:.2%}")
    print(f"Exhaustividad = relevantes recuperados / relevantes existentes = {vp}/{len(RELEVANTES)} = {exhaustividad:.2%}")
    print(f"F1 = 2*P*R/(P+R) = {f1:.2%}")

    print("\nMétricas por corte (P@k):")
    for k in range(1, len(recuperados) + 1):
        p_k, _, _, _ = metricas(recuperados, RELEVANTES, k)
        print(f"  P@{k}={p_k:.2%}")
    for k_extra in (5, 10):
        if k_extra > len(recuperados):
            p_k = precision_at_k(recuperados, RELEVANTES, k_extra)
            print(f"  P@{k_extra}={p_k:.2%} (con solo {len(recuperados)} recuperados)")
    print("\nÍndice invertido (términos de la consulta):")
    for termino in terminos_consulta:
        print(f"  {termino}: {sorted(indice.get(termino, set()))}")

    print("\nPipeline por documento (grupos sustantivos y keywords):")
    for doc_id, texto in DOCUMENTOS.items():
        tokens = normalizar(texto).split()
        filtrados = eliminar_stopwords(tokens)
        stems = [stem_simple(t) for t in filtrados]
        grupos = extract_noun_groups(filtrados)
        keywords = get_keywords(stems)
        print(f"  {doc_id}: grupos={grupos[:3]} keywords={keywords[:5]}")

    graficar(recuperados, RELEVANTES)

if __name__ == "__main__":
    main()
