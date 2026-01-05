import math
from collections import Counter
from typing import Dict, List, Tuple, Optional


def calculate_frequency(text: str, ignore_spaces: bool = True) -> Dict[str, int]:
    if ignore_spaces:
        text = text.replace(" ", "").replace("\n", "").replace("\t", "").replace("\r", "")
    
    return dict(Counter(text))


def calculate_probability(frequencies: Dict[str, int]) -> Dict[str, float]:
    total = sum(frequencies.values())
    if total == 0:
        return {}
    
    return {char: count / total for char, count in frequencies.items()}


def calculate_entropy(probabilities: Dict[str, float]) -> float:
    if not probabilities:
        return 0.0
    
    entropy = 0.0
    for prob in probabilities.values():
        if prob > 0:
            entropy -= prob * math.log2(prob)
    
    return entropy


def calculate_max_entropy(num_symbols: int) -> float:
    if num_symbols <= 1:
        return 0.0
    return math.log2(num_symbols)


def calculate_efficiency(entropy: float, max_entropy: float) -> float:
    if max_entropy == 0:
        return 0.0
    return (entropy / max_entropy) * 100


def analyze_source(text: str, source_name: str = "Unknown", 
                   ignore_spaces: bool = True) -> Dict:
    """
    Phân tích đầy đủ một nguồn tin.
    
    Args:
        text: Văn bản/dữ liệu cần phân tích
        source_name: Tên nguồn tin
        ignore_spaces: Bỏ qua khoảng trắng
        
    Returns:
        Dictionary chứa tất cả thông tin phân tích
    """
    frequencies = calculate_frequency(text, ignore_spaces)
    probabilities = calculate_probability(frequencies)
    entropy = calculate_entropy(probabilities)
    num_symbols = len(frequencies)
    max_entropy = calculate_max_entropy(num_symbols)
    efficiency = calculate_efficiency(entropy, max_entropy)
    total_chars = sum(frequencies.values())
    
    # Sắp xếp xác suất theo thứ tự giảm dần
    sorted_probs = dict(sorted(probabilities.items(), 
                               key=lambda x: x[1], reverse=True))
    
    return {
        "name": source_name,
        "total_characters": total_chars,
        "num_symbols": num_symbols,
        "frequencies": frequencies,
        "probabilities": sorted_probs,
        "entropy": entropy,
        "max_entropy": max_entropy,
        "efficiency": efficiency,
        "redundancy": 100 - efficiency  # Độ dư tương đối
    }


def analyze_binary_data(data: bytes, source_name: str = "Binary") -> Dict:
    """
    Phân tích dữ liệu nhị phân (theo byte).
    
    Args:
        data: Dữ liệu nhị phân
        source_name: Tên nguồn tin
        
    Returns:
        Dictionary chứa thông tin phân tích
    """
    # Chuyển bytes thành danh sách các giá trị byte (0-255)
    byte_values = list(data)
    frequencies = dict(Counter(byte_values))
    
    # Chuyển key thành string để hiển thị
    frequencies_str = {f"0x{k:02X}": v for k, v in frequencies.items()}
    
    probabilities = calculate_probability(frequencies)
    probabilities_str = {f"0x{k:02X}": v for k, v in probabilities.items()}
    
    entropy = calculate_entropy(probabilities)
    num_symbols = len(frequencies)
    max_entropy = calculate_max_entropy(num_symbols)  # Tính theo số ký hiệu thực tế
    efficiency = calculate_efficiency(entropy, max_entropy)
    
    sorted_probs = dict(sorted(probabilities_str.items(), 
                               key=lambda x: x[1], reverse=True))
    
    return {
        "name": source_name,
        "total_characters": len(data),
        "num_symbols": num_symbols,
        "frequencies": frequencies_str,
        "probabilities": sorted_probs,
        "entropy": entropy,
        "max_entropy": max_entropy,
        "efficiency": efficiency,
        "redundancy": 100 - efficiency
    }


def compare_sources(sources: List[Dict]) -> str:
    """
    Tạo bảng so sánh các nguồn tin.
    
    Args:
        sources: Danh sách kết quả phân tích từ analyze_source
        
    Returns:
        Chuỗi văn bản dạng bảng để hiển thị
    """
    if not sources:
        return "Không có nguồn tin để so sánh."
    
    header = f"{'Nguồn tin':<20} {'Số ký tự':>10} {'Số ký hiệu':>12} {'Entropy':>10} {'H_max':>10} {'Hiệu suất':>12}"
    separator = "-" * 80
    
    lines = [header, separator]
    
    for src in sources:
        line = f"{src['name']:<20} {src['total_characters']:>10} {src['num_symbols']:>12} {src['entropy']:>10.4f} {src['max_entropy']:>10.4f} {src['efficiency']:>11.2f}%"
        lines.append(line)
    
    return "\n".join(lines)


# Demo test
if __name__ == "__main__":
    # Test với các chuỗi đơn giản
    print("=== Test Entropy Calculator ===\n")
    
    # Test 1: Chuỗi chỉ có 1 ký tự -> Entropy = 0
    test1 = "AAAA"
    result1 = analyze_source(test1, "Chỉ ký tự A")
    print(f"Test 1: '{test1}'")
    print(f"  Entropy = {result1['entropy']:.4f} bit (expected: 0)\n")
    
    # Test 2: Chuỗi 2 ký tự 50-50 -> Entropy = 1
    test2 = "ABAB"
    result2 = analyze_source(test2, "A và B 50-50")
    print(f"Test 2: '{test2}'")
    print(f"  Entropy = {result2['entropy']:.4f} bit (expected: 1)\n")
    
    # Test 3: Văn bản tiếng Việt
    test3 = "Xin chào Việt Nam"
    result3 = analyze_source(test3, "Tiếng Việt")
    print(f"Test 3: '{test3}'")
    print(f"  Entropy = {result3['entropy']:.4f} bit")
    print(f"  Số ký hiệu = {result3['num_symbols']}")
    print(f"  Hiệu suất = {result3['efficiency']:.2f}%\n")
    
    # So sánh
    print("\n=== So sánh các nguồn tin ===\n")
    print(compare_sources([result1, result2, result3]))
