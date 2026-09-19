import os
import re
from typing import List, Dict, Tuple

PAYLOADS_DIR = "payloads"

# Palabras vacías en español e inglés que no aportan relevancia en comandos
STOPWORDS = {
    "de", "la", "el", "en", "un", "al", "se", "su", "mi", "tu", "es", "son",
    "to", "in", "on", "at", "by", "of", "is", "it", "or", "an", "as", "no",
    "que", "para", "con", "por", "como", "cual", "cuales", "donde", "cuando",
    "los", "las", "una", "uno", "unos", "unas", "del", "este", "esta", "estos",
    "the", "and", "for", "with", "from", "that", "this", "are", "have", "has",
    "dame", "muestrame", "genera", "crea", "hacer", "hago", "puedo", "sirve",
    "necesito", "quiero", "comando", "codigo", "favor", "ayuda"
}

# Caché en memoria para evitar leer el disco en cada solicitud
_CHUNKS_CACHE: List[Dict] = []
_FILES_MTIME: Dict[str, float] = {}


def extract_keywords(text: str) -> set[str]:
    """Extrae palabras clave de al menos 2 caracteres, preservando términos como 'ip', 'ls', 'ps'."""
    tokens = re.findall(r'\b[a-zA-Z0-9_\-\.]{2,}\b', text.lower())
    return {t for t in tokens if t not in STOPWORDS}


def _chunk_content(content: str, filename: str) -> List[Dict]:
    """Divide un documento en bloques lógicos (párrafos o secciones) de 300-600 caracteres."""
    raw_blocks = re.split(r'\n\s*\n', content)
    chunks = []
    current_chunk = []
    current_len = 0

    for block in raw_blocks:
        block = block.strip()
        if not block:
            continue

        # Si un bloque es muy grande (> 900 chars), dividirlo por líneas
        if len(block) > 900:
            lines = block.splitlines()
            sub_chunk = []
            sub_len = 0
            for line in lines:
                sub_chunk.append(line)
                sub_len += len(line)
                if sub_len >= 450:
                    text_chunk = "\n".join(sub_chunk).strip()
                    chunks.append({
                        "filename": filename,
                        "content": text_chunk,
                        "keywords": extract_keywords(text_chunk)
                    })
                    sub_chunk = []
                    sub_len = 0
            if sub_chunk:
                text_chunk = "\n".join(sub_chunk).strip()
                chunks.append({
                    "filename": filename,
                    "content": text_chunk,
                    "keywords": extract_keywords(text_chunk)
                })
            continue

        if current_len + len(block) > 550 and current_chunk:
            text_chunk = "\n\n".join(current_chunk).strip()
            chunks.append({
                "filename": filename,
                "content": text_chunk,
                "keywords": extract_keywords(text_chunk)
            })
            current_chunk = [block]
            current_len = len(block)
        else:
            current_chunk.append(block)
            current_len += len(block)

    if current_chunk:
        text_chunk = "\n\n".join(current_chunk).strip()
        chunks.append({
            "filename": filename,
            "content": text_chunk,
            "keywords": extract_keywords(text_chunk)
        })

    return chunks


def reload_payloads(force: bool = False) -> None:
    """Verifica si hubo cambios en los archivos y recarga los fragmentos en memoria."""
    global _CHUNKS_CACHE, _FILES_MTIME

    if not os.path.exists(PAYLOADS_DIR):
        os.makedirs(PAYLOADS_DIR, exist_ok=True)
        _CHUNKS_CACHE = []
        _FILES_MTIME = {}
        return

    current_files = {}
    for filename in os.listdir(PAYLOADS_DIR):
        if filename.endswith(".txt") or filename.endswith(".md"):
            filepath = os.path.join(PAYLOADS_DIR, filename)
            try:
                current_files[filename] = os.path.getmtime(filepath)
            except OSError:
                continue

    # Si nada cambió y no es forzado, reusar caché existente
    if not force and current_files == _FILES_MTIME and _CHUNKS_CACHE:
        return

    new_chunks = []
    for filename in current_files:
        filepath = os.path.join(PAYLOADS_DIR, filename)
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                new_chunks.extend(_chunk_content(f.read(), filename))
        except Exception as e:
            print(f"[!] Error leyendo {filename}: {e}")

    _CHUNKS_CACHE = new_chunks
    _FILES_MTIME = current_files


def get_relevant_context(query: str, top_k: int = 2, min_score: int = 3) -> Tuple[str, List[str]]:
    """
    Busca los fragmentos más relevantes para la consulta del usuario.
    Retorna (contexto_formateado, lista_de_archivos_fuente).
    Si la consulta no coincide con ninguna nota, retorna ("", []).
    """
    reload_payloads()
    
    if not _CHUNKS_CACHE:
        return "", []

    query_keywords = extract_keywords(query)
    if not query_keywords:
        return "", []

    scored_chunks = []
    min_required_matches = 2 if len(query_keywords) >= 2 else 1

    for chunk in _CHUNKS_CACHE:
        common = query_keywords.intersection(chunk["keywords"])
        if len(common) < min_required_matches:
            continue

        # Puntuación: 3 puntos por cada palabra clave única coincidente
        score = len(common) * 3
        # Bonus si la consulta comparte términos exactos de longitud >= 4
        for word in common:
            if len(word) >= 4:
                score += 1
        scored_chunks.append((score, chunk))

    if not scored_chunks:
        return "", []

    scored_chunks.sort(key=lambda x: x[0], reverse=True)

    top_score = scored_chunks[0][0]
    if top_score < min_score:
        return "", []

    # Umbral dinámico: solo mantener fragmentos que alcancen al menos el 60% de la puntuación máxima
    dynamic_threshold = max(min_score, int(top_score * 0.6))
    selected = [item for item in scored_chunks if item[0] >= dynamic_threshold][:top_k]

    sources = list(dict.fromkeys(item[1]["filename"] for item in selected))
    formatted_chunks = [f"[{item[1]['filename']}]:\n{item[1]['content']}" for item in selected]
    
    return "\n\n".join(formatted_chunks), sources


def get_payload_stats() -> Dict[str, int]:
    """Retorna estadísticas de la base de conocimiento cargada."""
    reload_payloads()
    return {
        "files_count": len(_FILES_MTIME),
        "chunks_count": len(_CHUNKS_CACHE)
    }