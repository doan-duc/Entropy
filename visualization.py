import matplotlib.pyplot as plt
import matplotlib
from typing import List, Dict, Optional
import numpy as np

# Cấu hình font hỗ trợ tiếng Việt
matplotlib.rcParams['font.family'] = ['DejaVu Sans', 'Arial', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False


def plot_entropy_comparison(sources: List[Dict], figsize: tuple = (10, 6)) -> plt.Figure:
    if not sources:
        return None
    
    fig, ax = plt.subplots(figsize=figsize)
    
    names = [src['name'] for src in sources]
    entropies = [src['entropy'] for src in sources]
    max_entropies = [src['max_entropy'] for src in sources]
    
    x = np.arange(len(names))
    width = 0.35
    
    # Vẽ cột entropy thực tế và entropy max
    bars1 = ax.bar(x - width/2, entropies, width, label='Entropy thực tế', 
                   color='#3498db', edgecolor='white', linewidth=1)
    bars2 = ax.bar(x + width/2, max_entropies, width, label='Entropy tối đa', 
                   color='#e74c3c', alpha=0.7, edgecolor='white', linewidth=1)
    
    # Thêm giá trị lên đầu cột
    for bar, val in zip(bars1, entropies):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f'{val:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    for bar, val in zip(bars2, max_entropies):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f'{val:.3f}', ha='center', va='bottom', fontsize=10)
    
    ax.set_xlabel('Nguồn tin', fontsize=12)
    ax.set_ylabel('Entropy (bit/ký hiệu)', fontsize=12)
    ax.set_title('So sánh Entropy giữa các nguồn tin', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=15, ha='right')
    ax.legend(loc='upper right')
    ax.grid(axis='y', alpha=0.3)
    
    # Đặt giới hạn y để có khoảng trống cho labels
    max_val = max(max_entropies) if max_entropies else 1
    ax.set_ylim(0, max_val * 1.2)
    
    plt.tight_layout()
    return fig


def plot_efficiency_comparison(sources: List[Dict], figsize: tuple = (10, 6)) -> plt.Figure:
    if not sources:
        return None
    
    fig, ax = plt.subplots(figsize=figsize)
    
    names = [src['name'] for src in sources]
    efficiencies = [src['efficiency'] for src in sources]
    redundancies = [src['redundancy'] for src in sources]
    
    x = np.arange(len(names))
    
    # Stacked bar chart
    bars1 = ax.bar(x, efficiencies, label='Hiệu suất (%)', 
                   color='#2ecc71', edgecolor='white', linewidth=1)
    bars2 = ax.bar(x, redundancies, bottom=efficiencies, 
                   label='Độ dư tương đối (%)', color='#e67e22', alpha=0.7,
                   edgecolor='white', linewidth=1)
    
    # Thêm labels
    for bar, val in zip(bars1, efficiencies):
        if val > 5:  # Chỉ hiển thị nếu đủ lớn
            ax.text(bar.get_x() + bar.get_width()/2, val/2,
                    f'{val:.1f}%', ha='center', va='center', 
                    fontsize=10, fontweight='bold', color='white')
    
    ax.set_xlabel('Nguồn tin', fontsize=12)
    ax.set_ylabel('Phần trăm (%)', fontsize=12)
    ax.set_title('Hiệu suất sử dụng Entropy', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=15, ha='right')
    ax.legend(loc='upper right')
    ax.set_ylim(0, 110)
    ax.axhline(y=100, color='gray', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    return fig


def plot_probability_distribution(source: Dict, top_n: int = 20, 
                                   figsize: tuple = (12, 6)) -> plt.Figure:
    if not source or not source.get('probabilities'):
        return None
    
    fig, ax = plt.subplots(figsize=figsize)
    
    probs = source['probabilities']
    
    # Lấy top N ký tự có xác suất cao nhất
    sorted_items = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    chars = [item[0] for item in sorted_items]
    values = [item[1] for item in sorted_items]
    
    # Tạo màu gradient
    colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(chars)))
    
    bars = ax.bar(range(len(chars)), values, color=colors, edgecolor='white', linewidth=1)
    
    # Format labels cho ký tự đặc biệt
    display_chars = []
    for c in chars:
        if c == ' ':
            display_chars.append('[space]')
        elif c == '\n':
            display_chars.append('[newline]')
        elif c == '\t':
            display_chars.append('[tab]')
        else:
            display_chars.append(c)
    
    ax.set_xlabel('Ký tự', fontsize=12)
    ax.set_ylabel('Xác suất', fontsize=12)
    ax.set_title(f'Phân phối xác suất - {source["name"]}', fontsize=14, fontweight='bold')
    ax.set_xticks(range(len(chars)))
    ax.set_xticklabels(display_chars, rotation=45, ha='right', fontsize=9)
    ax.grid(axis='y', alpha=0.3)
    
    # Thêm giá trị lên đầu cột
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                f'{val:.3f}', ha='center', va='bottom', fontsize=8, rotation=45)
    
    plt.tight_layout()
    return fig


