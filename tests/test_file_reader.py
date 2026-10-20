import unittest
from file_reader import extract_keywords, _chunk_content, get_relevant_context


class TestFileReader(unittest.TestCase):

    def test_extract_keywords_short_commands(self):
        # Asegurar que comandos de 2 letras técnicos no sean filtrados
        keywords = extract_keywords("como usar el comando ip y ls en linux")
        self.assertIn("ip", keywords)
        self.assertIn("ls", keywords)
        self.assertIn("linux", keywords)
        # Asegurar que palabras vacías comunes sean eliminadas
        self.assertNotIn("el", keywords)
        self.assertNotIn("como", keywords)
        self.assertNotIn("en", keywords)

    def test_chunk_content_splits_paragraphs(self):
        sample = "Párrafo 1 con info de redes.\n\nSegundo bloque con comandos nmap.\n\nTercer bloque."
        chunks = _chunk_content(sample, "test.txt")
        self.assertGreaterEqual(len(chunks), 1)
        self.assertEqual(chunks[0]["filename"], "test.txt")
        self.assertIn("content", chunks[0])
        self.assertIn("keywords", chunks[0])

    def test_get_relevant_context_empty_query(self):
        context, sources = get_relevant_context("")
        self.assertEqual(context, "")
        self.assertEqual(sources, [])

    def test_get_relevant_context_unrelated_query(self):
        # Una consulta que no tenga nada que ver con los payloads existentes
        context, sources = get_relevant_context("receta para cocinar fideos con salsa")
        self.assertEqual(context, "")
        self.assertEqual(sources, [])


if __name__ == "__main__":
    unittest.main()
