import os
import sys
import argparse


def read_file_with_encoding(file_path, encodings=['utf-8', 'gbk', 'gb2312', 'utf-16', 'latin-1']):
    """尝试多种编码读取文件"""
    content = None
    used_encoding = None
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                used_encoding = encoding
                break
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    if content is None:
        with open(file_path, 'rb') as f:
            content = f.read()
        used_encoding = 'binary'
    
    return content, used_encoding


def generate_position_number_line(start_pos, length):
    """
    生成位置数字行，每个字符位置显示对应位置的个位数字
    例如：位置0-25显示为：
    0        10        20      
    01234567890123456789012345
    """
    tens_line = []
    ones_line = []
    
    for i in range(length):
        pos = start_pos + i
        
        if pos % 10 == 0:
            pos_str = str(pos)
            if len(pos_str) == 1:
                tens_line.append(' ')
            elif len(pos_str) == 2:
                tens_line.append(pos_str[0])
            else:
                tens_line.append(pos_str[-2])
            ones_line.append(pos_str[-1])
        else:
            tens_line.append(' ')
            ones_line.append(str(pos % 10))
    
    return {
        'tens': ''.join(tens_line),
        'ones': ''.join(ones_line)
    }


def generate_ruler_markers(start_pos, length):
    """
    生成标尺标记线：
    - 10的倍数位置用 | 标记
    - 5的倍数位置用 + 标记
    - 其他位置用 - 标记
    """
    markers = []
    for i in range(length):
        pos = start_pos + i
        if pos % 10 == 0:
            markers.append('|')
        elif pos % 5 == 0:
            markers.append('+')
        else:
            markers.append('-')
    return ''.join(markers)


def format_content_line(chunk, start_pos):
    """
    格式化内容行，每个字符占一个位置
    特殊字符：
    - 制表符 \t 显示为 →
    - 空格显示为 ·
    - 不可打印字符显示为 ?
    """
    content = []
    for char in chunk:
        if char == '\t':
            content.append('→')
        elif char == ' ':
            content.append('·')
        elif char.isprintable():
            content.append(char)
        else:
            content.append('?')
    return ''.join(content)


def generate_ruler_lines(chunk, start_pos):
    """
    生成简洁的标尺系统，每个字符位置占一个位：
    1. 十位数字行（显示10的倍数位置的十位）
    2. 个位数字行（显示每个位置的个位）
    3. 标记线（| 标记10的倍数，+ 标记5的倍数）
    4. 内容行
    """
    chunk_len = len(chunk)
    
    position_numbers = generate_position_number_line(start_pos, chunk_len)
    marker_line = generate_ruler_markers(start_pos, chunk_len)
    content_line = format_content_line(chunk, start_pos)
    
    return {
        'tens': position_numbers['tens'],
        'ones': position_numbers['ones'],
        'markers': marker_line,
        'content': content_line,
        'chunk_len': chunk_len
    }


def generate_compact_ruler(chunk, start_pos):
    """生成紧凑版标尺，简化显示"""
    return generate_ruler_lines(chunk, start_pos)


def display_file_content(file_path, start_line=0, max_lines=None, show_binary=False, compact_mode=False):
    """显示文件内容带简洁标尺"""
    if not os.path.exists(file_path):
        print(f"\n[错误] 文件 '{file_path}' 不存在")
        return False
    
    content, encoding = read_file_with_encoding(file_path)
    
    print(f"\n{'='*80}")
    print(f"文件: {file_path}")
    print(f"编码: {encoding}")
    print(f"{'='*80}")
    
    if encoding == 'binary' or show_binary:
        display_binary_content(content)
        return True
    
    lines = content.splitlines()
    
    if max_lines is None:
        max_lines = len(lines)
    
    end_line = min(start_line + max_lines, len(lines))
    
    for line_num in range(start_line, end_line):
        line = lines[line_num]
        line_length = len(line)
        
        print(f"\n{'-'*80}")
        print(f"第 {line_num + 1} 行 (共 {len(lines)} 行) | 字符数: {line_length}")
        print(f"{'-'*80}")
        
        if line_length == 0:
            print("  (空行)")
            continue
        
        max_width = 60
        num_chunks = (line_length + max_width - 1) // max_width
        
        for chunk_idx in range(num_chunks):
            start_pos = chunk_idx * max_width
            end_pos = min(start_pos + max_width, line_length)
            chunk = line[start_pos:end_pos]
            chunk_len = len(chunk)
            
            ruler = generate_ruler_lines(chunk, start_pos)
            
            print(f"\n  列 {start_pos:3d} - {end_pos-1:3d}:")
            print(f"  {'-'*(chunk_len + 2)}")
            print(f"  十位: {ruler['tens']}")
            print(f"  个位: {ruler['ones']}")
            print(f"  标记: {ruler['markers']}")
            print(f"  内容: {ruler['content']}")
            print(f"  {'-'*(chunk_len + 2)}")
            
            if not compact_mode:
                print(f"\n  详细信息:")
                print(f"  {'-'*50}")
                for i, char in enumerate(chunk):
                    col = start_pos + i
                    
                    if char == '\t':
                        char_repr = '\\t'
                        display_char = '→'
                    elif char == ' ':
                        char_repr = '空格'
                        display_char = '·'
                    elif char.isprintable():
                        char_repr = char
                        display_char = char
                    else:
                        char_repr = repr(char).strip("'")
                        display_char = '?'
                    
                    print(f"  [{col:4d}]  '{display_char}' | 十六进制: 0x{ord(char):04X} | 十进制: {ord(char):5d} | {char_repr}")
    
    print(f"\n{'='*80}")
    print(f"统计:")
    print(f"   总字符数: {len(content)}")
    print(f"   总行数: {len(lines)}")
    print(f"{'='*80}\n")
    
    return True


