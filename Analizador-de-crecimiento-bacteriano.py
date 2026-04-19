import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import csv
from collections import defaultdict

# Intentar importar scipy para ajuste y suavizado
try:
    from scipy.optimize import curve_fit
    from scipy.signal import savgol_filter
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

# Intentar importar chardet para detección de codificación
CHARDET_AVAILABLE = False
try:
    import chardet
    CHARDET_AVAILABLE = True
except ImportError:
    pass

# Configuración de estilo matplotlib minimalista y elegante
plt.style.use('seaborn-v0_8-white')
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'axes.labelweight': 'normal',
    'lines.linewidth': 1.8,
    'lines.markersize': 6,
    'figure.dpi': 120,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'axes.edgecolor': '#333333',
    'axes.linewidth': 0.8,
    'grid.color': '#cccccc',
    'grid.linestyle': '--',
    'grid.linewidth': 0.5,
    'grid.alpha': 0.7,
    'legend.frameon': True,
    'legend.fancybox': True,
    'legend.framealpha': 0.9,
    'legend.edgecolor': '#dddddd'
})

# Paleta de colores sofisticada para múltiples datasets
COLORS = ['#2E86AB', '#D64933', '#F18F01', '#6A994E', '#BC4B51', '#5E4B56', '#3D5A80', '#EE6C4D']


# ============================================================================
# Funciones de utilidad para carga de CSV
# ============================================================================

def detect_encoding(filepath, num_lines=10000):
    """
    Detecta la codificación del archivo.
    Primero intenta con chardet si está disponible, luego prueba codificaciones comunes.
    """
    if CHARDET_AVAILABLE:
        try:
            with open(filepath, 'rb') as f:
                raw_data = f.read(num_lines)
                result = chardet.detect(raw_data)
                if result and result.get('encoding'):
                    return result['encoding']
        except Exception as e:
            pass
    
    # Fallback: probar codificaciones comunes
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-16', 'ascii']
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                f.read(num_lines)
            return encoding
        except (UnicodeDecodeError, LookupError):
            continue
    
    return 'utf-8'  # Por defecto


def detect_separator(filepath, encoding='utf-8', num_lines=5):
    """
    Detecta el separador del CSV usando csv.Sniffer.
    Prueba con un número limitado de líneas para velocidad.
    """
    try:
        with open(filepath, 'r', encoding=encoding, errors='replace') as f:
            # Leer primeras líneas
            sample = ''
            for _ in range(num_lines):
                line = f.readline()
                if not line:
                    break
                sample += line
        
        if sample:
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample, delimiters=',;\t|')
            return dialect.delimiter
    except Exception:
        pass
    
    # Fallback: retornar separador por defecto
    return ','


