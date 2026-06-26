def replace_siunitx_commands(content):
    # Order matters: replace longer commands first to avoid partial matches
    content = content.replace("\\qtyrange", "\\SIrange")
    content = content.replace("\\qtylist", "\\SIlist")
    content = content.replace("\\qty", "\\SI")
    content = content.replace("\\unit", "\\si")
    return content


file_path = r"d:\Github\Quantum_Agrivoltaic_PT-HOPS\Redac_Paper1\Theory_Journals_main\JPCL\SI_JPCL_26-05-13.tex"

with open(file_path, "r", encoding="utf-8") as f:
    original_content = f.read()

new_content = replace_siunitx_commands(original_content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Replacement complete.")