def display_binary_content(content):
    """以二进制模式显示文件内容"""
    print("\n二进制模式显示:\n")
    
    bytes_per_line = 16
    total_bytes = len(content) if isinstance(content, bytes) else len(content.encode('latin-1'))
    
    if isinstance(content, str):
        content = content.encode('latin-1')
    
    print(f"{'偏移量(十六进制)':<14} {'十六进制数据':<48} {'ASCII'}")
    print(f"{'-'*14} {'-'*48} {'-'*16}")
    
    for i in range(0, total_bytes, bytes_per_line):
        chunk = content[i:i+bytes_per_line]
        
        hex_part = []
        ascii_part = []
        
        for j, byte in enumerate(chunk):
            hex_part.append(f"{byte:02X}")
            if 32 <= byte <= 126:
                ascii_part.append(chr(byte))
            else:
                ascii_part.append('.')
        
        while len(hex_part) < bytes_per_line:
            hex_part.append('  ')
        
        hex_str = ' '.join(hex_part)
        ascii_str = ''.join(ascii_part)
        
        print(f"{i:08X}       {hex_str}  {ascii_str}")


def search_character(file_path, search_char):
    """搜索指定字符在文件中的位置"""
    content, encoding = read_file_with_encoding(file_path)
    
    if encoding == 'binary':
        print("\n[错误] 二进制文件不支持字符搜索")
        return
    
    lines = content.splitlines()
    
    print(f"\n{'='*60}")
    print(f"搜索字符: '{search_char}'")
    print(f"{'='*60}")
    
    found = False
    results = []
    
    for line_num, line in enumerate(lines):
        for col_num, char in enumerate(line):
            if char == search_char:
                results.append((line_num + 1, col_num, line))
                found = True
    
    if not found:
        print(f"\n未找到字符 '{search_char}'")
    else:
        print(f"\n找到 {len(results)} 个匹配:\n")
        for line_num, col_num, line in results:
            context_start = max(0, col_num - 10)
            context_end = min(len(line), col_num + 11)
            context = line[context_start:context_end]
            
            marker_pos = col_num - context_start
            
            print(f"第 {line_num} 行, 第 {col_num} 列")
            print(f"   上下文: ...{context}...")
            print(f"            {' '*(3+marker_pos)}^")
            print()
    
    print(f"{'='*60}\n")


def interactive_mode():
    """交互式模式"""
    print("\n" + "="*60)
    print("DAT文件字符位置查看器 - 交互式模式")
    print("="*60)
    
    compact_mode = False
    
    while True:
        print("\n请选择操作:")
        print("  1. 查看文件内容 (带标尺)")
        print("  2. 搜索指定字符位置")
        print("  3. 切换显示模式 (当前: " + ("紧凑" if compact_mode else "详细") + ")")
        print("  4. 退出")
        
        choice = input("\n请输入选项 (1/2/3/4): ").strip()
        
        if choice == '4':
            print("\n再见!")
            break
        
        elif choice == '3':
            compact_mode = not compact_mode
            print(f"\n显示模式已切换为: " + ("紧凑模式" if compact_mode else "详细模式"))
        
        elif choice == '1':
            file_path = input("请输入.dat文件路径: ").strip()
            file_path = file_path.strip('"\'')
            
            start_line = input("从第几行开始查看 (默认1): ").strip()
            start_line = int(start_line) - 1 if start_line.isdigit() else 0
            
            max_lines = input("显示多少行 (默认全部): ").strip()
            max_lines = int(max_lines) if max_lines.isdigit() else None
            
            display_file_content(file_path, start_line, max_lines, compact_mode=compact_mode)
        
        elif choice == '2':
            file_path = input("请输入.dat文件路径: ").strip()
            file_path = file_path.strip('"\'')
            
            search_str = input("请输入要搜索的字符: ").strip()
            if len(search_str) > 0:
                search_character(file_path, search_str[0])
        
        else:
            print("\n无效选项，请重新选择。")


def main():
    parser = argparse.ArgumentParser(
        description='DAT文件字符位置查看器 - 以友好的标尺形式显示文件中字符的位置'
    )
    
    parser.add_argument('file', nargs='?', help='要查看的.dat文件路径')
    parser.add_argument('-s', '--start', type=int, default=1, help='起始行号 (默认: 1)')
    parser.add_argument('-n', '--lines', type=int, help='显示的行数 (默认: 全部)')
    parser.add_argument('-b', '--binary', action='store_true', help='以二进制模式查看')
    parser.add_argument('-c', '--char', help='搜索指定字符的位置')
    parser.add_argument('-i', '--interactive', action='store_true', help='交互式模式')
    parser.add_argument('--compact', action='store_true', help='紧凑显示模式')
    
    args = parser.parse_args()
    
    if args.interactive or not args.file:
        interactive_mode()
        return
    
    file_path = args.file.strip('"\'')
    
    if args.char:
        search_character(file_path, args.char[0])
    else:
        start_line = max(0, args.start - 1)
        display_file_content(file_path, start_line, args.lines, args.binary, args.compact)


if __name__ == '__main__':
    main()
