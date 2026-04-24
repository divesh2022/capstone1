import requests

def build_tree(paths):
    tree = {}
    for path in paths:
        parts = path.split('/')
        current = tree
        for part in parts[:-1]:
            if part not in current or not isinstance(current[part], dict):
                current[part] = {}
            current = current[part]
        # mark the last part as a file
        current[parts[-1]] = None
    return tree

def format_tree(tree, prefix=""):
    lines = []
    keys = sorted(tree.keys())
    for i, key in enumerate(keys):
        is_last = i == len(keys) - 1
        connector = "└── " if is_last else "├── "
        if isinstance(tree[key], dict):
            lines.append(f"{prefix}{connector}{key}/")
            extension = "    " if is_last else "│   "
            lines.extend(format_tree(tree[key], prefix + extension))
        else:
            lines.append(f"{prefix}{connector}{key}")
    return lines

def etl_repo_structure(repo_owner, repo_name, branch="main"):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/git/trees/{branch}?recursive=1"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    paths = [item["path"] for item in data["tree"]]
    tree = build_tree(paths)

    output = [f"{repo_name}/"]
    output.extend(format_tree(tree))
    return "\n".join(output)

if __name__ == "__main__":
    repo_owner = "divesh2022"
    repo_name = "capstone1"
    print(etl_repo_structure(repo_owner, repo_name))
