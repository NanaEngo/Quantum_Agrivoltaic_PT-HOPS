import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# Publication style from source
plt.rcParams.update({
    'font.size': 10, 'font.family': 'serif',
    'axes.labelsize': 11, 'axes.titlesize': 11,
    'xtick.labelsize': 9, 'ytick.labelsize': 9,
    'legend.fontsize': 8, 'figure.dpi': 300,
    'savefig.dpi': 300, 'savefig.bbox': 'tight',
    'axes.linewidth': 0.8, 'lines.linewidth': 1.2,
})

C = {'blue': '#2166AC', 'red': '#B2182B', 'green': '#1B7837',
     'orange': '#E08214', 'purple': '#7B3294', 'cyan': '#00798C',
     'gold': '#D4A017', 'grey': '#666666'}

def generate_figure_7():
    fig = plt.figure(figsize=(12, 4))
    gs = gridspec.GridSpec(1, 3, wspace=0.35)
    
    # (a) Composite spectral density
    ax0 = plt.subplot(gs[0])
    omega = np.linspace(0, 1500, 1000)
    lam, gam = 35, 50
    J_DL = 2 * lam * gam * omega / (omega**2 + gam**2)
    ax0.fill_between(omega, J_DL, alpha=0.3, color=C['blue'], label='Drude–Lorentz')
    ax0.plot(omega, J_DL, color=C['blue'], lw=1.2)
    
    modes = [(150, 0.05), (200, 0.02), (575, 0.01), (1185, 0.005)]
    for w0, S in modes:
        gv = 10
        J_v = S * w0**2 * gv * omega / ((omega**2 - w0**2)**2 + (gv * omega)**2) * 500
        ax0.fill_between(omega, J_v, alpha=0.2, color=C['orange'])
        ax0.plot(omega, J_v, color=C['orange'], lw=1.0)
        ax0.annotate(f'{w0}', xy=(w0, J_v.max()*1.1), fontsize=8, ha='center', color=C['orange'])
        
    ax0.set_xlabel('Frequency (cm$^{-1}$)')
    ax0.set_ylabel('$J(\\omega)$ (a.u.)')
    ax0.set_title('(a) Spectral density', fontweight='bold', pad=10)
    ax0.legend(frameon=False, loc='upper right')
    ax0.set_xlim(0, 1500)
    ax0.set_ylim(0, 450)

    # (b) Bath correlation function
    ax1 = plt.subplot(gs[1])
    t_c = np.linspace(0, 550, 500)
    C_re = np.exp(-t_c / 120) * np.cos(2 * np.pi * t_c / 100) 
    C_im = np.exp(-t_c / 120) * np.sin(2 * np.pi * t_c / 100) * 0.5
    ax1.plot(t_c, C_re, color=C['blue'], lw=1.6, label='Re[$C(t)$]')
    ax1.plot(t_c, C_im, '--', color=C['red'], lw=1.4, label='Im[$C(t)$]')
    ax1.axhline(y=0, ls='-', color='k', alpha=0.2, lw=0.5)
    ax1.set_xlabel('Time (fs)')
    ax1.set_ylabel('$C(t)$ (a.u.)')
    ax1.set_title('(b) Bath correlation', fontweight='bold', pad=10)
    ax1.legend(frameon=False)
    ax1.set_xlim(0, 500)

    # (c) Spectral Overlap
    ax2 = plt.subplot(gs[2])
    wl = np.linspace(400, 950, 500)
    opv_t = 0.4 + 0.4 * np.exp(-((wl-580)/120)**2) + 0.2 * np.exp(-((wl-750)/20)**2) + 0.2 * np.exp(-((wl-825)/15)**2)
    psu_r = 0.4 * np.exp(-((wl-680)/40)**2) + 0.9 * np.exp(-((wl-750)/25)**2) + 0.75 * np.exp(-((wl-825)/12)**2)
    
    ax2.fill_between(wl, opv_t, alpha=0.25, color=C['green'], label='OPV Trans.')
    ax2.plot(wl, opv_t, color=C['green'], lw=1.4)
    ax2.fill_between(wl, psu_r, alpha=0.25, color=C['red'], label='PSU Response')
    ax2.plot(wl, psu_r, color=C['red'], lw=1.4)
    
    for wc in [750, 825]:
        ax2.axvspan(wc-10, wc+10, alpha=0.15, color=C['gold'])
        ax2.axvline(wc, ls=':', color=C['grey'], lw=1.0)
        
    ax2.set_xlabel('Wavelength (nm)')
    ax2.set_ylabel('Normalised Resp.')
    ax2.set_title('(c) Spectral overlap', fontweight='bold', pad=10)
    ax2.legend(frameon=False, loc='upper left', fontsize=7)
    ax2.set_xlim(400, 900)
    ax2.set_ylim(0, 1.2)

    # Use plt.tight_layout with explicit margins to prevent label overlap
    plt.subplots_adjust(top=0.88, bottom=0.18, left=0.08, right=0.95)
    plt.savefig('Graphics/Figure_7_Spectral_Analysis.png', dpi=300)
    print("✓ Figure_7_Spectral_Analysis.png generated in Graphics/")

if __name__ == "__main__":
    generate_figure_7()
