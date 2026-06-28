import re

files = [
    "Redac_Paper2/Submission_Package_Nature_Energy_Manuscript/Manuscript_NatureEnergy_26-06-25.tex",
    "Redac_Paper2/Submission_Package_Nature_Energy_Manuscript/SI.tex",
]

keep_case = {
    "QAOA",
    "CQD",
    "CQDs",
    "NPoM",
    "BB84",
    "SERS",
    "QKD",
    "OPV",
    "FMO",
    "PT-HOPS",
    "SBD",
    "IoT",
    "DL",
    "LCA",
    "TEA",
    "AI",
    "QML",
    "ROS",
    "MOF",
    "EMA",
    "SI",
    "FWHM",
    "VQE",
    "HEOM",
    "GPU",
    "NVIDIA",
    "A4000",
    "CPU",
    "OOM",
    "RAM",
    "HOPS",
    "MesoHOPS",
    "QuTiP",
    "PennyLane",
    "SciPy",
    "OpenMM",
    "MDAnalysis",
}


def sentence_case(match):
    prefix = match.group(1)
    title = match.group(2)

    words = title.split(" ")
    if not words:
        return match.group(0)

    new_words = []
    for i, w in enumerate(words):
        clean_w = re.sub(r"[^a-zA-Z0-9-]", "", w)
        if i == 0:
            new_words.append(w)
        elif clean_w in keep_case or any(k in w for k in keep_case):
            new_words.append(w)
        else:
            new_words.append(w.lower())

    new_title = " ".join(new_words)
    if new_title != title:
        print(f"CHANGED: '{title}' -> '{new_title}'")

    return prefix + new_title + "}"


for file in files:
    with open(file, "r") as f:
        content = f.read()

    new_content = re.sub(r"(\\(?:sub)*section\*?\{)([^}]+)\}", sentence_case, content)

    with open(file, "w") as f:
        f.write(new_content)
