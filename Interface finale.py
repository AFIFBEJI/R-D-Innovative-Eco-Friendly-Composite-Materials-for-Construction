import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
import tkinter as tk
import threading
import os
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from matplotlib.lines import Line2D

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# ------------------- SpreadsheetFrame (tableur principal) -------------------
class SpreadsheetFrame(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.data = {}
        self.columns = []
        self.rows = 0
        self.entries = {}
        self.setup_ui()

    def setup_ui(self):
        toolbar = ctk.CTkFrame(self)
        toolbar.pack(fill="x", pady=(0, 5))
        ctk.CTkButton(toolbar, text="+ Colonne", command=self.add_column, fg_color="#27AE60", width=100).pack(side="left", padx=2)
        ctk.CTkButton(toolbar, text="- Colonne", command=self.remove_column, fg_color="#E74C3C", width=100).pack(side="left", padx=2)
        ctk.CTkButton(toolbar, text="+ Ligne", command=self.add_row, fg_color="#3498DB", width=100).pack(side="left", padx=2)
        ctk.CTkButton(toolbar, text="- Ligne", command=self.remove_row, fg_color="#E67E22", width=100).pack(side="left", padx=2)
        
        # --- MODIFIÉ ---
        ctk.CTkButton(toolbar, text="📂 Charger Fichier", command=self.load_file, fg_color="#9B59B6", width=130).pack(side="left", padx=2)
        ctk.CTkButton(toolbar, text="💾 Sauvegarder Fichier", command=self.save_file, fg_color="#01704B", width=140).pack(side="left", padx=2)
        # --- FIN MODIFIÉ ---
        
        self.sheet_frame = ctk.CTkFrame(self)
        self.sheet_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.canvas = tk.Canvas(self.sheet_frame, bg="white", highlightthickness=0)
        self.v_scrollbar = ttk.Scrollbar(self.sheet_frame, orient="vertical", command=self.canvas.yview)
        self.h_scrollbar = ttk.Scrollbar(self.sheet_frame, orient="horizontal", command=self.canvas.xview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")
        
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.v_scrollbar.pack(side="right", fill="y")
        self.h_scrollbar.pack(side="bottom", fill="x")
        
        self.initialize_empty_sheet()

    def initialize_empty_sheet(self):
        self.columns = ["A", "B", "C"]
        self.rows = 5
        self.rebuild_sheet()

    def add_column(self):
        dialog = ctk.CTkInputDialog(text="Nom de la nouvelle colonne:", title="Ajouter Colonne")
        col_name = dialog.get_input()
        if col_name and col_name.strip():
            self.columns.append(col_name.strip())
            self.rebuild_sheet()

    def remove_column(self):
        if len(self.columns) > 1:
            self.columns.pop()
            self.rebuild_sheet()
        else:
            messagebox.showwarning("Attention", "Il doit y avoir au moins une colonne")

    def add_row(self):
        self.rows += 1
        self.rebuild_sheet()

    def remove_row(self):
        if self.rows > 1:
            self.rows -= 1
            self.rebuild_sheet()
        else:
            messagebox.showwarning("Attention", "Il doit y avoir au moins une ligne")

    def rebuild_sheet(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        self.entries = {}
        
        # Create headers
        for col_idx, col_name in enumerate(self.columns):
            header_entry = tk.Entry(self.scrollable_frame, width=12, font=("Arial", 10, "bold"), justify="center", bg="#f0f0f0")
            header_entry.grid(row=0, column=col_idx+1, padx=1, pady=1, sticky="ew")
            header_entry.insert(0, col_name)
            header_entry.bind("<FocusOut>", lambda e, idx=col_idx: self.update_column_name(idx, e.widget.get()))
            header_entry.bind("<Return>", lambda e, idx=col_idx: self.update_column_name(idx, e.widget.get()))
            
        # Create rows
        for row_idx in range(self.rows):
            row_label = tk.Label(self.scrollable_frame, text=str(row_idx+1), width=4, bg="#f0f0f0", font=("Arial", 9, "bold"))
            row_label.grid(row=row_idx+1, column=0, padx=1, pady=1, sticky="ew")
            
            for col_idx in range(len(self.columns)):
                entry = tk.Entry(self.scrollable_frame, width=12, justify="center")
                entry.grid(row=row_idx+1, column=col_idx+1, padx=1, pady=1, sticky="ew")
                
                if (row_idx, col_idx) in self.data:
                    entry.insert(0, str(self.data[(row_idx, col_idx)]))
                    
                self.entries[(row_idx, col_idx)] = entry
                entry.bind("<FocusOut>", lambda e, r=row_idx, c=col_idx: self.save_cell(r, c, e.widget.get()))
                entry.bind("<Return>", lambda e, r=row_idx, c=col_idx: self.save_cell(r, c, e.widget.get()))

    def update_column_name(self, col_idx, new_name):
        if new_name.strip():
            self.columns[col_idx] = new_name.strip()
            # Update the main app's column selectors
            if hasattr(self.master.master, 'update_column_selectors'):
                self.master.master.update_column_selectors()

    def save_cell(self, row, col, value):
        if value.strip():
            self.data[(row, col)] = value.strip()
        elif (row, col) in self.data:
            del self.data[(row, col)]

    def get_dataframe(self):
        data_dict = {col: [] for col in self.columns}
        for row_idx in range(self.rows):
            for col_idx, col_name in enumerate(self.columns):
                value = self.data.get((row_idx, col_idx), "")
                try:
                    # Try to convert to float, supporting both comma and dot decimals
                    value = float(value.replace(",", ".")) if value else np.nan
                except (ValueError, AttributeError):
                    value = value if value else np.nan
                data_dict[col_name].append(value)
        return pd.DataFrame(data_dict)

    def load_from_dataframe(self, df):
        self.columns = list(df.columns)
        self.rows = len(df)
        self.data = {}
        for row_idx in range(len(df)):
            for col_idx, col_name in enumerate(df.columns):
                value = df.iloc[row_idx, col_idx]
                if pd.notna(value):
                    self.data[(row_idx, col_idx)] = str(value)
        self.rebuild_sheet()
        # Update main app's selectors after loading
        self.after(100, self.master.master.update_column_selectors)

    # --- MÉTHODE MODIFIÉE (anciennement load_csv) ---
    def load_file(self):
        filetypes = [
            ("Fichiers Excel", "*.xlsx *.xls"),
            ("Fichiers CSV", "*.csv"),
            ("Tous les fichiers", "*.*")
        ]
        filepath = filedialog.askopenfilename(filetypes=filetypes)
        if not filepath:
            return
            
        file_ext = os.path.splitext(filepath)[1].lower()
            
        def _load():
            try:
                df = None
                if file_ext == '.csv':
                    # Sniff delimiter
                    with open(filepath, 'r', encoding='utf-8') as f:
                        start = f.read(2048) 
                        delimiter = ";" if start.count(";") > start.count(",") else ","
                    df = pd.read_csv(filepath, sep=delimiter, decimal='.')
                
                elif file_ext in ['.xlsx', '.xls']:
                    # Charge la première feuille par défaut
                    df = pd.read_excel(filepath, sheet_name=0) 
                
                else:
                    self.after(0, lambda: messagebox.showwarning("Type non supporté", f"Le type de fichier '{file_ext}' n'est pas supporté."))
                    return

                if df is not None:
                    self.after(0, lambda: self.load_from_dataframe(df))
                    self.after(0, lambda: messagebox.showinfo("Succès", "Fichier chargé avec succès"))
                    
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Erreur", f"Erreur lors du chargement:\n{str(e)}"))
                
        threading.Thread(target=_load).start()

    # --- MÉTHODE MODIFIÉE (anciennement save_csv) ---
    def save_file(self):
        filetypes = [
            ("Fichier Excel (*.xlsx)", "*.xlsx"),
            ("Fichier CSV (*.csv)", "*.csv")
        ]
        filepath = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=filetypes)
        if not filepath:
            return

        file_ext = os.path.splitext(filepath)[1].lower()
            
        def _save():
            try:
                df = self.get_dataframe()
                
                if file_ext == '.csv':
                    # Utiliser ; comme séparateur pour CSV
                    df.to_csv(filepath, index=False, sep=";", decimal='.')
                
                elif file_ext == '.xlsx':
                    # Sauvegarder en Excel
                    df.to_excel(filepath, index=False, sheet_name="Data", engine='openpyxl')
                
                else:
                    self.after(0, lambda: messagebox.showwarning("Type non supporté", f"Sauvegarde en '{file_ext}' non supportée. Utilisez .xlsx ou .csv"))
                    return
                    
                self.after(0, lambda: messagebox.showinfo("Succès", "Fichier sauvegardé avec succès"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde:\n{str(e)}"))
        
        threading.Thread(target=_save).start()

# ---------------- Fenêtre de graphiques personnalisés ----------------
class CustomGraphsWindow(ctk.CTkToplevel):
    def __init__(self, master, dataframe_getter):
        super().__init__(master)
        self.title("Graphiques personnalisés")
        self.geometry("1200x850")
        self.dataframe_getter = dataframe_getter
        self.configure(fg_color="#f6f8fa")
        self.setup_ui()
        self.fig = None
        self.ax = None
        self.canvas = None

    def setup_ui(self):
        # En-tête stylisé
        header_frame = ctk.CTkFrame(self, fg_color="#0073e6", height=60)
        header_frame.pack(fill="x", pady=0, padx=0)
        ctk.CTkLabel(header_frame, text="📊 Graphiques Personnalisés", 
                     font=('Arial', 20, 'bold'), text_color="white").pack(pady=15)

        # Frame pour le type de graphe et les boutons
        self.graph_type_var = ctk.StringVar(value="Scatter + Line")
        type_frame = ctk.CTkFrame(self, fg_color="transparent")
        type_frame.pack(fill="x", pady=15, padx=15)
        
        ctk.CTkLabel(type_frame, text="Type de graphe :", font=('Arial', 14, 'bold')).pack(side="left", padx=10)
        ctk.CTkOptionMenu(type_frame, variable=self.graph_type_var,
                          values=["Scatter + Line", "Radar (Spider)", "Scatter avec régression"],
                          width=200, font=('Arial', 12)).pack(side="left", padx=10)
        ctk.CTkButton(type_frame, text="🎨 Générer", command=self.generate_graph, 
                      fg_color="#0073e6", hover_color="#005bb5", width=120, height=35,
                      font=('Arial', 13, 'bold')).pack(side="left", padx=10)
        ctk.CTkButton(type_frame, text="💾 Exporter", command=self.export_graph, 
                      fg_color="#27AE60", hover_color="#1e8449", width=120, height=35,
                      font=('Arial', 13, 'bold')).pack(side="left", padx=10)

        # Frame des paramètres
        self.params_frame = ctk.CTkFrame(self, fg_color="#e8f4f8")
        self.params_frame.pack(fill="x", pady=10, padx=15)
        self.dynamic_widgets = []
        self.graph_type_var.trace("w", self.refresh_dynamic_params)
        self.refresh_dynamic_params()

        # Frame du graphique
        self.plot_frame = ctk.CTkFrame(self, fg_color="white")
        self.plot_frame.pack(fill="both", expand=True, padx=15, pady=15)

    def refresh_dynamic_params(self, *args):
        for w in self.dynamic_widgets:
            w.destroy()
        self.dynamic_widgets.clear()
        
        df = self.dataframe_getter()
        if df.empty:
            messagebox.showwarning("Attention", "La feuille de calcul est vide")
            return
            
        cols = df.columns.tolist()
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = [c for c in cols if c not in num_cols]
        
        gtype = self.graph_type_var.get()
        
        if gtype == "Scatter + Line":
            if len(num_cols) < 2:
                messagebox.showwarning("Attention", "Il faut au moins 2 colonnes numériques")
                return
                
            self.x_var = ctk.StringVar(value=num_cols[0])
            self.y_var = ctk.StringVar(value=num_cols[1] if len(num_cols) > 1 else num_cols[0])
            self.cat_var = ctk.StringVar(value=cat_cols[0] if cat_cols else "Aucune")
            
            w1 = ctk.CTkLabel(self.params_frame, text="Axe X :", font=('Arial', 12, 'bold'))
            w1.pack(side="left", padx=10, pady=10)
            w2 = ctk.CTkOptionMenu(self.params_frame, variable=self.x_var, values=num_cols, width=150)
            w2.pack(side="left", padx=5)
            w3 = ctk.CTkLabel(self.params_frame, text="Axe Y :", font=('Arial', 12, 'bold'))
            w3.pack(side="left", padx=10)
            w4 = ctk.CTkOptionMenu(self.params_frame, variable=self.y_var, values=num_cols, width=150)
            w4.pack(side="left", padx=5)
            
            if cat_cols:
                w5 = ctk.CTkLabel(self.params_frame, text="Catégorie :", font=('Arial', 12, 'bold'))
                w5.pack(side="left", padx=10)
                w6 = ctk.CTkOptionMenu(self.params_frame, variable=self.cat_var, 
                                       values=["Aucune"] + cat_cols, width=150)
                w6.pack(side="left", padx=5)
                self.dynamic_widgets += [w1, w2, w3, w4, w5, w6]
            else:
                self.dynamic_widgets += [w1, w2, w3, w4]
                
        elif gtype == "Radar (Spider)":
            if len(num_cols) < 3:
                messagebox.showwarning("Attention", "Il faut au moins 3 colonnes numériques pour un graphe radar")
                return
                
            w1 = ctk.CTkLabel(self.params_frame, text="Colonnes à inclure :", font=('Arial', 12, 'bold'))
            w1.pack(side="left", padx=10, pady=10)
            
            # Frame pour la liste
            list_frame = ctk.CTkFrame(self.params_frame, fg_color="white")
            list_frame.pack(side="left", padx=5, fill="both", expand=True)
            
            w2 = tk.Listbox(list_frame, selectmode="multiple", exportselection=False, 
                           height=min(6, len(num_cols)), font=('Arial', 10))
            for c in num_cols:
                w2.insert("end", c)
            w2.selection_set(0, min(5, len(num_cols)-1))  # Sélectionne les 6 premières
            w2.pack(fill="both", expand=True, padx=2, pady=2)
            
            self.cols_listbox = w2
            self.dynamic_widgets += [w1, list_frame, w2]
            
        elif gtype == "Scatter avec régression":
            if len(num_cols) < 2:
                messagebox.showwarning("Attention", "Il faut au moins 2 colonnes numériques")
                return
                
            self.x_var = ctk.StringVar(value=num_cols[0])
            self.y_var = ctk.StringVar(value=num_cols[1] if len(num_cols) > 1 else num_cols[0])
            self.group_var = ctk.StringVar(value=cat_cols[0] if cat_cols else "Aucun")
            
            w1 = ctk.CTkLabel(self.params_frame, text="Axe X :", font=('Arial', 12, 'bold'))
            w1.pack(side="left", padx=10, pady=10)
            w2 = ctk.CTkOptionMenu(self.params_frame, variable=self.x_var, values=num_cols, width=150)
            w2.pack(side="left", padx=5)
            w3 = ctk.CTkLabel(self.params_frame, text="Axe Y :", font=('Arial', 12, 'bold'))
            w3.pack(side="left", padx=10)
            w4 = ctk.CTkOptionMenu(self.params_frame, variable=self.y_var, values=num_cols, width=150)
            w4.pack(side="left", padx=5)
            
            if cat_cols:
                w5 = ctk.CTkLabel(self.params_frame, text="Grouper par :", font=('Arial', 12, 'bold'))
                w5.pack(side="left", padx=10)
                w6 = ctk.CTkOptionMenu(self.params_frame, variable=self.group_var, 
                                       values=["Aucun"] + cat_cols, width=150)
                w6.pack(side="left", padx=5)
                self.dynamic_widgets += [w1, w2, w3, w4, w5, w6]
            else:
                self.dynamic_widgets += [w1, w2, w3, w4]
        
        # Suppression de la section "Barres groupées"

    def clear_plot(self):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        if self.fig:
            plt.close(self.fig)
            self.fig = None

    def generate_graph(self):
        try:
            self.clear_plot()
            df = self.dataframe_getter()
            
            if df.empty:
                messagebox.showwarning("Attention", "La feuille de calcul est vide")
                return
                
            gtype = self.graph_type_var.get()
            plt.style.use('seaborn-v0_8-whitegrid')
            self.fig, self.ax = plt.subplots(figsize=(10, 7))
            self.fig.patch.set_facecolor('#f6f8fa')
            self.ax.set_facecolor('#ffffff')
            
            if gtype == "Scatter + Line":
                xcol, ycol = self.x_var.get(), self.y_var.get()
                catcol = self.cat_var.get() if hasattr(self, 'cat_var') else "Aucune"
                
                if not xcol or not ycol:
                    messagebox.showwarning("Sélection incomplète", "Veuillez choisir les axes X et Y")
                    return
                
                df_plot = df[[xcol, ycol]].dropna()
                if df_plot.empty:
                    messagebox.showwarning("Attention", "Aucune donnée valide pour ces colonnes")
                    return
                
                colors = plt.cm.Set3(np.linspace(0, 1, 10))
                
                if catcol and catcol != "Aucune" and catcol in df.columns:
                    for idx, (cat, dfg) in enumerate(df.groupby(catcol)):
                        dfg_clean = dfg[[xcol, ycol]].dropna()
                        if not dfg_clean.empty:
                            self.ax.scatter(dfg_clean[xcol], dfg_clean[ycol], s=100, 
                                          edgecolor='black', linewidth=1.5, alpha=0.7,
                                          color=colors[idx % len(colors)], label=str(cat))
                    
                    # Ligne de tendance globale
                    means = df.groupby(xcol)[ycol].mean().reset_index().dropna()
                    if len(means) > 1:
                        self.ax.plot(means[xcol], means[ycol], color='darkblue', 
                                   linewidth=2.5, linestyle='--', alpha=0.8, label='Tendance')
                else:
                    self.ax.scatter(df_plot[xcol], df_plot[ycol], s=100, 
                                  edgecolor='black', linewidth=1.5, alpha=0.7,
                                  color='#3498db')
                    
                    # Ligne de tendance
                    means = df.groupby(xcol)[ycol].mean().reset_index().dropna()
                    if len(means) > 1:
                        self.ax.plot(means[xcol], means[ycol], color='darkred', 
                                   linewidth=2.5, linestyle='--', alpha=0.8)
                
                self.ax.set_xlabel(xcol, fontsize=14, fontweight='bold')
                self.ax.set_ylabel(ycol, fontsize=14, fontweight='bold')
                self.ax.set_title(f'Graphique Scatter + Line: {ycol} vs {xcol}', 
                                fontsize=16, fontweight='bold', pad=20)
                self.ax.tick_params(axis='both', labelsize=11)
                self.ax.grid(True, alpha=0.3, linestyle='--')
                if catcol and catcol != "Aucune" and catcol in df.columns:
                    self.ax.legend(title=catcol, fontsize=11, framealpha=0.95)
                
            elif gtype == "Radar (Spider)":
                if not hasattr(self, 'cols_listbox'):
                    messagebox.showwarning("Erreur", "Paramètres non initialisés")
                    return
                
                cols = [self.cols_listbox.get(i) for i in self.cols_listbox.curselection()]
                if len(cols) < 3:
                    messagebox.showwarning("Sélection incomplète", "Sélectionnez au moins 3 colonnes")
                    return
                
                dfnum = df[cols]
                if dfnum.empty:
                    messagebox.showwarning("Attention", "Aucune donnée valide pour ces colonnes")
                    return

                # Configuration du graphique radar
                self.fig, self.ax = plt.subplots(figsize=(12, 8), subplot_kw=dict(polar=True))
                self.fig.patch.set_facecolor('#ffffff')
                
                # Nombre de lignes et angles
                angles = np.linspace(0, 2*np.pi, len(dfnum), endpoint=False)
                
                # Ajouter les numéros des lignes comme étiquettes
                self.ax.set_thetagrids(np.degrees(angles), 
                                      [f"{i+1}" for i in range(len(dfnum))], 
                                      fontsize=10)
                
                # Ajouter les cercles concentriques avec valeurs numériques en rouge
                max_value = dfnum.max().max()
                levels = np.linspace(0, max_value, 5)
                self.ax.set_rgrids(levels, 
                                  [f"{v:.1f}" for v in levels], 
                                  color='red', 
                                  fontsize=9)
                
                # Tracer les données pour chaque colonne
                for idx, col in enumerate(cols):
                    values = dfnum[col].values.tolist()
                    values += values[:1]  # Fermer le polygone
                    angles_plot = np.concatenate([angles, [angles[0]]])
                    
                    self.ax.plot(angles_plot, values, 'o-', 
                                linewidth=2, 
                                label=col,  # Utiliser le nom de la colonne comme légende
                                markersize=6)
                    self.ax.fill(angles_plot, values, alpha=0.1)
                
                # Personnalisation
                self.ax.set_title("Graphique Radar (Spider)", 
                                  pad=20, 
                                  fontsize=14, 
                                  fontweight='bold')
                
                # Légende avec les noms des colonnes
                self.ax.legend(loc='center left', 
                               bbox_to_anchor=(1.2, 0.5),
                               fontsize=10,
                               frameon=True,
                               facecolor='white',
                               edgecolor='gray',
                               framealpha=1,
                               shadow=True)
                
                # Grille
                self.ax.grid(True, color='gray', linestyle=':', alpha=0.5)
                
                # Ajuster la mise en page
                self.fig.tight_layout()
            
            elif gtype == "Scatter avec régression":
                xcol, ycol = self.x_var.get(), self.y_var.get()
                groupcol = self.group_var.get() if hasattr(self, 'group_var') else "Aucun"
                
                if not xcol or not ycol:
                    messagebox.showwarning("Sélection incomplète", "Veuillez choisir les axes X et Y")
                    return
                
                df_plot = df[[xcol, ycol]].dropna()
                if df_plot.empty:
                    messagebox.showwarning("Attention", "Aucune donnée valide pour ces colonnes")
                    return
                
                colors = plt.cm.tab10.colors
                
                if groupcol and groupcol != "Aucun" and groupcol in df.columns:
                    groups = df[groupcol].dropna().unique()
                    for i, group in enumerate(groups):
                        dfg = df[df[groupcol] == group][[xcol, ycol]].dropna()
                        if len(dfg) > 0:
                            color = colors[i % len(colors)]
                            self.ax.scatter(dfg[xcol], dfg[ycol], s=100, label=str(group),
                                          color=color, edgecolor='black', linewidth=1.5, alpha=0.7)
                            
                            if len(dfg) > 1:
                                X = dfg[xcol].values.reshape(-1, 1)
                                Y = dfg[ycol].values
                                model = LinearRegression().fit(X, Y)
                                x_range = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
                                y_pred = model.predict(x_range)
                                self.ax.plot(x_range, y_pred, linestyle='--', color=color, 
                                           linewidth=2.5, alpha=0.8)
                                
                                r2 = model.score(X, Y)
                                eq_str = f'y = {model.coef_[0]:.2f}x + {model.intercept_:.2f}\nR² = {r2:.3f}'
                                self.ax.text(0.05, 0.95 - i*0.08, eq_str, transform=self.ax.transAxes,
                                           fontsize=10, verticalalignment='top',
                                           bbox=dict(boxstyle='round', facecolor=color, alpha=0.3))
                else:
                    self.ax.scatter(df_plot[xcol], df_plot[ycol], s=100, color='#3498db',
                                  edgecolor='black', linewidth=1.5, alpha=0.7)
                    
                    if len(df_plot) > 1:
                        X = df_plot[xcol].values.reshape(-1, 1)
                        Y = df_plot[ycol].values
                        model = LinearRegression().fit(X, Y)
                        x_range = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
                        y_pred = model.predict(x_range)
                        self.ax.plot(x_range, y_pred, linestyle='--', color='darkred',
                                   linewidth=2.5, alpha=0.8, label='Régression')
                        
                        r2 = model.score(X, Y)
                        eq_str = f'y = {model.coef_[0]:.2f}x + {model.intercept_:.2f}\nR² = {r2:.3f}'
                        self.ax.text(0.05, 0.95, eq_str, transform=self.ax.transAxes,
                                   fontsize=11, verticalalignment='top',
                                   bbox=dict(boxstyle='round', facecolor='lightyellow', 
                                           edgecolor='darkred', linewidth=2, alpha=0.9))
                
                self.ax.set_xlabel(xcol, fontsize=14, fontweight='bold')
                self.ax.set_ylabel(ycol, fontsize=14, fontweight='bold')
                self.ax.set_title(f'Scatter avec Régression: {ycol} vs {xcol}',
                                fontsize=16, fontweight='bold', pad=20)
                self.ax.tick_params(axis='both', labelsize=11)
                self.ax.grid(True, alpha=0.3, linestyle='--')
                self.ax.legend(fontsize=11, framealpha=0.95)
            
            self.fig.tight_layout()
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
            self.canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la génération du graphique:\n{str(e)}")
            import traceback
            traceback.print_exc()

    def export_graph(self):
        if not self.fig:
            messagebox.showinfo("Pas de graphe", "Veuillez générer un graphe avant d'exporter.")
            return
        
        filetypes = [("PNG", "*.png"), ("PDF", "*.pdf"), ("SVG", "*.svg"), ("JPEG", "*.jpg")]
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=filetypes)
        if file_path:
            try:
                self.fig.savefig(file_path, dpi=300, bbox_inches='tight', facecolor='white')
                messagebox.showinfo("Succès", f"Graphique exporté avec succès:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'export:\n{str(e)}")

# --------------------------- Classe principale ---------------------------
class ProjectApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Analyse et Optimisation RSM - Feuille de Calcul")
        self.geometry("1400x800")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.spreadsheet = SpreadsheetFrame(self.left_frame)
        self.spreadsheet.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        self.setup_graph_controls()
        self.setup_graph_and_stats()
        self._colorbar = None

    def setup_graph_controls(self):
        control_frame = ctk.CTkFrame(self.right_frame)
        control_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # En-tête avec titre et bouton graphiques personnalisés
        header_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(header_frame, text="Configuration du Graphique 3D", 
                     font=("Arial", 14, "bold")).pack(side="left", padx=10)
        
        # Bouton Graphiques Personnalisés à droite dans l'en-tête
        ctk.CTkButton(
            header_frame, 
            text="📊 Graphiques Personnalisés", 
            fg_color="#8e44ad", 
            hover_color="#6c3483",
            font=("Arial", 12, "bold"),
            height=35,
            width=220,
            command=self.open_custom_graph_window
        ).pack(side="right", padx=10)
        
        axes_frame = ctk.CTkFrame(control_frame)
        axes_frame.pack(fill="x", padx=10, pady=5)
        
        x_frame = ctk.CTkFrame(axes_frame, fg_color="transparent")
        x_frame.pack(side="left", expand=True, fill="x", padx=5)
        ctk.CTkLabel(x_frame, text="Axe X:").pack()
        self.x_axis_var = ctk.StringVar(value="A")
        self.x_axis_menu = ctk.CTkOptionMenu(x_frame, variable=self.x_axis_var, values=["A"])
        self.x_axis_menu.pack(fill="x")
        
        y_frame = ctk.CTkFrame(axes_frame, fg_color="transparent")
        y_frame.pack(side="left", expand=True, fill="x", padx=5)
        ctk.CTkLabel(y_frame, text="Axe Y:").pack()
        self.y_axis_var = ctk.StringVar(value="B")
        self.y_axis_menu = ctk.CTkOptionMenu(y_frame, variable=self.y_axis_var, values=["B"])
        self.y_axis_menu.pack(fill="x")
        
        z_frame = ctk.CTkFrame(axes_frame, fg_color="transparent")
        z_frame.pack(side="left", expand=True, fill="x", padx=5)
        ctk.CTkLabel(z_frame, text="Axe Z:").pack()
        self.z_axis_var = ctk.StringVar(value="C")
        self.z_axis_menu = ctk.CTkOptionMenu(z_frame, variable=self.z_axis_var, values=["C"])
        self.z_axis_menu.pack(fill="x")
        
        ctk.CTkButton(control_frame, text="🔄 Actualiser Colonnes", 
                      command=self.update_column_selectors, fg_color="#3498DB").pack(pady=5)
        
        analysis_frame = ctk.CTkFrame(control_frame)
        analysis_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(analysis_frame, text="📊 Afficher Graphique", 
                      command=self.generate_3d_plot, fg_color="#9B59B6").pack(side="left", expand=True, padx=2)
        ctk.CTkButton(analysis_frame, text="📈 Analyser RSM", 
                      command=self.analyze_rsm, fg_color="#E67E22").pack(side="left", expand=True, padx=2)
        ctk.CTkButton(analysis_frame, text="💾 Exporter Graphe", 
                      command=self.export_graph, fg_color="#2E86C1").pack(side="left", expand=True, padx=2)
        ctk.CTkButton(analysis_frame, text="🗺️ Vue 2D RSM", 
                      command=self.show_2d_rsm, fg_color="#16A085").pack(side="left", expand=True, padx=2)
        
        style_frame = ctk.CTkFrame(control_frame)
        style_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(style_frame, text="Palette:").pack(side="left", padx=5)
        self.colormap_var = ctk.StringVar(value="viridis")
        ctk.CTkOptionMenu(style_frame, values=["viridis", "plasma", "magma", "coolwarm"], 
                          variable=self.colormap_var).pack(side="left", padx=5)
        
        ctk.CTkLabel(style_frame, text="Rotation:").pack(side="left", padx=5)
        self.rotation_var = ctk.IntVar(value=45)
        ctk.CTkSlider(style_frame, from_=0, to=360, variable=self.rotation_var, 
                      command=self.update_graph_rotation).pack(side="left", expand=True, fill="x", padx=5)
        
        ctk.CTkButton(style_frame, text="📄 Exporter Équation", fg_color="#8e44ad", 
                      command=self.export_equation).pack(side="left", padx=5)

    def setup_graph_and_stats(self):
        graph_frame = ctk.CTkFrame(self.right_frame)
        graph_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        self.fig = Figure(figsize=(6, 6), dpi=100)
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.canvas = FigureCanvasTkAgg(self.fig, graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        self.stats_frame = ctk.CTkFrame(self.right_frame)
        self.stats_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        
        metrics_frame = ctk.CTkFrame(self.stats_frame)
        metrics_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(metrics_frame, text="Métrique:").pack(side="left", padx=5)
        self.metric_var = ctk.StringVar(value="R²")
        self.metric_menu = ctk.CTkOptionMenu(
            metrics_frame, 
            variable=self.metric_var,
            values=["R²", "MAE", "MSE", "RMSE", "Équation complète"],
            command=self.update_metric_display
        )
        self.metric_menu.pack(side="left", padx=5, expand=True, fill="x")
        
        self.stats_label = ctk.CTkLabel(
            self.stats_frame,
            text="--",
            justify="left",
            font=("Arial", 11)
        )
        self.stats_label.pack(pady=10, padx=10)

    def update_metric_display(self, *args):
        if not hasattr(self, 'current_model'):
            self.stats_label.configure(text="Aucun modèle calculé")
            return
        
        metric = self.metric_var.get()
        df = self.spreadsheet.get_dataframe()
        x_col = self.x_axis_var.get()
        y_col = self.y_axis_var.get()
        z_col = self.z_axis_var.get()
        
        df_clean = df[[x_col, y_col, z_col]].dropna()
        if df_clean.empty:
            self.stats_label.configure(text="Aucune donnée valide")
            return
        
        X = df_clean[[x_col, y_col]].values
        y_true = df_clean[z_col].values
        
        try:
            y_pred = self.current_model.predict(X)
        except Exception as e:
            self.stats_label.configure(text=f"Erreur de prédiction: {str(e)}")
            return
        
        if metric == "R²":
            value = f"R² = {self.current_model.score(X, y_true):.4f}"
        elif metric == "MAE":
            mae = np.mean(np.abs(y_true - y_pred))
            value = f"MAE = {mae:.4f}"
        elif metric == "MSE":
            mse = np.mean((y_true - y_pred)**2)
            value = f"MSE = {mse:.4f}"
        elif metric == "RMSE":
            rmse = np.sqrt(np.mean((y_true - y_pred)**2))
            value = f"RMSE = {rmse:.4f}"
        else:
            try:
                coeffs = self.current_model.named_steps['linearregression'].coef_
                intercept = self.current_model.named_steps['linearregression'].intercept_
                poly_features = self.current_model.named_steps['polynomialfeatures']
                feature_names = poly_features.get_feature_names_out([x_col, y_col])
                equation = f"{z_col} = {intercept:.2f}"
                for coef, name in zip(coeffs, feature_names):
                    equation += f" + ({coef:.2f})*{name}"
                value = f"Équation:\n{equation}"
            except Exception as e:
                value = f"Erreur équation: {str(e)}"
        
        self.stats_label.configure(text=value)

    def update_column_selectors(self):
        df = self.spreadsheet.get_dataframe()
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numeric_cols:
            messagebox.showwarning("Attention", "Aucune colonne numérique trouvée")
            return
        
        self.x_axis_menu.configure(values=numeric_cols)
        self.y_axis_menu.configure(values=numeric_cols)
        self.z_axis_menu.configure(values=numeric_cols)
        
        if len(numeric_cols) >= 3:
            self.x_axis_var.set(numeric_cols[0])
            self.y_axis_var.set(numeric_cols[1])
            self.z_axis_var.set(numeric_cols[2])
        elif len(numeric_cols) >= 1:
            self.x_axis_var.set(numeric_cols[0])
            self.y_axis_var.set(numeric_cols[0])
            self.z_axis_var.set(numeric_cols[0])
        
        messagebox.showinfo("Succès", f"{len(numeric_cols)} colonnes numériques détectées")

    def generate_3d_plot(self):
        try:
            self.fig.clear()
            if hasattr(self, '_colorbar') and self._colorbar:
                try:
                    self._colorbar.remove()
                except:
                    pass
                self._colorbar = None
            self.ax = self.fig.add_subplot(111, projection='3d')
            
            df = self.spreadsheet.get_dataframe()
            x_col = self.x_axis_var.get()
            y_col = self.y_axis_var.get()
            z_col = self.z_axis_var.get()
            
            if x_col not in df.columns or y_col not in df.columns or z_col not in df.columns:
                raise ValueError("Colonnes sélectionnées invalides")
            
            df_clean = df[[x_col, y_col, z_col]].dropna()
            if len(df_clean) == 0:
                raise ValueError("Aucune donnée valide trouvée")
            
            x_data = df_clean[x_col].values
            y_data = df_clean[y_col].values
            z_data = df_clean[z_col].values
            
            self.ax.clear()
            scatter = self.ax.scatter(x_data, y_data, z_data, c=z_data, 
                                     cmap=self.colormap_var.get(), marker='o', s=100)
            
            if hasattr(self, '_colorbar') and self._colorbar:
                try:
                    self._colorbar.remove()
                except:
                    pass
                self._colorbar = None
            
            self._colorbar = self.fig.colorbar(scatter, ax=self.ax, label=z_col)
            
            self.ax.set_xlabel(x_col)
            self.ax.set_ylabel(y_col)
            self.ax.set_zlabel(z_col)
            self.ax.set_title('Graphique 3D')
            self.ax.view_init(elev=30, azim=self.rotation_var.get())
            
            self.canvas.draw()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la génération du graphique:\n{str(e)}")

    def analyze_rsm(self):
        try:
            # Nettoyer complètement la figure
            self.fig.clear()
            if hasattr(self, '_colorbar') and self._colorbar:
                try:
                    self._colorbar.remove()
                except:
                    pass
                self._colorbar = None
            
            # Créer un nouvel axe 3D
            self.ax = self.fig.add_subplot(111, projection='3d')
            
            df = self.spreadsheet.get_dataframe()
            x_col = self.x_axis_var.get()
            y_col = self.y_axis_var.get()
            z_col = self.z_axis_var.get()
            
            df_clean = df[[x_col, y_col, z_col]].dropna()
            if len(df_clean) < 6:
                messagebox.showinfo("Données Insuffisantes", 
                                  "Il faut au moins 6 points pour l'analyse RSM")
                return
            
            X = df_clean[[x_col, y_col]].values
            y = df_clean[z_col].values
            
            poly_features = PolynomialFeatures(degree=2, include_bias=False)
            model = make_pipeline(poly_features, LinearRegression())
            model.fit(X, y)
            
            self.current_model = model
            self.update_metric_display()
            
            r2_score = model.score(X, y)
            coeffs = model.named_steps['linearregression'].coef_
            intercept = model.named_steps['linearregression'].intercept_
            feature_names = poly_features.get_feature_names_out([x_col, y_col])
            
            equation = f"{z_col} = {intercept:.2f}"
            for coef, name in zip(coeffs, feature_names):
                equation += f" + ({coef:.2f})*{name}"
            
            stats_text = f"R² = {r2_score:.4f}\n{equation}"
            self.stats_label.configure(text=stats_text)
            
            x_min, x_max = X[:, 0].min(), X[:, 0].max()
            y_min, y_max = X[:, 1].min(), X[:, 1].max()
            xx, yy = np.meshgrid(np.linspace(x_min, x_max, 50), np.linspace(y_min, y_max, 50))
            zz = model.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
            
            surface = self.ax.plot_surface(xx, yy, zz, cmap=self.colormap_var.get(), alpha=0.7)
            scatter = self.ax.scatter(X[:, 0], X[:, 1], y, c='red', s=50, marker='o', 
                                     label='Points expérimentaux')
            
            if hasattr(self, '_colorbar') and self._colorbar:
                try:
                    self._colorbar.remove()
                except:
                    pass
                self._colorbar = None
            
            self._colorbar = self.fig.colorbar(surface, ax=self.ax, label=z_col)
            
            self.ax.set_xlabel(x_col)
            self.ax.set_ylabel(y_col)
            self.ax.set_zlabel(f'{z_col} Prédite')
            self.ax.set_title('Surface de Réponse (RSM)')
            
            legend_elements = [
                Line2D([0], [0], marker='o', color='w', markerfacecolor='red', 
                      markersize=10, label='Points expérimentaux'),
                Line2D([0], [0], linestyle='-', 
                      color=plt.cm.get_cmap(self.colormap_var.get())(0.5), 
                      label='Surface de réponse')
            ]
            self.ax.legend(handles=legend_elements, loc='upper right')
            self.ax.view_init(elev=30, azim=self.rotation_var.get())
            
            self.canvas.draw()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'analyse RSM:\n{str(e)}")

    def export_equation(self):
        if not hasattr(self, 'current_model'):
            messagebox.showinfo("Info", "Aucun modèle à exporter")
            return
        
        x_col = self.x_axis_var.get()
        y_col = self.y_axis_var.get()
        z_col = self.z_axis_var.get()
        
        try:
            coeffs = self.current_model.named_steps['linearregression'].coef_
            intercept = self.current_model.named_steps['linearregression'].intercept_
            poly_features = self.current_model.named_steps['polynomialfeatures']
            feature_names = poly_features.get_feature_names_out([x_col, y_col])
            
            equation = f"{z_col} = {intercept:.6f}"
            for coef, name in zip(coeffs, feature_names):
                equation += f" + ({coef:.6f})*{name}"
            
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", 
                                                    filetypes=[("Texte", "*.txt")])
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(equation)
                messagebox.showinfo("Succès", "Équation exportée avec succès")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export:\n{str(e)}")

    def update_graph_rotation(self, *args):
        if hasattr(self, 'ax') and self.ax.name == '3d':
            self.ax.view_init(elev=30, azim=self.rotation_var.get())
            self.canvas.draw()

    def export_graph(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("PDF", "*.pdf"), ("SVG", "*.svg")]
        )
        if file_path:
            try:
                self.fig.savefig(file_path, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Succès", f"Graphique exporté vers:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'export:\n{str(e)}")

    def show_2d_rsm(self):
        try:
            # Nettoyer la figure et recréer l'axe 2D
            self.fig.clear()
            if hasattr(self, '_colorbar') and self._colorbar:
                try:
                    self._colorbar.remove()
                except:
                    pass
                self._colorbar = None
            
            self.ax = self.fig.add_subplot(111)
            
            df = self.spreadsheet.get_dataframe()
            x_col = self.x_axis_var.get()
            y_col = self.y_axis_var.get()
            z_col = self.z_axis_var.get()
            
            df_clean = df[[x_col, y_col, z_col]].dropna()
            if len(df_clean) < 6:
                messagebox.showinfo("Données Insuffisantes", 
                                  "Il faut au moins 6 points pour l'analyse RSM")
                return
            
            X = df_clean[[x_col, y_col]].values
            y = df_clean[z_col].values
            
            poly_features = PolynomialFeatures(degree=2, include_bias=False)
            model = make_pipeline(poly_features, LinearRegression())
            model.fit(X, y)
            
            x_min, x_max = X[:, 0].min(), X[:, 0].max()
            y_min, y_max = X[:, 1].min(), X[:, 1].max()
            xx, yy = np.meshgrid(np.linspace(x_min, x_max, 100), np.linspace(y_min, y_max, 100))
            zz = model.predict(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)
            
            contour = self.ax.contourf(xx, yy, zz, levels=50, cmap=self.colormap_var.get())
            self._colorbar = self.fig.colorbar(contour, ax=self.ax, label=z_col)
            scatter = self.ax.scatter(X[:, 0], X[:, 1], c='red', s=100, marker='o', 
                                     label='Points expérimentaux')
            
            self.ax.set_xlabel(x_col)
            self.ax.set_ylabel(y_col)
            self.ax.set_title(f'Vue 2D RSM - {z_col}')
            self.ax.legend()
            self.fig.tight_layout()
            
            self.canvas.draw()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'affichage 2D RSM:\n{str(e)}")

    def open_custom_graph_window(self):
        def get_current_df():
            return self.spreadsheet.get_dataframe()
        win = CustomGraphsWindow(self, get_current_df)
        win.grab_set()

if __name__ == "__main__":
    app = ProjectApp()
    app.mainloop()