import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
from merge import PDFMerger
from split import PDFSplitter
import tkinterdnd2 as tkdnd  # New import

class PDFMergerApp:
    def __init__(self, root):
        if not isinstance(root, tkdnd.Tk):
            self.root = tkdnd.Tk()
        else:
            self.root = root
        self.root.title("PDF Merger (by Alisson Pokrywiecki)")
        self.root.geometry("600x400")
        self.pdf_files = []
        self.merger = PDFMerger()
        self.splitter = PDFSplitter()

        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create top button frame
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Select PDF Files", command=self.select_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Remove Selected", command=self.remove_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Sort A-Z", command=self.sort_files_alphabetically).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Sort 1-9", command=self.sort_files_numerically).pack(side=tk.LEFT, padx=5)

        # Create listbox to show selected files with drag & drop support
        self.file_listbox = tk.Listbox(self.main_frame, width=70, height=15, selectmode=tk.EXTENDED)
        self.file_listbox.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Bind keyboard events for selection
        self.file_listbox.bind('<Control-Button-1>', self.ctrl_click)
        self.file_listbox.bind('<Shift-Button-1>', self.shift_click)
        self.last_selection = None  # Track last selected item for Shift+Click

        # Add tooltip/help label
        help_text = "Use Ctrl+Click for multiple selection or Shift+Click for range selection"
        help_label = ttk.Label(self.main_frame, text=help_text, foreground='gray')
        help_label.pack(pady=(0, 5))
        
        # Configure external drag & drop
        self.file_listbox.drop_target_register(tkdnd.DND_FILES)
        self.file_listbox.dnd_bind('<<Drop>>', self.handle_drop)
        
        # Configure internal drag & drop for reordering
        self.drag_start_indices = None
        self.file_listbox.bind('<Button-1>', self.on_drag_start)
        self.file_listbox.bind('<B1-Motion>', self.on_drag_motion)
        self.file_listbox.bind('<ButtonRelease-1>', self.on_drag_release)

        # Create bottom button frame
        bottom_frame = ttk.Frame(self.main_frame)
        bottom_frame.pack(side=tk.BOTTOM, pady=10)
        
        # Create a sub-frame for the buttons to keep them together
        buttons_container = ttk.Frame(bottom_frame)
        buttons_container.pack(expand=True)
        
        ttk.Button(buttons_container, text="Merge PDF files", command=self.merge_pdfs).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_container, text="Split PDF", command=self.split_pdf).pack(side=tk.LEFT, padx=5)

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Select PDF files",
            filetypes=[("PDF files", "*.pdf")]
        )
        self.pdf_files = list(files)
        self.update_listbox()

    def update_listbox(self):
        self.file_listbox.delete(0, tk.END)
        for file in self.pdf_files:
            self.file_listbox.insert(tk.END, os.path.basename(file))

    def remove_selected(self):
        selected_indices = self.file_listbox.curselection()
        for index in reversed(selected_indices):
            del self.pdf_files[index]
        self.update_listbox()

    def merge_pdfs(self):
        if not self.pdf_files:
            tk.messagebox.showwarning("Warning", "Please select PDF files first!")
            return

        output_file = filedialog.asksaveasfilename(
            initialfile="mergedPDF.pdf",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )

        if output_file:
            try:
                self.merger.merge_pdfs(self.pdf_files, output_file)
                tk.messagebox.showinfo("Success", "PDFs merged successfully!")
                os.startfile(output_file)
            except Exception as e:
                tk.messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def split_pdf(self):
        input_file = filedialog.askopenfilename(
            title="Select PDF file to split",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if input_file:
            try:
                output_dir = self.splitter.split_pdf(input_file)
                if output_dir:  # Only show success message if splitting occurred
                    tk.messagebox.showinfo("Success", f"PDF split successfully!\nFiles saved in: {output_dir}")
                    os.startfile(output_dir)
            except Exception as e:
                tk.messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def handle_drop(self, event):
        files = event.data
        # Convert the dropped files string to a list and filter for PDFs
        dropped_files = [f.strip('{}') for f in files.split('} {') if f.lower().endswith('.pdf')]
        if dropped_files:
            self.pdf_files.extend(dropped_files)
            self.update_listbox()
        else:
            messagebox.showwarning("Warning", "Please drop only PDF files!")

    def extract_number(self, filename):
        # Extract numbers from filename
        numbers = ''.join(char for char in filename if char.isdigit())
        return int(numbers) if numbers else float('inf')  # If no numbers, put at end

    def sort_files_alphabetically(self):
        if self.pdf_files:
            self.pdf_files.sort(key=lambda x: os.path.basename(x).lower())
            self.update_listbox()

    def sort_files_numerically(self):
        if self.pdf_files:
            self.pdf_files.sort(key=lambda x: self.extract_number(os.path.basename(x)))
            self.update_listbox()

    def ctrl_click(self, event):
        index = self.file_listbox.nearest(event.y)
        if index in self.file_listbox.curselection():
            self.file_listbox.selection_clear(index)
        else:
            self.file_listbox.selection_set(index)
        self.last_selection = index
        return 'break'  # Prevent default handling

    def shift_click(self, event):
        current_index = self.file_listbox.nearest(event.y)
        if self.last_selection is not None:
            start = min(self.last_selection, current_index)
            end = max(self.last_selection, current_index)
            self.file_listbox.selection_clear(0, tk.END)
            for i in range(start, end + 1):
                self.file_listbox.selection_set(i)
        else:
            self.file_listbox.selection_set(current_index)
        self.last_selection = current_index
        return 'break'  # Prevent default handling

    def on_drag_start(self, event):
        clicked_index = self.file_listbox.nearest(event.y)
        
        # Only start drag if clicking on a selected item
        if not self.file_listbox.curselection() or clicked_index not in self.file_listbox.curselection():
            self.file_listbox.selection_clear(0, tk.END)
            self.file_listbox.selection_set(clicked_index)
        
        self.drag_start_indices = self.file_listbox.curselection()
        self.last_selection = clicked_index

    def on_drag_motion(self, event):
        if self.drag_start_indices:
            current_index = self.file_listbox.nearest(event.y)
            # Visual feedback showing where items will be inserted
            self.file_listbox.selection_clear(0, tk.END)
            self.file_listbox.selection_set(current_index)

    def on_drag_release(self, event):
        if self.drag_start_indices:
            drop_index = self.file_listbox.nearest(event.y)
            
            # Don't move if drop index is in selected indices
            if drop_index not in self.drag_start_indices:
                # Convert to list and sort in original order
                indices = sorted(list(self.drag_start_indices))
                
                # Collect files in their original order
                files_to_move = [self.pdf_files[i] for i in indices]
                
                # Remove files from end to not affect remaining indices
                for i in reversed(indices):
                    del self.pdf_files[i]
                
                # Adjust drop index based on whether we're moving up or down
                if drop_index > indices[-1]:
                    drop_index -= len(indices)
                
                # Insert all files at once at the new position
                self.pdf_files[drop_index:drop_index] = files_to_move
                
                # Update the listbox
                self.update_listbox()
                
                # Restore selection at new positions
                self.file_listbox.selection_clear(0, tk.END)
                for i in range(len(files_to_move)):
                    self.file_listbox.selection_set(drop_index + i)
            
            self.drag_start_indices = None