import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import sys
import re
import unicodedata

# Import các module tự tạo
from entropy_calculator import analyze_source, analyze_binary_data, compare_sources
from visualization import (plot_entropy_comparison, plot_efficiency_comparison, 
                           plot_probability_distribution, plot_all_comparisons)
import math

# Tiêu chuẩn Entropy cho một số nguồn tin (bit/ký tự)
STANDARD_ENTROPY = {
    "Tiếng Việt": 4.2,
    "Tiếng Anh": 4.0,
    "Nhị phân": 8.0
}


class EntropyCalculatorApp:
    """Ứng dụng Desktop tính toán Entropy"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🔢 Entropy Calculator - Phân tích Nguồn tin")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Danh sách các nguồn tin đã phân tích
        self.sources = []
        
        # Thiết lập style
        self.setup_styles()
        
        # Tạo giao diện
        self.create_widgets()
        
    def setup_styles(self):
        """Thiết lập style cho ứng dụng"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom styles
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'))
        style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'))
        style.configure('Info.TLabel', font=('Segoe UI', 10))
        style.configure('Action.TButton', font=('Segoe UI', 10, 'bold'), padding=10)
        
    def create_widgets(self):
        """Tạo các widget chính"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="📊 PHÂN TÍCH ENTROPY NGUỒN TIN", 
                                style='Title.TLabel')
        title_label.pack(pady=(0, 10))
        
        # Paned window để chia 2 phần
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Input
        left_frame = ttk.Frame(paned, padding="5")
        paned.add(left_frame, weight=1)
        
        # Right panel - Results
        right_frame = ttk.Frame(paned, padding="5")
        paned.add(right_frame, weight=2)
        
        # Tạo các phần
        self.create_input_section(left_frame)
        self.create_results_section(right_frame)
        
    def create_input_section(self, parent):
        """Tạo phần nhập liệu"""
        # Notebook để có tabs
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Nhập văn bản
        text_tab = ttk.Frame(notebook, padding="10")
        notebook.add(text_tab, text="📝 Nhập văn bản")
        
        # Tab 2: Đọc từ file
        file_tab = ttk.Frame(notebook, padding="10")
        notebook.add(file_tab, text="📁 Đọc từ file")
        
        # === Tab Nhập văn bản ===
        ttk.Label(text_tab, text="Tên nguồn tin:", style='Header.TLabel').pack(anchor=tk.W)
        self.source_name_var = tk.StringVar(value="Nguồn tin 1")
        name_entry = ttk.Entry(text_tab, textvariable=self.source_name_var, width=30)
        name_entry.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(text_tab, text="Loại nguồn tin:", style='Header.TLabel').pack(anchor=tk.W)
        self.source_type_var = tk.StringVar(value="Khác")
        type_combo = ttk.Combobox(text_tab, textvariable=self.source_type_var, 
                                   values=["Tiếng Việt", "Tiếng Anh", "Nhị phân", "Khác"])
        type_combo.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(text_tab, text="Nhập hoặc paste văn bản:", style='Header.TLabel').pack(anchor=tk.W)
        self.text_input = scrolledtext.ScrolledText(text_tab, height=15, wrap=tk.WORD,
                                                     font=('Consolas', 10))
        self.text_input.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Checkbox bỏ qua khoảng trắng
        self.ignore_spaces_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(text_tab, text="Bỏ qua khoảng trắng", 
                        variable=self.ignore_spaces_var).pack(anchor=tk.W)
        
        # Nút thêm nguồn tin
        btn_frame = ttk.Frame(text_tab)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="➕ Thêm nguồn tin", style='Action.TButton',
                   command=self.add_text_source).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Xóa văn bản", 
                   command=lambda: self.text_input.delete('1.0', tk.END)).pack(side=tk.LEFT)
        
        # === Tab Đọc từ file ===
        ttk.Label(file_tab, text="Tên nguồn tin:", style='Header.TLabel').pack(anchor=tk.W)
        self.file_source_name_var = tk.StringVar(value="File data")
        file_name_entry = ttk.Entry(file_tab, textvariable=self.file_source_name_var, width=30)
        file_name_entry.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(file_tab, text="Loại file:", style='Header.TLabel').pack(anchor=tk.W)
        self.file_type_var = tk.StringVar(value="Văn bản (.txt)")
        file_type_combo = ttk.Combobox(file_tab, textvariable=self.file_type_var,
                                        values=["Văn bản (.txt)", "File Word (.docx)", "Nhị phân (.bin)", "Tự động nhận diện"])
        file_type_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Frame cho file path
        file_path_frame = ttk.Frame(file_tab)
        file_path_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.file_path_var = tk.StringVar()
        ttk.Entry(file_path_frame, textvariable=self.file_path_var, 
                  state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(file_path_frame, text="📂 Chọn file", 
                   command=self.browse_file).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Label(file_tab, text="Xem trước nội dung:", style='Header.TLabel').pack(anchor=tk.W)
        self.file_preview = scrolledtext.ScrolledText(file_tab, height=12, wrap=tk.WORD,
                                                       font=('Consolas', 10), state='disabled')
        self.file_preview.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Nút thêm file
        ttk.Button(file_tab, text="➕ Thêm từ file", style='Action.TButton',
                   command=self.add_file_source).pack(pady=10)
        

        
    def create_results_section(self, parent):
        """Tạo phần hiển thị kết quả"""
        # Header với các nút điều khiển
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="📊 Kết quả phân tích", 
                  style='Title.TLabel').pack(side=tk.LEFT)
        
        btn_frame = ttk.Frame(header_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text="📈 Vẽ biểu đồ", 
                   command=self.show_charts).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 Làm mới", 
                   command=self.clear_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="💾 Xuất kết quả", 
                   command=self.export_results).pack(side=tk.LEFT, padx=5)
        
        # Notebook cho kết quả và biểu đồ
        self.result_notebook = ttk.Notebook(parent)
        self.result_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Bảng kết quả
        table_tab = ttk.Frame(self.result_notebook, padding="5")
        self.result_notebook.add(table_tab, text="📋 Bảng kết quả")
        
        # Tab 2: Biểu đồ
        chart_tab = ttk.Frame(self.result_notebook, padding="5")
        self.result_notebook.add(chart_tab, text="📊 Biểu đồ")
        
        # Tab 3: Chi tiết
        detail_tab = ttk.Frame(self.result_notebook, padding="5")
        self.result_notebook.add(detail_tab, text="🔍 Chi tiết")
        
        # === Bảng kết quả ===
        # Treeview
        columns = ("name", "total", "symbols", "entropy", "max_entropy", "efficiency", "redundancy")
        self.result_tree = ttk.Treeview(table_tab, columns=columns, show='headings', height=8)
        
        # Định nghĩa headers
        self.result_tree.heading("name", text="Nguồn tin")
        self.result_tree.heading("total", text="Tổng ký tự")
        self.result_tree.heading("symbols", text="Số ký hiệu")
        self.result_tree.heading("entropy", text="Entropy (bit)")
        self.result_tree.heading("max_entropy", text="H_max (bit)")
        self.result_tree.heading("efficiency", text="Hiệu suất (%)")
        self.result_tree.heading("redundancy", text="Độ dư tương đối (%)")
        
        # Định nghĩa độ rộng cột
        self.result_tree.column("name", width=120)
        self.result_tree.column("total", width=80, anchor=tk.CENTER)
        self.result_tree.column("symbols", width=80, anchor=tk.CENTER)
        self.result_tree.column("entropy", width=100, anchor=tk.CENTER)
        self.result_tree.column("max_entropy", width=100, anchor=tk.CENTER)
        self.result_tree.column("efficiency", width=100, anchor=tk.CENTER)
        self.result_tree.column("redundancy", width=100, anchor=tk.CENTER)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_tab, orient=tk.VERTICAL, command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=scrollbar.set)
        
        self.result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click để xem chi tiết
        self.result_tree.bind('<Double-1>', self.show_source_detail)
        
        # Nút xóa nguồn tin được chọn
        ttk.Button(table_tab, text="🗑️ Xóa nguồn tin đã chọn", 
                   command=self.delete_selected_source).pack(pady=10)
        
        # === Biểu đồ ===
        self.chart_frame = ttk.Frame(chart_tab)
        self.chart_frame.pack(fill=tk.BOTH, expand=True)
        
        self.chart_label = ttk.Label(self.chart_frame, 
                                      text="Thêm ít nhất 1 nguồn tin và nhấn 'Vẽ biểu đồ'",
                                      style='Info.TLabel')
        self.chart_label.pack(expand=True)
        
        # === Chi tiết ===
        self.detail_text = scrolledtext.ScrolledText(detail_tab, wrap=tk.WORD,
                                                      font=('Consolas', 10))
        self.detail_text.pack(fill=tk.BOTH, expand=True)
        
        # Hiển thị công thức
        formula = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                           CÔNG THỨC ENTROPY SHANNON                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║    H(X) = -Σ p(xi) × log₂(p(xi))                                            ║
║                                                                              ║
║    Trong đó:                                                                 ║
║    • H(X)   : Entropy của nguồn tin (bit/ký hiệu)                           ║
║    • p(xi)  : Xác suất xuất hiện của ký hiệu thứ i                          ║
║    • n      : Số lượng ký hiệu khác nhau                                    ║
║                                                                              ║
║    Entropy tối đa: H_max = log₂(n) (khi tất cả ký hiệu có xác suất bằng nhau)║
║    Hiệu suất: η = H(X) / H_max × 100%                                       ║
║    Độ dư tương đối: Rs = 100% - η                                           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

👆 Double-click vào một nguồn tin trong bảng để xem chi tiết phân phối xác suất.
"""
        self.detail_text.insert('1.0', formula)
        
    def filter_english_text(self, text):
        """Chuẩn hóa văn bản về ký tự tiếng Anh (loại bỏ dấu)"""
        # Bước 1: Xử lý ký tự đặc biệt Việt Nam
        vietnamese_map = {
            'đ': 'd', 'Đ': 'D',
        }
        for vn_char, en_char in vietnamese_map.items():
            text = text.replace(vn_char, en_char)
        
        # Bước 2: Loại bỏ dấu (accents) từ các ký tự Latin
        # NFD: Decompose characters to base + combining marks
        nfd_text = unicodedata.normalize('NFD', text)
        # Lọc bỏ các dấu combining marks
        without_accents = ''.join(
            char for char in nfd_text 
            if unicodedata.category(char) != 'Mn'  # Mn = Nonspacing_Mark (dấu)
        )
        
        # Bước 3: Chỉ giữ lại ký tự Latinh cơ bản, số và dấu câu
        filtered_text = re.sub(r'[^a-zA-Z0-9\s\.,!?;:\'"\(\)\-]', '', without_accents)
        
        return filtered_text

    def add_text_source(self):
        """Thêm nguồn tin từ văn bản nhập"""
        text = self.text_input.get('1.0', tk.END).strip()
        if not text:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập văn bản!")
            return
        
        name = self.source_name_var.get() or f"Nguồn tin {len(self.sources) + 1}"
        ignore_spaces = self.ignore_spaces_var.get()
        
        try:
            source_type = self.source_type_var.get()
            
            # Xử lý lọc nếu là tiếng Anh
            if source_type == "Tiếng Anh":
                original_len = len(text)
                text = self.filter_english_text(text)
                if len(text) < original_len:
                    # Có thể thông báo cho người dùng biết đã lọc bỏ một số ký tự
                    # print(f"Đã lọc bỏ {original_len - len(text)} ký tự không hợp lệ")
                    pass

            if source_type == "Nhị phân":
                # Chuyển văn bản thành bytes (UTF-8) để phân tích nhị phân
                data = text.encode('utf-8')
                result = analyze_binary_data(data, name)
            else:
                result = analyze_source(text, name, ignore_spaces)
            
            # Lưu loại nguồn tin để so sánh sau này
            result['source_type'] = source_type
                
            self.sources.append(result)
            self.update_result_table()
            
            # Cập nhật tên mặc định cho nguồn tin tiếp theo
            self.source_name_var.set(f"Nguồn tin {len(self.sources) + 1}")
            
            messagebox.showinfo("Thành công", 
                               f"Đã thêm nguồn tin '{name}'\nEntropy = {result['entropy']:.4f} bit/ký hiệu")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể phân tích: {str(e)}")
    
    
    def browse_file(self):
        """Mở dialog chọn file"""
        filetypes = [
            ("Tất cả file", "*.*"),
            ("File văn bản", "*.txt"),
            ("File Word", "*.docx"),
            ("File nhị phân", "*.bin"),
        ]
        filepath = filedialog.askopenfilename(filetypes=filetypes)
        if filepath:
            self.file_path_var.set(filepath)
            self.preview_file(filepath)
            # Tự động đặt tên theo tên file
            self.file_source_name_var.set(os.path.basename(filepath))
            
            # Tự động chọn loại file nếu là .docx
            if filepath.lower().endswith('.docx'):
                self.file_type_var.set("File Word (.docx)")
    
    def read_docx(self, filepath):
        """Đọc nội dung file Word"""
        try:
            import docx
        except ImportError:
            return "Lỗi: Chưa cài đặt thư viện python-docx. Vui lòng chạy 'pip install python-docx'"
        
        doc = docx.Document(filepath)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)

    def preview_file(self, filepath):
        """Xem trước nội dung file"""
        self.file_preview.config(state='normal')
        self.file_preview.delete('1.0', tk.END)
        
        try:
            # Xử lý file .docx
            if filepath.lower().endswith('.docx'):
                content = self.read_docx(filepath)
                if len(content) > 2000:
                    content = content[:2000] + "\n\n... (còn nữa)"
                self.file_preview.insert('1.0', content)
            else:
                # Thử đọc như văn bản
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read(2000)  # Chỉ hiển thị 2000 ký tự đầu
                        if len(content) == 2000:
                            content += "\n\n... (còn nữa)"
                        self.file_preview.insert('1.0', content)
                except:
                    # Đọc như binary
                    with open(filepath, 'rb') as f:
                        data = f.read(500)
                        hex_str = ' '.join(f'{b:02X}' for b in data)
                        if len(data) == 500:
                            hex_str += "\n\n... (còn nữa)"
                        self.file_preview.insert('1.0', f"[Binary Data]\n\n{hex_str}")
        except Exception as e:
            self.file_preview.insert('1.0', f"Lỗi đọc file: {str(e)}")
        
        self.file_preview.config(state='disabled')
    
    def add_file_source(self):
        """Thêm nguồn tin từ file"""
        filepath = self.file_path_var.get()
        if not filepath:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn file!")
            return
        
        name = self.file_source_name_var.get() or os.path.basename(filepath)
        file_type = self.file_type_var.get()
        
        try:
            if "Nhị phân" in file_type:
                with open(filepath, 'rb') as f:
                    data = f.read()
                result = analyze_binary_data(data, name)
            elif filepath.lower().endswith('.docx') or "Word" in file_type:
                text = self.read_docx(filepath)
                result = analyze_source(text, name)
                file_type = "File Word (.docx)" # Đảm bảo loại file đúng
            else:
                # Thử đọc như văn bản
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        text = f.read()
                    result = analyze_source(text, name)
                except:
                    # Fallback to binary
                    with open(filepath, 'rb') as f:
                        data = f.read()
                    result = analyze_binary_data(data, name)
            
            # Lưu loại nguồn tin
            result['source_type'] = file_type.split(' ')[0] if '(' in file_type else file_type
            
            self.sources.append(result)
            self.update_result_table()
            
            messagebox.showinfo("Thành công", 
                               f"Đã thêm nguồn tin '{name}'\nEntropy = {result['entropy']:.4f} bit/ký hiệu")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đọc file: {str(e)}")
    

    
    def update_result_table(self):
        """Cập nhật bảng kết quả"""
        # Xóa dữ liệu cũ
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        # Thêm dữ liệu mới
        for src in self.sources:
            self.result_tree.insert('', tk.END, values=(
                src['name'],
                src['total_characters'],
                src['num_symbols'],
                f"{src['entropy']:.4f}",
                f"{src['max_entropy']:.4f}",
                f"{src['efficiency']:.2f}",
                f"{src['redundancy']:.2f}"
            ))
    
    def delete_selected_source(self):
        """Xóa nguồn tin được chọn"""
        selection = self.result_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nguồn tin cần xóa!")
            return
        
        # Lấy index của item được chọn
        for item in selection:
            idx = self.result_tree.index(item)
            if 0 <= idx < len(self.sources):
                del self.sources[idx]
        
        self.update_result_table()
    
    def show_charts(self):
        """Hiển thị biểu đồ"""
        if not self.sources:
            messagebox.showwarning("Cảnh báo", "Chưa có nguồn tin nào để vẽ biểu đồ!")
            return
        
        # Xóa widget cũ
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        # Tạo figure
        fig = plot_all_comparisons(self.sources, figsize=(10, 8))
        
        if fig:
            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Chuyển sang tab biểu đồ
            self.result_notebook.select(1)
        
        plt.close(fig)
    
    def show_source_detail(self, event):
        """Hiển thị chi tiết nguồn tin khi double-click"""
        selection = self.result_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        idx = self.result_tree.index(item)
        
        if 0 <= idx < len(self.sources):
            src = self.sources[idx]
            
            # 1. So sánh với tiêu chuẩn
            src_type = src.get('source_type', 'Khác')
            std_val = STANDARD_ENTROPY.get(src_type)
            comparison_text = ""
            if std_val:
                diff = src['entropy'] - std_val
                relation = "cao hơn" if diff > 0 else "thấp hơn"
                comparison_text = f"⚖️ SO SÁNH TIÊU CHUẨN ({src_type}):\n"
                comparison_text += f"   • Entropy tiêu chuẩn: {std_val:.2f} bit/ký hiệu\n"
                comparison_text += f"   • Văn bản của bạn {relation} tiêu chuẩn {abs(diff):.4f} bit.\n"
            
            # 2. Tạo chuỗi công thức thay số
            sorted_probs = sorted(src['probabilities'].items(), 
                                  key=lambda x: x[1], reverse=True)
            
            formula_steps = "🧮 CÁCH TÍNH CHI TIẾT (Thay số):\n"
            formula_steps += "   H(X) = - Σ p_i × log₂(p_i)\n"
            formula_steps += "   H(X) = - ["
            
            terms = []
            # Hiển thị tối đa 8 ký tự đầu tiên trong công thức để tránh quá dài
            display_limit = 6
            for i, (char, prob) in enumerate(sorted_probs[:display_limit]):
                log_val = math.log2(prob) if prob > 0 else 0
                display_char = char
                if char == ' ': display_char = '[sp]'
                elif char == '\n': display_char = '[nl]'
                
                term = f"({prob:.3f} × {log_val:.2f})"
                terms.append(term)
            
            formula_steps += " + ".join(terms)
            if len(sorted_probs) > display_limit:
                formula_steps += " + ... "
            
            formula_steps += "]\n"
            formula_steps += f"   H(X) = {src['entropy']:.6f} bit/ký hiệu\n"

            detail = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           CHI TIẾT NGUỒN TIN                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

