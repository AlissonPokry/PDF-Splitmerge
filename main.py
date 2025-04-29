import tkinterdnd2 as tkdnd
from interface.UI import PDFMergerApp

if __name__ == "__main__":
    root = tkdnd.Tk()
    app = PDFMergerApp(root)
    root.mainloop()