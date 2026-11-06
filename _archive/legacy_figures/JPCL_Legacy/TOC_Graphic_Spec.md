# Table of Contents Graphic Specification

**Journal:** Journal of Physical Chemistry Letters  
**Required Size:** 1000 × 500 pixels (width × height)  
**Format:** PNG or TIFF  
**File Name:** `TOC_Graphic.png`

---

## Concept: Quantum-Coherent Spectral Engineering

### Visual Elements (Left to Right)

#### **Left Panel: Broadband Illumination (Baseline)**
- White light spectrum (rainbow gradient)
- FMO complex (7 green spheres connected by lines)
- Wavy arrows showing rapid decoherence (red X marks)
- Label: "Broadband: τc ≈ 300 fs"

#### **Center Panel: Spectral Filter**
- OPV semi-transparent panel (blue-tinted glass)
- Transmission spectrum showing two peaks at 750 nm and 820 nm
- Arrows filtering through the panel
- Label: "Spectral Filter: 750, 820 nm"

#### **Right Panel: Filtered Illumination (Enhanced)**
- Dual-color light (green + near-IR)
- FMO complex with glowing connections (quantum coherence)
- Smooth arrows showing sustained energy transfer
- Label: "Filtered: τc ≈ 500 fs (+50%)"

### Color Scheme
- **Broadband light:** White/rainbow gradient
- **Filtered light:** Green (#4CAF50) + Near-IR (#9C27B0)
- **FMO complex:** Emerald green (#2E7D32)
- **Coherence pathways:** Glowing cyan (#00BCD4)
- **Decoherence:** Red (#F44336)
- **Background:** White or light gray

### Text Elements
- **Title (top):** "Quantum-Coherent Spectral Engineering"
- **Bottom labels:** 
  - Left: "Decoherence"
  - Center: "Vibronic Resonance"
  - Right: "Coherence Enhancement"

### Style Guidelines
- Clean, minimalist design
- No clutter or excessive detail
- High contrast for small thumbnail viewing
- Sans-serif fonts (Arial or Helvetica)
- Professional scientific illustration style

---

## Prompt for AI Image Generation

```
Scientific illustration, horizontal layout 1000x500 pixels, three panels 
showing quantum coherence in photosynthetic complexes:

LEFT PANEL: White rainbow light shining on molecular structure (7 connected 
spheres), red X marks showing decoherence, label "300 fs"

CENTER PANEL: Semi-transparent blue filter with two transmission peaks, 
wavelengths 750nm and 820nm labeled

RIGHT PANEL: Green and purple light shining on same molecular structure, 
glowing cyan connections between spheres showing quantum coherence, 
label "500 fs"

Clean minimalist style, white background, professional scientific 
illustration, high contrast, sans-serif text labels
```

---

## Alternative: Manual Creation with Python/Matplotlib

```python
import matplotlib.pyplot as plt
import numpy as np

fig, axes = plt.subplots(1, 3, figsize=(10, 5), dpi=100)

# Left: Broadband
axes[0].imshow(np.linspace(0, 1, 100).reshape(100, 1), aspect='auto', 
               cmap='rainbow')
axes[0].text(0.5, 0.5, 'Broadband\nτc ≈ 300 fs', ha='center', va='center',
             fontsize=12, fontweight='bold')
axes[0].set_title('Baseline')

# Center: Filter
wavelengths = np.linspace(400, 900, 500)
transmission = np.exp(-(wavelengths-750)**2/2/30**2) + \
               np.exp(-(wavelengths-820)**2/2/30**2)
axes[1].fill_between(wavelengths, 0, transmission, color='blue', alpha=0.5)
axes[1].text(0.5, 0.5, 'Spectral Filter\n750, 820 nm', ha='center', 
             va='center', fontsize=12, fontweight='bold')
axes[1].set_title('Engineering')

# Right: Enhanced
axes[2].imshow(np.linspace(0, 1, 100).reshape(100, 1), 
               aspect='auto', cmap='Greens')
axes[2].text(0.5, 0.5, 'Filtered\nτc ≈ 500 fs (+50%)', ha='center', 
             va='center', fontsize=12, fontweight='bold')
axes[2].set_title('Enhanced Coherence')

for ax in axes:
    ax.axis('off')

plt.tight_layout()
plt.savefig('TOC_Graphic.png', dpi=100, bbox_inches='tight')
```

---

## Checklist

- [ ] Size: 1000 × 500 pixels
- [ ] Format: PNG (transparent background OK)
- [ ] File size: < 5 MB
- [ ] Text readable at thumbnail size
- [ ] Colors match manuscript figures
- [ ] No copyright violations
- [ ] Saved as `TOC_Graphic.png` in JPCL folder

---

**Last Updated:** March 22, 2026  
**Status:** Ready for Creation
