import re
import sys

variables = {}


def safe_int(val):
    try:
        return int(val)
    except:
        return 0


allowed_builtins = {
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,
    "safe_int": safe_int,
}


def eval_expr_value(expr):
    local_vars = {var: variables[var] for var in variables}
    try:
        return eval(
            expr, {"__builtins__": allowed_builtins, "safe_int": safe_int}, local_vars
        )
    except Exception as e:
        print(f"[Erreur évaluation] {e} dans expression: {expr}")
        return expr.strip('"').strip("'")


def eval_expr_string(expr):
    # Convertit toutes les variables en string pour concaténation
    local_vars = {var: str(variables[var]) for var in variables}
    try:
        return eval(
            expr, {"__builtins__": allowed_builtins, "safe_int": safe_int}, local_vars
        )
    except Exception as e:
        print(f"[Erreur dans eval_expr_string] {e} dans expression : {expr}")
        return expr.strip('"').strip("'")


def extract_block(lines, start):
    block = []
    depth = 0
    i = start
    while i < len(lines):
        line = lines[i].strip()
        depth += line.count("{")
        depth -= line.count("}")
        if depth < 0:
            break
        if depth > 0 or (depth == 0 and "}" not in line):
            block.append(line)
        if depth == 0 and line.endswith("}"):
            break
        i += 1
    return block, i


def run_block(block_lines):
    for line in block_lines:
        run_line(line)


def run_line(line):
    line = line.strip()
    if not line or line.startswith("&"):
        return

    if line.startswith("set_var("):
        m = re.match(r"set_var\((\w+)\)\s*=\s*(.+)", line)
        if m:
            name, value = m.groups()
            variables[name] = eval_expr_value(value)
        else:
            print(f"[Erreur] Syntaxe invalide : {line}")

    elif line.startswith("logger(") and line.endswith(")"):
        content = line[7:-1]
        print(eval_expr_string(content))

    elif line.startswith("ask(") and line.endswith(")"):
        m = re.match(r'ask\((\w+)\s*,\s*"(.*)"\)', line)
        if m:
            var_name, question = m.groups()
            answer = input(question + " ")
            variables[var_name] = answer
        else:
            print(f"[Erreur] Syntaxe invalide pour ask : {line}")

    else:
        print(f"[Erreur] Ligne inconnue : {line}")


def run_script(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = [l.rstrip() for l in f]
    except FileNotFoundError:
        print(f"[Erreur] Fichier introuvable : {filename}")
        return

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("if(") and line.endswith("{"):
            cond = re.match(r"if\((.+)\)\s*\{", line).group(1)
            cond_value = eval_expr_value(cond)
            cond_bool = bool(cond_value)

            true_block, end_true = extract_block(lines, i + 1)

            else_block = []
            j = end_true + 1
            if j < len(lines) and lines[j].strip().startswith("else"):
                else_block, end_else = extract_block(lines, j + 1)
                i = end_else
            else:
                i = end_true

            if cond_bool:
                run_block(true_block)
            else:
                run_block(else_block)
        else:
            run_line(line)
        i += 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage : est script.easyt")
        sys.exit(1)
    run_script(sys.argv[1])