def load_csv_with_preview(root, filepath):
    """
    Abre un diálogo de previsualización interactivo donde el usuario puede:
    - Ajustar la codificación y el separador
    - Confirmar manualmente el mapeo de columnas
    - Opcionalmente agrupar por archivo/ID
    Retorna (df, encoding, separator, col_map, group_by) o (None, None, None, None, None) si cancela.
    """
    encoding = detect_encoding(filepath)
    separator = detect_separator(filepath, encoding)
    
    # Carga inicial para detectar columnas
    df_temp = pd.read_csv(filepath, sep=separator, encoding=encoding, nrows=20, on_bad_lines='skip')
    available_columns = list(df_temp.columns)
    
    preview_window = tk.Toplevel(root)
    preview_window.title("Previsualización de CSV")
    preview_window.geometry("950x700")
    preview_window.configure(bg='#f5f5f5')
    
    # Variables de configuración
    encoding_var = tk.StringVar(value=encoding)
    separator_var = tk.StringVar(value=separator)
    
    # Variables para mapeo de columnas
    tiempo_col_var = tk.StringVar(value="")
    altura_col_var = tk.StringVar(value="")
    temp_col_var = tk.StringVar(value="")
    notas_col_var = tk.StringVar(value="")
    group_by_var = tk.StringVar(value="Ninguno")
    
    result = {'df': None, 'encoding': encoding, 'separator': separator, 
              'col_map': {}, 'group_by': None, 'cancelled': True}
    
    # Frame superior: Configuración básica
    config_frame = ttk.LabelFrame(preview_window, text="Configuración del CSV", padding=10)
    config_frame.pack(fill="x", padx=10, pady=10)
    
    ttk.Label(config_frame, text="Codificación:").pack(side="left", padx=5)
    encoding_combo = ttk.Combobox(config_frame, textvariable=encoding_var, 
                                   values=['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'ascii'],
                                   state='readonly', width=15)
    encoding_combo.pack(side="left", padx=5)
    
    ttk.Label(config_frame, text="Separador:").pack(side="left", padx=20)
    separator_combo = ttk.Combobox(config_frame, textvariable=separator_var,
                                    values=[',', ';', '\t', '|', ' '],
                                    state='readonly', width=10)
    separator_combo.pack(side="left", padx=5)
    separator_combo.set(separator)
    
    # Frame de mapeo de columnas
    mapping_frame = ttk.LabelFrame(preview_window, text="Mapeo de Columnas", padding=10)
    mapping_frame.pack(fill="x", padx=10, pady=5)
    
    ttk.Label(mapping_frame, text="Tiempo:").grid(row=0, column=0, sticky="e", padx=5)
    tiempo_combo = ttk.Combobox(mapping_frame, textvariable=tiempo_col_var, 
                                 values=available_columns, state='readonly', width=20)
    tiempo_combo.grid(row=0, column=1, padx=5, sticky="ew")
    
    ttk.Label(mapping_frame, text="Altura:").grid(row=0, column=2, sticky="e", padx=5)
    altura_combo = ttk.Combobox(mapping_frame, textvariable=altura_col_var, 
                                 values=available_columns, state='readonly', width=20)
    altura_combo.grid(row=0, column=3, padx=5, sticky="ew")
    
    ttk.Label(mapping_frame, text="Temperatura (opt):").grid(row=1, column=0, sticky="e", padx=5)
    temp_combo = ttk.Combobox(mapping_frame, textvariable=temp_col_var, 
                               values=[''] + available_columns, state='readonly', width=20)
    temp_combo.grid(row=1, column=1, padx=5, sticky="ew")
    
    ttk.Label(mapping_frame, text="Notas (opt):").grid(row=1, column=2, sticky="e", padx=5)
    notas_combo = ttk.Combobox(mapping_frame, textvariable=notas_col_var, 
                                values=[''] + available_columns, state='readonly', width=20)
    notas_combo.grid(row=1, column=3, padx=5, sticky="ew")
    
    ttk.Label(mapping_frame, text="Agrupar por (opt):").grid(row=2, column=0, sticky="e", padx=5)
    group_combo = ttk.Combobox(mapping_frame, textvariable=group_by_var,
                                values=['Ninguno'] + available_columns, state='readonly', width=20)
    group_combo.grid(row=2, column=1, padx=5, sticky="ew")
    
    mapping_frame.grid_columnconfigure(1, weight=1)
    mapping_frame.grid_columnconfigure(3, weight=1)
    
    # Frame de tabla de previsualización
    table_frame = ttk.LabelFrame(preview_window, text="Previsualización (primeras 20 filas)", padding=5)
    table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    columns_tree = ttk.Treeview(table_frame, show="headings", height=15)
    columns_tree.pack(side="left", fill="both", expand=True)
    
    scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=columns_tree.yview)
    scrollbar_y.pack(side="right", fill="y")
    columns_tree.configure(yscrollcommand=scrollbar_y.set)
    
    scrollbar_x = ttk.Scrollbar(preview_window, orient="horizontal", command=columns_tree.xview)
    scrollbar_x.pack(fill="x", padx=10)
    columns_tree.configure(xscrollcommand=scrollbar_x.set)
    
    # Frame inferior: Mensajes
    info_frame = ttk.Frame(preview_window)
    info_frame.pack(fill="x", padx=10, pady=5)
    info_var = tk.StringVar(value="Cargando previsualización...")
    ttk.Label(info_frame, textvariable=info_var, foreground='#2E86AB').pack(anchor="w")
    
    def update_preview():
        """Actualiza la previsualización con la configuración actual."""
        try:
            encoding_val = encoding_var.get()
            separator_val = separator_var.get()
            
            df_preview = pd.read_csv(filepath, sep=separator_val, encoding=encoding_val, 
                                     nrows=20, on_bad_lines='skip')
            
            for item in columns_tree.get_children():
                columns_tree.delete(item)
            
            columns = list(df_preview.columns)
            columns_tree['columns'] = columns
            
            for col in columns:
                columns_tree.heading(col, text=col)
                columns_tree.column(col, width=100, anchor="center")
            
            for idx, row in df_preview.iterrows():
                values = [str(row[col])[:50] for col in columns]
                columns_tree.insert("", "end", values=values)
            
            # Actualizar combos de columnas
            for combo in [tiempo_combo, altura_combo, temp_combo, notas_combo, group_combo]:
                combo['values'] = [''] + columns if combo != tiempo_combo and combo != altura_combo else columns
            
            num_rows = len(df_preview)
            num_cols = len(columns)
            info_var.set(f"✓ Cargado: {num_rows} filas, {num_cols} columnas | "
                        f"Codificación: {encoding_val} | Separador: '{separator_val}'")
            result['df'] = df_preview
            result['encoding'] = encoding_val
            result['separator'] = separator_val
            
        except Exception as e:
            info_var.set(f"✗ Error: {str(e)[:100]}")
    
    encoding_combo.bind("<<ComboboxSelected>>", lambda e: update_preview())
    separator_combo.bind("<<ComboboxSelected>>", lambda e: update_preview())
    
    preview_window.after(100, update_preview)
    
    # Frame de botones
    btn_frame = ttk.Frame(preview_window)
    btn_frame.pack(fill="x", padx=10, pady=10)
    
    def on_accept():
        t_col = tiempo_col_var.get()
        h_col = altura_col_var.get()
        
        if not t_col or not h_col:
            messagebox.showwarning("Columnas faltantes", "Debe seleccionar Tiempo y Altura")
            return
        
        result['col_map'] = {
            'Tiempo': t_col,
            'Altura': h_col,
            'Temperatura': temp_col_var.get() or None,
            'Notas': notas_col_var.get() or None
        }
        result['group_by'] = None if group_by_var.get() == "Ninguno" else group_by_var.get()
        result['cancelled'] = False
        preview_window.destroy()
    
    def on_cancel():
        result['cancelled'] = True
        preview_window.destroy()
    
    ttk.Button(btn_frame, text="Cargar este CSV", command=on_accept).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Cancelar", command=on_cancel).pack(side="left", padx=5)
    
    preview_window.transient(root)
    preview_window.grab_set()
    root.wait_window(preview_window)
    
    if result['cancelled']:
        return None, None, None, None, None
    
    return result['df'], result['encoding'], result['separator'], result['col_map'], result['group_by']


