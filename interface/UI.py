import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
from functions.merge import PDFMerger
from functions.split import PDFSplitter
import tkinterdnd2 as tkdnd
from interface.config import * 
from handlers.file_handler import FileHandler
from handlers.listbox_handler import ListboxHandler

class PDFMergerApp:
    def __init__(self, root):
        if not isinstance(root, tkdnd.Tk):
            self.root = tkdnd.Tk()
        else:
            self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.pdf_files = []
        self.merger = PDFMerger()
        self.splitter = PDFSplitter()
        self.file_handler = FileHandler()
        self.listbox_handler = ListboxHandler()

        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding=DEFAULT_PADDING)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create top button frame
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=BUTTON_PADDING)
        
        ttk.Button(button_frame, text="Select PDF Files", command=self.select_files).pack(side=tk.LEFT, padx=BUTTON_PADDING)
        ttk.Button(button_frame, text="Remove Selected", command=self.remove_selected).pack(side=tk.LEFT, padx=BUTTON_PADDING)
        ttk.Button(button_frame, text="Sort A-Z", command=self.sort_files_alphabetically).pack(side=tk.LEFT, padx=BUTTON_PADDING)
        ttk.Button(button_frame, text="Sort 1-9", command=self.sort_files_numerically).pack(side=tk.LEFT, padx=BUTTON_PADDING)

        # Create listbox to show selected files with drag & drop support
        self.file_listbox = tk.Listbox(self.main_frame, width=LISTBOX_WIDTH, height=LISTBOX_HEIGHT, selectmode=tk.EXTENDED)
        self.file_listbox.pack(pady=BUTTON_PADDING, fill=tk.BOTH, expand=True)
        
        # Bind keyboard events for selection
        self.file_listbox.bind('<Control-Button-1>', self.ctrl_click)
        self.file_listbox.bind('<Shift-Button-1>', self.shift_click)
        self.last_selection = None  # Track last selected item for Shift+Click

        # Add tooltip/help label
        help_label = ttk.Label(self.main_frame, text=HELP_TEXT, foreground='gray')
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
        bottom_frame.pack(side=tk.BOTTOM, pady=BUTTON_PADDING)
        
        # Create a sub-frame for the buttons to keep them together
        buttons_container = ttk.Frame(bottom_frame)
        buttons_container.pack(expand=True)
        
        ttk.Button(buttons_container, text="Merge PDF files", command=self.merge_pdfs).pack(side=tk.LEFT, padx=BUTTON_PADDING)
        ttk.Button(buttons_container, text="Split PDF", command=self.split_pdf).pack(side=tk.LEFT, padx=BUTTON_PADDING)

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Select PDF files",
            filetypes=PDF_FILTER
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

    def handle_pdf_merge(self):
        if not self.pdf_files:
            tk.messagebox.showwarning("Warning", "Please select PDF files first!")
            return

        output_file = filedialog.asksaveasfilename(
            initialfile=DEFAULT_OUTPUT_NAME,
            defaultextension=".pdf",
            filetypes=PDF_FILTER
        )

        if output_file:
            try:
                self.merger.merge_pdf_files(self.pdf_files, output_file)
                tk.messagebox.showinfo("Success", "PDFs merged successfully!")
                os.startfile(output_file)
            except Exception as e:
                tk.messagebox.showerror("Error", f"An error occurred: {str(e)}")

    merge_pdfs = handle_pdf_merge

    def split_pdf(self):
        input_file = filedialog.askopenfilename(
            title="Select PDF file to split",
            filetypes=PDF_FILTER
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
        dropped_files = self.file_handler.process_dropped_files(event.data)
        if dropped_files:
            self.pdf_files.extend(dropped_files)
            self.update_listbox()
        else:
            messagebox.showwarning("Warning", "Please drop only PDF files!")

    def sort_files_alphabetically(self):
        if self.pdf_files:
            self.pdf_files = self.file_handler.sort_files_alphabetically(self.pdf_files)
            self.update_listbox()

    def sort_files_numerically(self):
        if self.pdf_files:
            self.pdf_files = self.file_handler.sort_files_numerically(self.pdf_files)
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
            self.pdf_files = self.listbox_handler.handle_drag_selection(
                self.file_listbox,
                self.drag_start_indices,
                drop_index,
                self.pdf_files
            )
            self.update_listbox()
            
            # Restore selection
            self.file_listbox.selection_clear(0, tk.END)
            for i in range(len(self.drag_start_indices)):
                self.file_listbox.selection_set(drop_index + i)
            
            self.drag_start_indices = None