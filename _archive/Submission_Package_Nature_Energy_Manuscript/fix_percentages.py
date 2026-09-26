import re

files = ["Manuscript_NatureEnergy_26-06-25.tex", "SI.tex"]


def replace_percentages(text):
    # Replace ranges: e.g., 12--18\% -> \qtyrange{12}{18}{\percent}
    text = re.sub(r"(\d+(?:\.\d+)?)--(\d+(?:\.\d+)?)\\%", r"\\qtyrange{\1}{\2}{\\percent}", text)

    # Replace ranges with hyphen: e.g., 5-8\% -> \qtyrange{5}{8}{\percent} (just in case, but usually -- in latex)
    text = re.sub(r"(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)\\%", r"\\qtyrange{\1}{\2}{\\percent}", text)

    # Replace minus signs in tables: e.g., $-$94.8\% -> \qty{-94.8}{\percent}
    text = re.sub(r"\$-\$-(\d+(?:\.\d+)?)\\%", r"\\qty{-\1}{\\percent}", text)

    # Replace single percentages: e.g., 85\% -> \qty{85}{\percent}
    text = re.sub(r"(\d+(?:\.\d+)?)\\%", r"\\qty{\1}{\\percent}", text)

    return text


for filename in files:
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = replace_percentages(content)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(new_content)

print("Replacements done.")
