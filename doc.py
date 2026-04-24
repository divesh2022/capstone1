import os
import ast
import re

SUPPORTED_EXTENSIONS = [".py", ".js", ".java", ".c", ".cpp", ".h", ".ts"]

def extract_python_functions(source):
    results = []
    try:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                docstring = ast.get_docstring(node) or ""
                results.append((func_name, docstring))
    except SyntaxError:
        pass
    return results

def extract_other_functions(source):
    results = []
    patterns = [
        r"function\s+(\w+)\(",           # JS
        r"\w+\s+(\w+)\s*\([^)]*\)\s*{", # C/Java style
    ]
    for line in source.splitlines():
        for pat in patterns:
            match = re.search(pat, line)
            if match:
                results.append((match.group(1), ""))  # no docstring concept here
    return results

def extract_comments_and_strings(source, ext):
    docs = []
    lines = source.splitlines()

    # Comments
    for line in lines:
        line = line.strip()
        if ext == ".py" and line.startswith("#"):
            docs.append(line)
        elif ext in [".js", ".java", ".c", ".cpp", ".h", ".ts"]:
            if line.startswith("//") or "/*" in line or "*/" in line:
                docs.append(line)

    # Multiline strings (Python only)
    if ext == ".py":
        multiline_pattern = r'("""|\'\'\')(.*?)("""|\'\'\')'
        matches = re.findall(multiline_pattern, source, re.DOTALL)
        for _, content, _ in matches:
            docs.append(content.strip())

    return docs

def scan_folder(folder_path, output_file="documentation.txt"):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("Source Code Documentation\n")
        f.write("="*50 + "\n\n")
        for root, _, files in os.walk(folder_path):
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext in SUPPORTED_EXTENSIONS:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as src:
                            source = src.read()
                    except Exception:
                        continue

                    if ext == ".py":
                        funcs = extract_python_functions(source)
                    else:
                        funcs = extract_other_functions(source)

                    docs = extract_comments_and_strings(source, ext)

                    f.write(f"File: {file_path}\n")
                    if not funcs:
                        f.write("  Function: None\n")
                    else:
                        for func_name, docstring in funcs:
                            f.write(f"  Function: {func_name}\n")
                            if docstring:
                                f.write(f"    Docstring: {docstring}\n")

                    if docs:
                        f.write("  Documentation Extracted:\n")
                        for d in docs:
                            f.write(f"    {d}\n")

                    f.write("-"*50 + "\n\n")

    print(f"Text documentation written to {output_file}")

# Example usage
if __name__ == "__main__":
    folder_to_scan = r"E:\project\capstone\frontend"  # replace with your folder path
    scan_folder(folder_to_scan, output_file="documentation.txt")