def plot_all_comparisons(sources: List[Dict], figsize: tuple = (14, 10)) -> plt.Figure:
    if not sources:
        return None
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    
    # Biểu đồ 1: So sánh entropy
    names = [src['name'] for src in sources]
    entropies = [src['entropy'] for src in sources]
    max_entropies = [src['max_entropy'] for src in sources]
    
    x = np.arange(len(names))
    width = 0.35
    
    axes[0, 0].bar(x - width/2, entropies, width, label='Entropy', color='#3498db')
    axes[0, 0].bar(x + width/2, max_entropies, width, label='H_max', color='#e74c3c', alpha=0.7)
    axes[0, 0].set_title('So sánh Entropy', fontweight='bold')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(names, rotation=15, ha='right', fontsize=9)
    axes[0, 0].legend()
    axes[0, 0].grid(axis='y', alpha=0.3)
    
    # Biểu đồ 2: Hiệu suất
    efficiencies = [src['efficiency'] for src in sources]
    colors = ['#2ecc71' if e >= 80 else '#f39c12' if e >= 50 else '#e74c3c' 
              for e in efficiencies]
    
    axes[0, 1].bar(x, efficiencies, color=colors, edgecolor='white')
    axes[0, 1].axhline(y=100, color='gray', linestyle='--', alpha=0.5)
    axes[0, 1].set_title('Hiệu suất sử dụng (%)', fontweight='bold')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(names, rotation=15, ha='right', fontsize=9)
    axes[0, 1].set_ylim(0, 110)
    axes[0, 1].grid(axis='y', alpha=0.3)
    
    # Biểu đồ 3: Số ký hiệu
    num_symbols = [src['num_symbols'] for src in sources]
    axes[1, 0].bar(x, num_symbols, color='#9b59b6', edgecolor='white')
    axes[1, 0].set_title('Số ký hiệu khác nhau', fontweight='bold')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(names, rotation=15, ha='right', fontsize=9)
    axes[1, 0].grid(axis='y', alpha=0.3)
    
    # Biểu đồ 4: Độ dư thừa
    redundancies = [src['redundancy'] for src in sources]
    axes[1, 1].bar(x, redundancies, color='#e67e22', edgecolor='white')
    axes[1, 1].set_title('Độ dư tương đối (%)', fontweight='bold')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(names, rotation=15, ha='right', fontsize=9)
    axes[1, 1].set_ylim(0, max(redundancies) * 1.2 if redundancies else 100)
    axes[1, 1].grid(axis='y', alpha=0.3)
    
    plt.suptitle('Phân tích Entropy các nguồn tin', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    return fig


# Demo
if __name__ == "__main__":
    # Dữ liệu mẫu để test
    sample_sources = [
        {
            "name": "Tiếng Việt",
            "entropy": 4.2,
            "max_entropy": 5.0,
            "efficiency": 84.0,
            "redundancy": 16.0,
            "num_symbols": 32,
            "probabilities": {"a": 0.12, "n": 0.08, "t": 0.07, "e": 0.06}
        },
        {
            "name": "Tiếng Anh",
            "entropy": 4.0,
            "max_entropy": 4.7,
            "efficiency": 85.1,
            "redundancy": 14.9,
            "num_symbols": 26,
            "probabilities": {"e": 0.13, "t": 0.09, "a": 0.08, "o": 0.07}
        },
        {
            "name": "Nhị phân",
            "entropy": 7.8,
            "max_entropy": 8.0,
            "efficiency": 97.5,
            "redundancy": 2.5,
            "num_symbols": 256,
            "probabilities": {}
        }
    ]
    
    # Test vẽ biểu đồ
    fig = plot_all_comparisons(sample_sources)
    plt.show()
