# evaluacion

Sistema de Recuperación de Información (SRI) en Python: pipeline completo + evaluación.

## Pipeline
1. Normalización (minúsculas, sin acentos NFD + Mn, limpia HTML)
2. Tokenización
3. Eliminación de stopwords ES
4. Stemming simple español
5. Grupos sustantivos (bigramas len > 3)
6. Keywords por frecuencia (Counter)
7. Índice invertido + búsqueda por coincidencias

## Métricas
- Precisión, Exhaustividad (Recall), F1
- P@k (P@1..P@5, P@10)
- Gráficas: `grafica_metricas_globales.png`, `curva_precision_exhaustividad.png`

## Uso
```bash
pip install -r requirements.txt
python evaluacion.py
```

## Documentos externos (.txt)
Ya no están quemados en el código. Viven en `docs/`:
- `docs/D1.txt` ... `docs/D8.txt` → el ID es el nombre del archivo (D1.txt = D1)
- `docs/consulta.txt` → la consulta (si no existe, usa la de respaldo)
- Para agregar un documento nuevo, solo crea `docs/D9.txt` y corre de nuevo
- `evaluacion.py: cargar_documentos()` y `cargar_consulta()` los leen con UTF-8

## Codespaces
Listo para abrir en GitHub Codespaces (Python 3.11 + matplotlib preinstalado).