class Dataset:
    """Representa un conjunto de datos con su nombre, color y datos crudos."""
    def __init__(self, name, color, df, group_by=None):
        self.name = name
        self.color = color
        self.group_by = group_by  # 'archivo' o 'id' para evitar promediar grupos diferentes
        self.df = df.copy()  # Debe tener columnas: Tiempo, Altura, Temperatura, Notas
        # Convertir a numérico
        self.df['Tiempo'] = pd.to_numeric(self.df['Tiempo'], errors='coerce')
        self.df['Altura'] = pd.to_numeric(self.df['Altura'], errors='coerce')
        self.df.dropna(subset=['Tiempo', 'Altura'], inplace=True)
        self.df.sort_values('Tiempo', inplace=True)

    def get_aggregated_data(self):
        """Agrupa por tiempo (y opcionalmente por archivo/ID) y calcula estadísticas."""
        if self.group_by and self.group_by in self.df.columns:
            # Agrupar por grupo y tiempo
            grouped = self.df.groupby([self.group_by, 'Tiempo'])['Altura'].agg(['mean', 'std', 'count']).reset_index()
            # Reagrupar por tiempo solamente (promediando entre grupos)
            grouped = grouped.groupby('Tiempo').agg({'mean': 'mean', 'std': 'mean', 'count': 'sum'}).reset_index()
            grouped.columns = ['Tiempo', 'mean', 'std', 'count']
        else:
            # Agrupación simple por tiempo
            grouped = self.df.groupby('Tiempo')['Altura'].agg(['mean', 'std', 'count'])
            grouped.reset_index(inplace=True)
        return grouped


class GrowthCurveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador de crecimiento de microorganismos")
        self.root.geometry("1200x850")
        self.root.configure(bg='#f5f5f5')
        
        # Datasets cargados
        self.datasets = []          # Lista de objetos Dataset
        self.current_color_idx = 0
        self.project_name = tk.StringVar(value="Experimento")
        
        self.create_widgets()
        self.update_dataset_listbox()
        
    def create_widgets(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background='#f5f5f5')
        style.configure('TFrame', background='#f5f5f5')
        style.configure('TLabelframe', background='#f5f5f5', borderwidth=1, relief='solid')
        style.configure('TButton', font=('Helvetica', 9))
        style.configure('TPanedwindow', background='#f5f5f5')
        
        # Frame superior: Proyecto
        top_frame = ttk.LabelFrame(self.root, text="Proyecto", padding=10)
        top_frame.pack(fill="x", padx=15, pady=(15,5))
        
        ttk.Label(top_frame, text="Nombre del proyecto:").grid(row=0, column=0, sticky="w")
        ttk.Entry(top_frame, textvariable=self.project_name, width=35, font=('Helvetica', 10)).grid(row=0, column=1, padx=10, sticky="w")
        ttk.Button(top_frame, text="Nuevo proyecto", command=self.new_project).grid(row=0, column=2, padx=5)
        ttk.Button(top_frame, text="Cargar CSV (añadir dataset)", command=self.load_csv).grid(row=0, column=3, padx=5)
        
        # PanedWindow horizontal para izquierda y centro
        main_paned = ttk.PanedWindow(self.root, orient="horizontal")
        main_paned.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Frame izquierdo: Gestión de datasets
        left_frame = ttk.LabelFrame(main_paned, text="Datasets cargados", padding=10)
        main_paned.add(left_frame, weight=0)
        
        self.dataset_listbox = tk.Listbox(left_frame, width=25, height=12, 
                                          font=('Helvetica', 10), bg='white', relief='flat',
                                          selectbackground='#d0d0d0')
        self.dataset_listbox.pack(pady=5)
        self.dataset_listbox.bind('<<ListboxSelect>>', self.on_dataset_select)
        
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill="x", pady=5)
        ttk.Button(btn_frame, text="Eliminar dataset", command=self.remove_dataset).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Limpiar todo", command=self.clear_all_datasets).pack(side="left", padx=2)
        
        # Frame central: Entrada manual + tabla
        center_frame = ttk.Frame(main_paned)
        main_paned.add(center_frame, weight=1)
        
        # PanedWindow vertical en el centro
        center_paned = ttk.PanedWindow(center_frame, orient="vertical")
        center_paned.pack(fill="both", expand=True)
        
        # Frame de entrada manual
        self.manual_frame = ttk.LabelFrame(center_paned, text="Agregar datos manualmente", padding=10)
        center_paned.add(self.manual_frame, weight=0)
        
        ttk.Label(self.manual_frame, text="Dataset:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.selected_dataset_var = tk.StringVar(value="Ninguno")
        ttk.Label(self.manual_frame, textvariable=self.selected_dataset_var, font=('Helvetica', 10, 'bold')).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(self.manual_frame, text="Tiempo:").grid(row=1, column=0, sticky="e", padx=5, pady=3)
        self.time_entry = ttk.Entry(self.manual_frame, width=12, font=('Helvetica', 10))
        self.time_entry.grid(row=1, column=1, sticky="w", padx=5, pady=3)
        
        ttk.Label(self.manual_frame, text="Altura:").grid(row=2, column=0, sticky="e", padx=5, pady=3)
        self.height_entry = ttk.Entry(self.manual_frame, width=12, font=('Helvetica', 10))
        self.height_entry.grid(row=2, column=1, sticky="w", padx=5, pady=3)
        
        ttk.Label(self.manual_frame, text="Temperatura:").grid(row=3, column=0, sticky="e", padx=5, pady=3)
        self.temp_entry = ttk.Entry(self.manual_frame, width=12, font=('Helvetica', 10))
        self.temp_entry.grid(row=3, column=1, sticky="w", padx=5, pady=3)
        
        ttk.Label(self.manual_frame, text="Notas:").grid(row=4, column=0, sticky="e", padx=5, pady=3)
        self.notes_entry = ttk.Entry(self.manual_frame, width=25, font=('Helvetica', 10))
        self.notes_entry.grid(row=4, column=1, sticky="w", padx=5, pady=3)
        
        btn_manual = ttk.Frame(self.manual_frame)
        btn_manual.grid(row=5, column=0, columnspan=2, pady=15)
        ttk.Button(btn_manual, text="Agregar punto", command=self.add_data_point).pack(side="left", padx=5)
        ttk.Button(btn_manual, text="Eliminar dataset", command=self.remove_dataset).pack(side="left", padx=5)
        
        # Tabla de datos
        table_frame = ttk.LabelFrame(center_paned, text="Datos del dataset seleccionado", padding=5)
        center_paned.add(table_frame, weight=1)
        
        columns = ("Tiempo", "Altura", "Temperatura", "Notas")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        self.tree.heading("Tiempo", text="Tiempo")
        self.tree.heading("Altura", text="Altura")
        self.tree.heading("Temperatura", text="Temp")
        self.tree.heading("Notas", text="Notas")
        self.tree.column("Tiempo", width=70, anchor="center")
        self.tree.column("Altura", width=70, anchor="center")
        self.tree.column("Temperatura", width=70, anchor="center")
        self.tree.column("Notas", width=150, anchor="w")
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # Frame derecho: Gráfica
        right_frame = ttk.LabelFrame(main_paned, text="Gráfica de crecimiento", padding=5)
        main_paned.add(right_frame, weight=1)
        
        self.plot_frame = right_frame
        self.canvas = None
        self.fig = None
        
        # Botones de análisis
        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill="x", padx=15, pady=10)
        ttk.Button(action_frame, text="Analizar y Graficar", command=self.analyze_and_plot).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Guardar gráfica como PNG", command=self.save_plot).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Exportar informe", command=self.export_report).pack(side="left", padx=5)
        
        # Barra de estado
        self.status_var = tk.StringVar(value="Listo")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w", padding=(5,2))
        status_bar.pack(fill="x", padx=15, pady=(0,10))
        
    def new_project(self):
        name = simpledialog.askstring(
            "Nuevo proyecto",
            "Ingrese el nombre del nuevo proyecto:"
        )
        if name:
            self.project_name.set(name)
            self.clear_all_datasets()
            self.status_var.set(f"Nuevo proyecto: {self.project_name.get()}")
        else:
            self.status_var.set("Creación de proyecto cancelada")
        
    def clear_all_datasets(self):
        if not self.datasets:
            return
        
        num_datasets = len(self.datasets)
        if messagebox.askyesno(
            "Limpiar todos los datasets",
            f"¿Desea eliminar todos los {num_datasets} dataset(s) cargados?\n\n"
            f"Esta acción no se puede deshacer."
        ):
            self.datasets = []
            self.current_color_idx = 0
            self.update_dataset_listbox()
            self.refresh_table()
            self.clear_plot()
            self.status_var.set(f"{num_datasets} dataset(s) eliminado(s)")
        
    def load_csv(self):
        filepath = filedialog.askopenfilename(
            title="Seleccionar archivo CSV",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")]
        )
        if not filepath:
            return
        
        if not os.path.isfile(filepath):
            messagebox.showerror(
                "Archivo no encontrado",
                f"El archivo no existe:\n{filepath}"
            )
            return
        
        try:
            # Mostrar diálogo de previsualización con mapeo manual
            df_preview, encoding_used, separator_used, col_map, group_by = load_csv_with_preview(self.root, filepath)
            
            if df_preview is None:
                self.status_var.set("Carga de CSV cancelada")
                return
            
            # Cargar CSV completo
            df_loaded = pd.read_csv(filepath, sep=separator_used, encoding=encoding_used,
                                   on_bad_lines='skip')
            
            if df_loaded.empty:
                messagebox.showerror(
                    "CSV vacío",
                    f"El archivo CSV está vacío o no contiene datos válidos.\n"
                    f"Verificar:\n"
                    f"  • Codificación: {encoding_used}\n"
                    f"  • Separador: '{separator_used}'"
                )
                return
            
            # Aplicar mapeo de columnas del usuario
            new_df = pd.DataFrame()
            for key, col in col_map.items():
                if col:
                    new_df[key] = df_loaded[col]
            
            # Validar columnas requeridas
            if 'Tiempo' not in new_df.columns or 'Altura' not in new_df.columns:
                raise ValueError("Debe seleccionar columnas válidas para Tiempo y Altura")
            
            if 'Temperatura' not in new_df.columns:
                new_df['Temperatura'] = np.nan
            if 'Notas' not in new_df.columns:
                new_df['Notas'] = ""
            
            # Si se seleccionó agrupar por, agregar esa columna
            if group_by and group_by in df_loaded.columns:
                new_df['__grupo__'] = df_loaded[group_by]
            
            # Convertir a numérico
            original_rows = len(new_df)
            try:
                new_df['Tiempo'] = pd.to_numeric(new_df['Tiempo'], errors='coerce')
                new_df['Altura'] = pd.to_numeric(new_df['Altura'], errors='coerce')
                new_df['Temperatura'] = pd.to_numeric(new_df['Temperatura'], errors='coerce')
            except Exception as e:
                raise ValueError(f"Error al convertir datos a números: {str(e)}")
            
            new_df.dropna(subset=['Tiempo', 'Altura'], inplace=True)
            
            if new_df.empty:
                raise ValueError(
                    f"Después de procesar los datos, no quedan filas válidas.\n"
                    f"Filas originales: {original_rows}"
                )
            
            removed_rows = original_rows - len(new_df)
            new_df.sort_values('Tiempo', inplace=True)
            
            # Solicitar nombre del dataset
            base = os.path.basename(filepath)
            name = simpledialog.askstring(
                "Nombre del dataset",
                "Nombre para este dataset:",
                initialvalue=os.path.splitext(base)[0]
            )
            if not name:
                name = os.path.splitext(base)[0]
            
            # Crear dataset
            color = COLORS[self.current_color_idx % len(COLORS)]
            self.current_color_idx += 1
            dataset = Dataset(name, color, new_df, group_by='__grupo__' if group_by else None)
            self.datasets.append(dataset)
            self.update_dataset_listbox()
            self.dataset_listbox.selection_clear(0, tk.END)
            self.dataset_listbox.selection_set(tk.END)
            self.on_dataset_select()
            
            status_msg = f"Dataset '{name}' cargado: {len(new_df)} filas válidas"
            if removed_rows > 0:
                status_msg += f" ({removed_rows} eliminadas)"
            if group_by:
                status_msg += f" [Agrupado por: {group_by}]"
            self.status_var.set(status_msg)
            
            messagebox.showinfo(
                "Carga exitosa",
                f"Dataset cargado correctamente:\n\n"
                f"Nombre: {name}\n"
                f"Filas válidas: {len(new_df)}\n"
                f"Filas descartadas: {removed_rows}\n"
                f"Codificación: {encoding_used}\n"
                f"Separador: '{separator_used}'"
                f"{f'Agrupado por: {group_by}' if group_by else ''}"
            )
            
        except FileNotFoundError:
            messagebox.showerror("Archivo no encontrado", f"No se pudo encontrar el archivo:\n{filepath}")
        except ValueError as e:
            messagebox.showerror("Error de validación de datos", f"Los datos no cumplen con los requisitos:\n\n{str(e)}")
        except Exception as e:
            messagebox.showerror(
                "Error inesperado al cargar CSV",
                f"Ocurrió un error inesperado:\n\n{type(e).__name__}: {str(e)}"
            )
            
    def update_dataset_listbox(self):
        # Guardar el índice actualmente seleccionado
        current_selection = self.dataset_listbox.curselection()
        selected_idx = current_selection[0] if current_selection else None
        
        self.dataset_listbox.delete(0, tk.END)
        for ds in self.datasets:
            self.dataset_listbox.insert(tk.END, f"{ds.name} ({len(ds.df)} pts)")
        
        # Restaurar la selección si aún existe
        if selected_idx is not None and selected_idx < len(self.datasets):
            self.dataset_listbox.selection_set(selected_idx)
            self.dataset_listbox.see(selected_idx)
        elif len(self.datasets) > 0:
            self.dataset_listbox.selection_set(0)
            self.dataset_listbox.see(0)
            
    def on_dataset_select(self, event=None):
        selection = self.dataset_listbox.curselection()
        if selection:
            idx = selection[0]
            ds = self.datasets[idx]
            self.selected_dataset_var.set(ds.name)
            self.refresh_table(ds)
        else:
            self.selected_dataset_var.set("Ninguno")
            self.refresh_table(None)
            
    def refresh_table(self, dataset=None):
        for row in self.tree.get_children():
            self.tree.delete(row)
        if dataset is None:
            return
        for _, row in dataset.df.iterrows():
            tiempo = row["Tiempo"]
            altura = row["Altura"]
            temp = f"{row['Temperatura']:.1f}" if not pd.isna(row["Temperatura"]) else ""
            notas = row["Notas"] if not pd.isna(row["Notas"]) else ""
            self.tree.insert("", "end", values=(tiempo, altura, temp, notas))
            
    def remove_dataset(self):
        selection = self.dataset_listbox.curselection()
        if selection:
            idx = selection[0]
            name = self.datasets[idx].name
            num_points = len(self.datasets[idx].df)
            if messagebox.askyesno(
                "Confirmar eliminación",
                f"¿Está seguro de que desea eliminar el dataset?\n\n"
                f"Nombre: {name}\n"
                f"Puntos de datos: {num_points}\n\n"
                f"Esta acción no se puede deshacer."
            ):
                del self.datasets[idx]
                self.update_dataset_listbox()
                self.refresh_table(None)
                self.status_var.set(f"Dataset '{name}' eliminado")
        else:
            messagebox.showinfo(
                "Seleccione un dataset",
                "Seleccione el dataset que desea eliminar de la lista."
            )
            
    def add_data_point(self):
        selection = self.dataset_listbox.curselection()
        if not selection:
            messagebox.showwarning(
                "Sin dataset seleccionado",
                "Seleccione un dataset de la lista en el que desea agregar el punto de datos."
            )
            return
        idx = selection[0]
        ds = self.datasets[idx]
        
        t_str = self.time_entry.get().strip()
        h_str = self.height_entry.get().strip()
        
        # Validación de campos obligatorios
        if not t_str:
            messagebox.showwarning(
                "Campo obligatorio",
                "El campo 'Tiempo' es obligatorio.\n\n"
                "Ingrese un valor numérico (ej: 0, 1.5, 24)."
            )
            return
        if not h_str:
            messagebox.showwarning(
                "Campo obligatorio",
                "El campo 'Altura' es obligatorio.\n\n"
                "Ingrese un valor numérico (ej: 0.5, 1.2, 10)."
            )
            return
        
        # Conversión a números
        try:
            t = float(t_str)
            if t < 0:
                raise ValueError("El tiempo no puede ser negativo")
        except ValueError as e:
            messagebox.showerror(
                "Valor inválido para Tiempo",
                f"'{t_str}' no es un valor numérico válido.\n\n"
                f"Error: {str(e)}\n\n"
                f"Ingrese un número (ej: 0, 1.5, 24)."
            )
            return
        
        try:
            h = float(h_str)
            if h < 0:
                raise ValueError("La altura no puede ser negativa")
        except ValueError as e:
            messagebox.showerror(
                "Valor inválido para Altura",
                f"'{h_str}' no es un valor numérico válido.\n\n"
                f"Error: {str(e)}\n\n"
                f"Ingrese un número (ej: 0.5, 1.2, 10)."
            )
            return
        
        # Temperatura (opcional)
        temp_str = self.temp_entry.get().strip()
        if temp_str:
            try:
                temp = float(temp_str)
            except ValueError:
                messagebox.showerror(
                    "Valor inválido para Temperatura",
                    f"'{temp_str}' no es un valor numérico válido.\n\n"
                    f"Deje en blanco si no desea especificar temperatura."
                )
                return
        else:
            temp = np.nan
        
        notes = self.notes_entry.get().strip()
        
        # Crear nueva fila y agregarla
        new_row = pd.DataFrame({
            "Tiempo": [t],
            "Altura": [h],
            "Temperatura": [temp],
            "Notas": [notes]
        })
        ds.df = pd.concat([ds.df, new_row], ignore_index=True)
        ds.df.sort_values("Tiempo", inplace=True)
        self.refresh_table(ds)
        self.update_dataset_listbox()
        
        # Limpiar campos
        self.time_entry.delete(0, tk.END)
        self.height_entry.delete(0, tk.END)
        self.temp_entry.delete(0, tk.END)
        self.notes_entry.delete(0, tk.END)
        self.status_var.set(f"Punto agregado a '{ds.name}' (Tiempo={t}, Altura={h})")
        
    def clear_plot(self):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
            self.fig = None
            
    def analyze_and_plot(self):
        if not self.datasets:
            messagebox.showwarning(
                "Sin datos",
                "No hay datasets cargados para analizar.\n\n"
                "Cargue al menos un archivo CSV o agregue puntos manualmente."
            )
            return
        
        try:
            self.clear_plot()
            self.fig, self.ax = plt.subplots(figsize=(9, 6))
            
            results_text = []
            
            for ds in self.datasets:
                aggregated = ds.get_aggregated_data()
                
                if aggregated.empty:
                    results_text.append(f"{ds.name}: SIN DATOS VÁLIDOS")
                    continue
                
                time = aggregated['Tiempo'].values
                mean = aggregated['mean'].values
                std = aggregated['std'].values
                n = aggregated['count'].values
                
                # Mostrar barras de error si hay múltiples mediciones por tiempo
                has_error = np.any(n > 1)
                if has_error:
                    self.ax.errorbar(time, mean, yerr=std, fmt='o-', color=ds.color, 
                                     capsize=4, capthick=1.5, elinewidth=1.2, 
                                     markersize=6, linewidth=2, label=ds.name)
                else:
                    self.ax.plot(time, mean, 'o-', color=ds.color, markersize=6, linewidth=2, label=ds.name)
                
                # Intentar ajuste logístico
                if SCIPY_AVAILABLE and len(time) >= 4:
                    try:
                        params, r2, td = self.fit_logistic(time, mean)
                        t_smooth = np.linspace(min(time), max(time), 200)
                        y_fit = self.logistic_model(t_smooth, *params)
                        self.ax.plot(t_smooth, y_fit, '--', color=ds.color, alpha=0.7, linewidth=1.5)
                        
                        results_text.append(f"{ds.name}:")
                        results_text.append(f"  A = {params[0]:.3f} | k = {params[1]:.3f} | t₀ = {params[2]:.2f}")
                        results_text.append(f"  R² = {r2:.4f} | Td = {td:.2f}")
                    except Exception:
                        # Fallback: usar Savitzky-Golay si ajuste logístico falla
                        if len(time) >= 5:
                            try:
                                window_length = min(5, len(time) if len(time) % 2 == 1 else len(time) - 1)
                                y_smooth = savgol_filter(mean, window_length=window_length, polyorder=3)
                                self.ax.plot(time, y_smooth, '--', color=ds.color, alpha=0.7, linewidth=1.5)
                                results_text.append(f"{ds.name}: (suavizado Savitzky-Golay)")
                            except Exception:
                                results_text.append(f"{ds.name}: (sin ajuste)")
                        else:
                            results_text.append(f"{ds.name}: (insuficientes puntos para ajuste)")
                else:
                    if len(time) < 4 and SCIPY_AVAILABLE:
                        results_text.append(f"{ds.name}: ({len(time)} puntos)")
            
            # Estilo minimalista
            self.ax.set_xlabel('Tiempo', fontsize=12, labelpad=10)
            self.ax.set_ylabel('Altura', fontsize=12, labelpad=10)
            self.ax.set_title(f"Crecimiento microbiano: {self.project_name.get()}", fontsize=14, pad=15)
            self.ax.grid(True, linestyle='--', alpha=0.4)
            self.ax.spines['top'].set_visible(False)
            self.ax.spines['right'].set_visible(False)
            
            # Leyenda
            if len(self.datasets) > 0:
                legend = self.ax.legend(loc='best', frameon=True, fancybox=True, framealpha=0.9, edgecolor='#cccccc')
                legend.get_frame().set_linewidth(0.5)
            
            self.fig.tight_layout()
            
            # Texto de resultados
            if results_text:
                textstr = '\n'.join(results_text)
                self.fig.text(0.02, 0.02, textstr, fontsize=9, family='monospace',
                              bbox=dict(boxstyle="round,pad=0.3", facecolor='white', edgecolor='#dddddd', alpha=0.9))
            
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill="both", expand=True)
            
            self.status_var.set("Análisis completado exitosamente.")
            
        except Exception as e:
            messagebox.showerror(
                "Error al generar gráfica",
                f"Ocurrió un error durante el análisis:\n\n{type(e).__name__}: {str(e)}"
            )
            self.status_var.set(f"Error: {str(e)[:50]}")
        
    @staticmethod
    def logistic_model(t, A, k, t0):
        """Modelo logístico: A = capacidad de carga, k = tasa máxima, t0 = punto de inflexión."""
        return A / (1 + np.exp(-k * (t - t0)))
    
    @staticmethod
    def fit_logistic(time, values):
        """Ajusta modelo logístico y devuelve (params, R², tiempo_duplicacion).
        Lanza excepción si el ajuste falla."""
        if len(time) < 4:
            raise ValueError(f"Se necesitan al menos 4 puntos, se tienen {len(time)}")
        
        if np.all(np.isnan(values)) or np.all(np.isnan(time)):
            raise ValueError("Los datos contienen todos NaN")
        
        # Estimaciones iniciales
        A0 = max(values)
        if A0 <= 0:
            raise ValueError(f"El valor máximo debe ser positivo (actual: {A0})")
        
        k0 = 0.5
        grad = np.gradient(values)
        max_grad_idx = np.argmax(grad)
        t0_0 = time[max_grad_idx] if 0 <= max_grad_idx < len(time) else np.mean(time)
        
        bounds = ([0, 0, min(time)], [A0*2, 5, max(time)])
        
        try:
            popt, _ = curve_fit(
                GrowthCurveApp.logistic_model, time, values, 
                p0=[A0, k0, t0_0], bounds=bounds, maxfev=5000
            )
        except RuntimeError as e:
            raise ValueError(f"Convergencia fallida en curve_fit: {str(e)}")
        
        # Calcular R²
        y_pred = GrowthCurveApp.logistic_model(time, *popt)
        residuals = values - y_pred
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((values - np.mean(values))**2)
        
        if ss_tot == 0:
            r2 = 0
        else:
            r2 = 1 - (ss_res / ss_tot)
        
        # Tiempo de duplicación (en fase exponencial, Td = ln2 / k)
        td = np.log(2) / popt[1] if popt[1] > 0 else np.inf
        
        return popt, r2, td
    
    def save_plot(self):
        if self.fig is None:
            messagebox.showinfo(
                "Sin gráfica",
                "No hay gráfica para guardar.\n\n"
                "Haga clic en 'Analizar y Graficar' primero."
            )
            return
        
        default_name = f"{self.project_name.get().replace(' ', '_')}_curva.png"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG imagen", "*.png"), ("PDF", "*.pdf"), ("SVG", "*.svg")],
            initialfile=default_name
        )
        if not filepath:
            return
        
        try:
            self.fig.savefig(filepath, dpi=200, bbox_inches='tight', facecolor='white')
            self.status_var.set(f"Gráfica guardada: {filepath}")
            messagebox.showinfo(
                "Guardado exitoso",
                f"Gráfica guardada correctamente:\n\n{filepath}\n\n"
                f"Formato: {filepath.split('.')[-1].upper()}"
            )
        except PermissionError:
            messagebox.showerror(
                "Permiso denegado",
                f"No tiene permisos para escribir en:\n{filepath}\n\n"
                f"Intente guardar en otra carpeta."
            )
        except IOError as e:
            messagebox.showerror(
                "Error de E/S",
                f"Error al escribir el archivo:\n\n{str(e)}\n\n"
                f"Verifique que tiene espacio disponible."
            )
        except Exception as e:
            messagebox.showerror(
                "Error inesperado",
                f"No se pudo guardar la gráfica:\n\n{type(e).__name__}: {str(e)}"
            )
            
    def export_report(self):
        """Exporta un informe con los datos agregados y parámetros de ajuste."""
        if not self.datasets:
            messagebox.showwarning(
                "Sin datos",
                "No hay datasets cargados para exportar.\n\n"
                "Cargue al menos un CSV antes de exportar."
            )
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx"), ("CSV", "*.csv")]
        )
        if not filepath:
            return
        
        try:
            if filepath.endswith('.xlsx'):
                # Verificar que openpyxl esté disponible
                try:
                    import openpyxl
                except ImportError:
                    messagebox.showerror(
                        "Dependencia faltante",
                        "openpyxl no está instalado para exportar a Excel.\n\n"
                        "Intente exportar a CSV en su lugar, o instale openpyxl:\n"
                        "pip install openpyxl"
                    )
                    return
                
                with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                    for ds in self.datasets:
                        agg = ds.get_aggregated_data()
                        sheet_name = ds.name[:31]  # Límite de Excel
                        agg.to_excel(writer, sheet_name=sheet_name, index=False)
                        
                        # Añadir parámetros de ajuste en otra hoja
                        if SCIPY_AVAILABLE and len(agg) >= 4:
                            try:
                                params, r2, td = self.fit_logistic(agg['Tiempo'].values, agg['mean'].values)
                                param_df = pd.DataFrame({
                                    'Parámetro': ['A (capacidad)', 'k (tasa)', 't0 (inflexión)', 'R² (ajuste)', 'Td (duplicación)'],
                                    'Valor': [params[0], params[1], params[2], r2, td]
                                })
                                fit_sheet_name = f"{ds.name[:27]}_fit"
                                param_df.to_excel(writer, sheet_name=fit_sheet_name, index=False)
                            except Exception as fit_err:
                                print(f"No se pudo calcular ajuste para {ds.name}: {fit_err}")
            else:
                # Exportar a CSV
                combined_df = pd.DataFrame()
                for ds in self.datasets:
                    agg = ds.get_aggregated_data()
                    agg['Dataset'] = ds.name
                    combined_df = pd.concat([combined_df, agg], ignore_index=True)
                
                combined_df.to_csv(filepath, index=False, encoding='utf-8')
            
            self.status_var.set(f"Informe exportado a: {filepath}")
            messagebox.showinfo(
                "Exportación exitosa",
                f"Informe guardado correctamente:\n\n{filepath}\n\n"
                f"Datasets incluidos: {len(self.datasets)}"
            )
            
        except PermissionError:
            messagebox.showerror(
                "Permiso denegado",
                f"No tiene permisos para escribir en la ubicación:\n{filepath}\n\n"
                f"Intente guardar en otra carpeta o verifique los permisos."
            )
        except IOError as e:
            messagebox.showerror(
                "Error de E/S",
                f"Error al escribir el archivo:\n\n{str(e)}\n\n"
                f"Verifique que la carpeta existe y que tiene espacio disponible."
            )
        except Exception as e:
            messagebox.showerror(
                "Error inesperado al exportar",
                f"Ocurrió un error inesperado:\n\n{type(e).__name__}: {str(e)}\n\n"
                f"Intente guardar en otra ubicación."
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = GrowthCurveApp(root)
    root.mainloop()