📌 Tên: {src['name']} (Loại: {src_type})
📊 Tổng số ký tự: {src['total_characters']:,}
🔤 Số ký hiệu khác nhau: {src['num_symbols']}

📈 CHỈ SỐ ENTROPY:
   • Entropy thực tế: {src['entropy']:.6f} bit/ký hiệu
   • Entropy tối đa:  {src['max_entropy']:.6f} bit/ký hiệu
   • Hiệu suất:       {src['efficiency']:.2f}%
   • Độ dư tương đối: {src['redundancy']:.2f}%

{comparison_text}
{formula_steps}
📋 PHÂN PHỐI XÁC SUẤT (Top 20):
{'─' * 60}
"""
            # Hiển thị top 20 ký tự
            sorted_probs = sorted(src['probabilities'].items(), 
                                  key=lambda x: x[1], reverse=True)[:20]
            
            for i, (char, prob) in enumerate(sorted_probs, 1):
                display_char = char
                if char == ' ':
                    display_char = '[space]'
                elif char == '\n':
                    display_char = '[newline]'
                elif char == '\t':
                    display_char = '[tab]'
                
                bar = '█' * int(prob * 50)
                detail += f"   {i:2}. '{display_char}'  → p = {prob:.4f}  {bar}\n"
            
            self.detail_text.config(state='normal')
            self.detail_text.delete('1.0', tk.END)
            self.detail_text.insert('1.0', detail)
            self.detail_text.config(state='disabled')
            
            # Chuyển sang tab chi tiết
            self.result_notebook.select(2)
    
    def clear_all(self):
        """Xóa tất cả dữ liệu"""
        if self.sources:
            if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa tất cả nguồn tin?"):
                self.sources.clear()
                self.update_result_table()
                
                # Xóa biểu đồ
                for widget in self.chart_frame.winfo_children():
                    widget.destroy()
                self.chart_label = ttk.Label(self.chart_frame, 
                                              text="Thêm ít nhất 1 nguồn tin và nhấn 'Vẽ biểu đồ'",
                                              style='Info.TLabel')
                self.chart_label.pack(expand=True)
    
    def export_results(self):
        """Xuất kết quả ra file"""
        if not self.sources:
            messagebox.showwarning("Cảnh báo", "Chưa có kết quả để xuất!")
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text file", "*.txt"), ("All files", "*.*")]
        )
        
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("=" * 80 + "\n")
                    f.write("           KẾT QUẢ PHÂN TÍCH ENTROPY CÁC NGUỒN TIN\n")
                    f.write("=" * 80 + "\n\n")
                    
                    f.write(compare_sources(self.sources))
                    
                    f.write("\n\n" + "=" * 80 + "\n")
                    f.write("                         CHI TIẾT TỪNG NGUỒN\n")
                    f.write("=" * 80 + "\n")
                    
                    for src in self.sources:
                        f.write(f"\n{'─' * 40}\n")
                        f.write(f"Nguồn: {src['name']}\n")
                        f.write(f"Entropy: {src['entropy']:.6f} bit/ký hiệu\n")
                        f.write(f"Hiệu suất: {src['efficiency']:.2f}%\n")
                
                messagebox.showinfo("Thành công", f"Đã xuất kết quả ra:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xuất file: {str(e)}")


def main():
    """Hàm chính khởi chạy ứng dụng"""
    root = tk.Tk()
    
    # Icon (nếu có)
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    app = EntropyCalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
