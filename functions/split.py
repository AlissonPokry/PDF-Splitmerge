from PyPDF2 import PdfReader, PdfWriter
import os
from tkinter import messagebox

class PDFSplitter:
    def split_pdf(self, input_file):
        # Create output directory with PDF name
        pdf_name = os.path.splitext(os.path.basename(input_file))[0]
        output_dir = os.path.join(os.path.dirname(input_file), pdf_name)
        
        # Read the PDF
        pdf = PdfReader(input_file)
        
        # Check if PDF has only one page
        if len(pdf.pages) <= 1:
            messagebox.showwarning("Warning", "Cannot split a single-page PDF file!")
            return None
        
        # Create directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Split each page into a separate PDF
        for page_num in range(len(pdf.pages)):
            pdf_writer = PdfWriter()
            pdf_writer.add_page(pdf.pages[page_num])
            
            # Create output file path
            output_file = os.path.join(output_dir, f'page_{page_num + 1}.pdf')
            
            # Save the page as a separate PDF
            with open(output_file, 'wb') as out_file:
                pdf_writer.write(out_file)
                
        return output_dir