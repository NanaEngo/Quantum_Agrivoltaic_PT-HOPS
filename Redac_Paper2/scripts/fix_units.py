import re


def replace_units(file_path):
    with open(file_path, "r") as f:
        content = f.read()

    # Replaces
    replacements = [
        (r"24--48~h", r"\\qtyrange{24}{48}{\\hour}"),
        (r"2--4~h", r"\\qtyrange{2}{4}{\\hour}"),
        (r"4\.23~yr", r"\\qty{4.23}{\\year}"),
        (r"8\.0~yr", r"\\qty{8.0}{\\year}"),
        (r"4~yr", r"\\qty{4}{\\year}"),
        (r"8\.2~kg", r"\\qty{8.2}{\\kilo\\gram}"),
        (r"25\.8~kg", r"\\qty{25.8}{\\kilo\\gram}"),
        (r"0\.68~kg", r"\\qty{0.68}{\\kilo\\gram}"),
        (r"128~GB", r"\\qty{128}{\\giga\\byte}"),
    ]

    new_content = content
    for pattern, repl in replacements:
        new_content = re.sub(pattern, repl, new_content)

    if new_content != content:
        with open(file_path, "w") as f:
            f.write(new_content)
        print(f"Updated {file_path}")


replace_units(
    "Redac_Paper2/Submission_Package_Nature_Energy_Manuscript/Manuscript_NatureEnergy_26-06-25.tex"
)
replace_units("Redac_Paper2/Submission_Package_Nature_Energy_Manuscript/SI.tex")
