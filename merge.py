from PyPDF2 import PdfMerger

class PDFMerger:
    def merge_pdfs(self, pdf_files, output_file):
        merger = PdfMerger()
        for pdf in pdf_files:
            merger.append(pdf)
        merger.write(output_file)
        merger.close()