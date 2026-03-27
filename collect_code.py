import os

# 配置项
output_file = 'classvision.txt' # 输出文件名
exclude_dirs = {'.venv', '__pycache__', 'node_modules', '.git', 'dist', 'build', 'public', 'assets'} # 忽略的目录
include_exts = {'.py', '.ts', '.js', '.vue', '.html', '.css', '.json', '.md', '.mdx'} # 要提取的文件扩展名

def collect_code(start_path='.'):
    total_files = 0
    with open(output_file, 'w', encoding='utf-8') as out_f:
        for root, dirs, files in os.walk(start_path):
            # 原地修改 dirs 以跳过排除的目录
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in include_exts:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as in_f:
                            content = in_f.read()
                        
                        out_f.write(f"{'='*60}\n")
                        out_f.write(f"File: {file_path}\n")
                        out_f.write(f"{'='*60}\n\n")
                        out_f.write(content)
                        out_f.write("\n\n")
                        total_files += 1
                        print(f"已添加: {file_path}")
                    except Exception as e:
                        print(f"跳过文件 {file_path} (无法读取): {e}")
                        
    print(f"\n收集完成！共提取了 {total_files} 个代码文件的内容，已保存至 {output_file}。")

if __name__ == '__main__':
    collect_code()
