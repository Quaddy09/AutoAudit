import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ──────────────────────────────────────────────────
# 1. Helper: Parse and clean the Excel audit sheet
# ──────────────────────────────────────────────────
def load_and_parse_excel(filepath):
    # Read whole sheet (no header), we'll find our header row by matching column names
    raw = pd.read_excel(filepath, header=None)
    # Find the row that contains 'Control Name' header
    header_row = raw.apply(lambda row: row.astype(str).str.contains('Control Name').any(), axis=1).idxmax()
    df = pd.read_excel(filepath, header=header_row)
    
    # We expect at least these columns:
    expected = {
        'Klausa/Annex':   'Clause/Annex',
        'Control Name':   'Control Name',
        'Persyaratan':    'Control Description',
        'Pertanyaan':     'Audit Question',
        'Fungsi':         'Responsible Function',
        'Hasil Observasi':'Status Observation'
    }
    # Rename if present
    rename_map = {orig: new for orig,new in expected.items() if orig in df.columns}
    df = df.rename(columns=rename_map)
    
    # Keep only renamed columns
    keep = list(rename_map.values())
    df = df[keep].dropna(how='all')  # drop empty rows
    
    # Map Indonesian status → (English, score, level)
    status_map = {
        'Belum Dilakukan':        ('Not Implemented',      3, 'High'),
        'Dilakukan Sebagian':      ('Partially Implemented',2, 'Medium'),
        'Sudah Dilakukan':         ('Implemented',          1, 'Low')
    }
    # Apply mapping (unknowns get zeros/Unknown)
    df[['Status English','Risk Score','Risk Level']] = df['Status Observation'] \
        .apply(lambda s: status_map.get(s, ('Unknown',0,'Unknown'))) \
        .tolist()
    
    return df

# ──────────────────────────────────────────────────
# 2. Helpers: Export functions
# ──────────────────────────────────────────────────
def export_csv(df, path):
    df.to_csv(path, index=False)
    messagebox.showinfo("CSV Exported", f"Saved to:\n{path}")

def export_pdf(df, path):
    buf = BytesIO()
    pdf = canvas.Canvas(buf, pagesize=letter)
    w, h = letter
    y = h - 40
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(30, y, "AutoAudit – IT Audit Report")
    pdf.setFont("Helvetica", 10)
    y -= 30
    for _, r in df.iterrows():
        line = (f"{r['Clause/Annex']} | {r['Control Name']} | "
                f"{r['Status English']} → {r['Risk Level']}")
        pdf.drawString(30, y, line)
        y -= 15
        if y < 40:
            pdf.showPage()
            y = h - 40
    pdf.save()
    with open(path, 'wb') as f:
        f.write(buf.getvalue())
    messagebox.showinfo("PDF Exported", f"Saved to:\n{path}")

# ──────────────────────────────────────────────────
# 3. Main GUI Application
# ──────────────────────────────────────────────────
class AutoAuditApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AutoAudit – IT Audit Automation")
        self.df = None
        
        # Top buttons
        bar = ttk.Frame(self)
        bar.pack(fill=tk.X, pady=5)
        ttk.Button(bar, text="Load Excel…",   command=self.load_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(bar, text="Export CSV…",   command=self.save_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(bar, text="Export PDF…",   command=self.save_pdf).pack(side=tk.LEFT, padx=5)
        
        # Table view
        cols = ("Clause","Name","Status","Risk")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c,w in zip(cols, (100,200,150,80)):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Chart area
        self.chart_frame = ttk.Frame(self)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def load_excel(self):
        path = filedialog.askopenfilename(
            filetypes=[("Excel files","*.xlsx"),("All files","*.*")]
        )
        if not path: return
        try:
            self.df = load_and_parse_excel(path)
        except Exception as e:
            messagebox.showerror("Load Error", str(e))
            return
        
        # Populate table
        for r in self.tree.get_children(): self.tree.delete(r)
        for _, r in self.df.iterrows():
            self.tree.insert("", tk.END, values=(
                r['Clause/Annex'], r['Control Name'],
                r['Status English'], r['Risk Level']
            ))
        # Show chart
        self.show_chart()

    def show_chart(self):
        for w in self.chart_frame.winfo_children(): w.destroy()
        if self.df is None: return
        counts = self.df['Risk Level'].value_counts().reindex(['Low','Medium','High'], fill_value=0)
        fig, ax = plt.subplots(figsize=(5,3))
        counts.plot(kind='bar', ax=ax)
        ax.set_title("Risk Level Distribution")
        ax.set_ylabel("Number of Controls")
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def save_csv(self):
        if self.df is None:
            messagebox.showwarning("No Data","Load an Excel file first.")
            return
        p = filedialog.asksaveasfilename(defaultextension=".csv")
        if p: export_csv(self.df, p)

    def save_pdf(self):
        if self.df is None:
            messagebox.showwarning("No Data","Load an Excel file first.")
            return
        p = filedialog.asksaveasfilename(defaultextension=".pdf")
        if p: export_pdf(self.df, p)

if __name__ == "__main__":
    app = AutoAuditApp()
    app.geometry("800x600")
    app.mainloop()
