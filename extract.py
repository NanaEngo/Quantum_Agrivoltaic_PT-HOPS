import json


def extract():
    found = False
    with open(
        "/home/taamangtchu/.gemini/antigravity/brain/759f2208-f4e8-45d5-8be0-f9652c73afc0/.system_generated/logs/transcript_full.jsonl"
    ) as f:
        for line in f:
            if found:
                break
            try:
                obj = json.loads(line)
                if "tool_calls" in obj:
                    for tc in obj["tool_calls"]:
                        if tc["name"] == "run_command":
                            args = tc.get("args", {})
                            cmd = args.get("CommandLine", "")
                            if (
                                "Figure_SI_NPoM_VolumeScan_n20" in cmd
                                and "PYEOF" in cmd
                                and "ssh -i" in cmd
                            ):
                                parts = cmd.split("PYEOF")
                                if len(parts) >= 3:
                                    # the script is everything between the first PYEOF and the last PYEOF
                                    # But since there's string parsing, let's just use the exact substring
                                    start_idx = cmd.find("import sy")
                                    end_idx = cmd.rfind("PYEOF")
                                    if start_idx != -1 and end_idx != -1:
                                        code = cmd[start_idx:end_idx].strip()
                                        code = code.replace(
                                            "'\"'\"'", "'"
                                        )  # unescape bash single quotes
                                        with open(
                                            "generate_light_figures.py", "w"
                                        ) as out:
                                            out.write(code)
                                        print(
                                            "Script saved to generate_light_figures.py"
                                        )
                                        found = True
                                        break
            except Exception:
                pass


if __name__ == "__main__":
    extract()
