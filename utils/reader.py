from PyPDF2 import PdfReader
from docx import Document

class Reader:
    """
    Lớp dùng để đọc nội dung từ tệp PDF và DOCX.
    """

    def __init__(self, file):
        self.file = file

    def read_pdf(self):
        """Đọc văn bản từ file PDF"""
        text = ""
        try:
            pdf_reader = PdfReader(self.file)
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted
        except Exception as e:
            print('Lỗi khi đọc file PDF:', e)
        return text

    def read_docx(self):
        """Đọc văn bản từ file DOCX"""
        text = ""
        try:
            doc = Document(self.file)
            print("Tải file DOCX thành công!")
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            print('Lỗi khi đọc file DOCX:', e)
        return text

    def read(self):
        """Tự động xác định định dạng và đọc file"""
        if self.file.name.endswith(".pdf"):
            return self.read_pdf()
        elif self.file.name.endswith(".docx"):
            return self.read_docx()
        else:
            print("Định dạng không được hỗ trợ.")
            return None
