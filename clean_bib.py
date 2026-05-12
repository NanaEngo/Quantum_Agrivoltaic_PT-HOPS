import re
import os

def clean_bib(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by @ followed by entry type
    # entries = re.split(r'\n(?=@)', content)
    # A more robust split that handles entries not separated by newlines
    entries_raw = re.findall(r'@\w+\s*\{[^@]*\}', content, re.DOTALL)
    
    header_match = re.match(r'^[^@]*', content)
    header = header_match.group(0).strip() if header_match else ""

    cleaned_entries = []
    doi_map = {}
    title_map = {}
    seen_keys = set()
    
    # Better field parser
    def get_fields_robust(entry_text):
        # Extract the type and key
        header_match = re.match(r'@(\w+)\s*\{\s*([^,]+),', entry_text)
        if not header_match: return None, None, {}
        e_type = header_match.group(1)
        e_key = header_match.group(2)
        
        body = entry_text[header_match.end():].rstrip('}')
        
        fields = {}
        # This regex matches key = {value} or key = "value"
        # It handles nested braces roughly by looking for balanced pairs (simplified)
        field_matches = re.finditer(r'(\w+)\s*=\s*(.*)', body)
        
        # We need a better way to split fields because they can contain commas
        # Let's split by key = 
        field_parts = re.split(r'(\w+)\s*=\s*', body)
        # field_parts[0] is empty or whitespace
        for i in range(1, len(field_parts), 2):
            key = field_parts[i].lower().strip()
            val_raw = field_parts[i+1].strip()
            # Trim trailing comma and whitespace
            if val_raw.endswith(','):
                val_raw = val_raw[:-1].strip()
            
            # Remove wrapping braces or quotes
            if (val_raw.startswith('{') and val_raw.endswith('}')) or (val_raw.startswith('"') and val_raw.endswith('"')):
                val = val_raw[1:-1]
            else:
                val = val_raw
            fields[key] = val
            
        return e_type, e_key, fields

    def get_author_year(fields, entry_key):
        author = fields.get('author', '')
        year = fields.get('year', '')
        
        # Fallback to current key if author or year missing
        if not author or not year:
            return entry_key

        # Extract last name of first author
        # Handle formats: "Last, First" or "First Last"
        first_author_full = author.split(' and ')[0].strip()
        if ',' in first_author_full:
            last_name = first_author_full.split(',')[0].strip()
        else:
            last_name = first_author_full.split(' ')[-1].strip()
        
        # Clean last name
        last_name = re.sub(r'[^a-zA-Z]', '', last_name)
        if not last_name: last_name = "Author"
        
        return f"{last_name}{year}"

    final_entries = []
    
    for entry_text in entries_raw:
        e_type, e_key, fields = get_fields_robust(entry_text)
        if not e_type: continue
        if e_type.lower() == 'comment': continue
        
        doi = fields.get('doi', '').lower().strip()
        # Clean DOI: some might have https://doi.org/ prefix
        if 'doi.org/' in doi:
            doi = doi.split('doi.org/')[-1]
            
        title_norm = re.sub(r'[^a-z0-9]', '', fields.get('title', '').lower().strip())
        
        # Deduplication
        if doi and doi in doi_map:
            print(f"Skipping duplicate DOI: {doi} (Key: {e_key})")
            continue
        if title_norm and title_norm in title_map:
            if fields.get('year') == title_map[title_norm].get('year'):
                print(f"Skipping duplicate Title: {fields.get('title')} (Key: {e_key})")
                continue
        
        if doi: doi_map[doi] = fields
        if title_norm: title_map[title_norm] = fields

        # Generate consistent key
        new_key = get_author_year(fields, e_key)
        base_key = new_key
        suffix_idx = 0
        suffixes = "abcdefghijklmnopqrstuvwxyz"
        while new_key in seen_keys:
            if suffix_idx < len(suffixes):
                new_key = base_key + suffixes[suffix_idx]
                suffix_idx += 1
            else:
                new_key = base_key + str(suffix_idx)
                suffix_idx += 1
        seen_keys.add(new_key)
        
        # Reconstruct entry
        reconstructed = f"@{e_type}{{{new_key},\n"
        field_order = ['author', 'title', 'journal', 'booktitle', 'year', 'volume', 'number', 'pages', 'doi', 'publisher', 'issn', 'month']
        
        # Add fields in order
        added_fields = set()
        for f_name in field_order:
            if f_name in fields:
                val = fields[f_name]
                if f_name == 'title':
                    # Ensure double braces for title to preserve capitalization
                    val = f"{{{val}}}"
                reconstructed += f"  {f_name:<10} = {{{val}}},\n"
                added_fields.add(f_name)
        
        # Add remaining fields
        for f_name, val in fields.items():
            if f_name not in added_fields:
                reconstructed += f"  {f_name:<10} = {{{val}}},\n"
        
        reconstructed = reconstructed.rstrip(',\n') + "\n}"
        final_entries.append(reconstructed)

    output_content = header + "\n\n" + "\n\n".join(final_entries)
    
    # Write to a temp file first
    with open(file_path + '.new', 'w', encoding='utf-8') as f:
        f.write(output_content)
    
    print(f"Processed {len(entries_raw)} entries. Saved to {file_path}.new")

clean_bib('/media/taamangtchu/MYDATA/Github/Quantum_Agrivoltaic_PT-HOPS/Redac_Paper1/Theory_Journals_main/JPCL/references.bib')
