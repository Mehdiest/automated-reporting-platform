from docx import Document
import pdfplumber


class FileExtractor:

    @staticmethod
    def extract(file, file_type: str) -> str:
        """
        Unified interface for extracting text from different file types.
        """

        if file_type == "docx":
            return FileExtractor._extract_docx(file)

        if file_type == "pdf":
            return FileExtractor._extract_pdf(file)

        if file_type == "txt":
            return FileExtractor._extract_txt(file)

        raise ValueError(f"Unsupported file type: {file_type}")

    @staticmethod
    def _extract_docx(file) -> str:
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

    @staticmethod
    def _extract_pdf(file) -> str:
        text = []
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
        return "\n".join(text)

    @staticmethod
    def _extract_txt(file) -> str:
        return file.read().decode("utf-8", errors="ignore")