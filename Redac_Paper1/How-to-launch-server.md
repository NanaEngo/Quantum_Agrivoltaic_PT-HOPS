# Summary of the 5 bugs found and fixed
  
  Bug 1 — No working directory anchor (critical — would crash immediately)
  
  MAIN_SCRIPT was a bare relative path. If you ran the script from $HOME or any other directory, Python would fail with No such file or directory. Fixed by anchoring everything to SCRIPT_DIR using $(dirname "${BASH_SOURCE[0]}").
  
  Bug 2 — Log file written to random CWD (silent data loss)
  
  LOG_FILE="reproducibility_cluster.log" would land wherever you launched the script from, not inside the framework. Fixed to $FRAMEWORK_DIR/reproducibility/logs/cluster_gpu_<timestamp>.log.
  
  Bug 3 — --config never forwarded (wrong config silently used)
  
  The script had no way to pass --config config/server_parameters.yaml. Fixed by forwarding $* to main.py, so you can now call:
  
  bash run_cluster_gpu.sh --config config/server_parameters.yaml
  
  Without --config, main.py still auto-selects parameters.yaml (L=8, production) which is correct.
  
  Bug 4 — XLA_PYTHON_CLIENT_MEM_FRACTION=0.33 contradicted parallel_config.yaml
  
  parallel_config.yaml sets gpu_memory_fraction: 0.9 but the script silently capped JAX at 33% of GPU memory. Fixed to 0.90 to match.
  
  Bug 5 — PID not persisted (no clean kill path)
  
  The PID was only printed to the terminal. If the SSH session closed, the job was untrackable. Fixed by writing $PID to cluster_gpu.pid, with a printed kill command: kill $(cat $PID_FILE).



# Running calculation

🚀 Launching /home/penavora/quantum_simulations_framework_parallel_260511/reproducibility/main.py in background...
✅ Job submitted (PID: 828473)
📂 Log file : /home/penavora/quantum_simulations_framework_parallel_260511/reproducibility/logs/cluster_gpu_20260511_102422.log
📄 PID file : /home/penavora/quantum_simulations_framework_parallel_260511/reproducibility/logs/cluster_gpu.pid
📊 Monitor  : tail -f /home/penavora/quantum_simulations_framework_parallel_260511/reproducibility/logs/cluster_gpu_20260511_102422.log
🛑 Kill job : kill $(cat /home/penavora/quantum_simulations_framework_parallel_260511/reproducibility/logs/cluster_gpu.pid)


# Server characteristics

System:
  Kernel: 6.8.0-107-generic arch: x86_64 bits: 64 compiler: gcc v: 13.3.0
  Console: pty pts/0 Distro: Ubuntu 24.04.4 LTS (Noble Numbat)
Machine:
  Type: Desktop System: LENOVO product: 30BBS2YC00 v: ThinkStation P720
    serial: <superuser required>
  Mobo: LENOVO model: 1037 v: SDK0Q40104 WIN 3305666836707 serial: <superuser required>
    UEFI: LENOVO v: S04KT73A date: 07/01/2024
CPU:
  Info: 2x 12-core model: Intel Xeon Gold 6136 bits: 64 type: MT MCP SMP arch: Skylake rev: 4
    cache: L1: 2x 768 KiB (1.5 MiB) L2: 2x 12 MiB (24 MiB) L3: 2x 24.8 MiB (49.5 MiB)
  Speed (MHz): avg: 1200 min/max: 1200/3700 cores: 1: 1200 2: 1200 3: 1200 4: 1200 5: 1200
    6: 1200 7: 1200 8: 1200 9: 1200 10: 1200 11: 1200 12: 1200 13: 1200 14: 1200 15: 1200 16: 1200
    17: 1200 18: 1200 19: 1200 20: 1200 21: 1200 22: 1200 23: 1200 24: 1200 25: 1200 26: 1200
    27: 1200 28: 1200 29: 1200 30: 1200 31: 1200 32: 1200 33: 1200 34: 1200 35: 1200 36: 1200
    37: 1200 38: 1200 39: 1200 40: 1200 41: 1200 42: 1200 43: 1200 44: 1200 45: 1200 46: 1200
    47: 1200 48: 1200 bogomips: 288000
  Flags: avx avx2 ht lm nx pae sse sse2 sse3 sse4_1 sse4_2 ssse3 vmx
Graphics:
  Device-1: NVIDIA GA104GL [RTX A4000] driver: nvidia v: 580.126.09 arch: Ampere bus-ID: 3b:00.0
  Display: server: X.org v: 1.21.1.11 driver: N/A tty: 153x54
  API: EGL v: 1.5 drivers: nvidia,swrast platforms: active: surfaceless,device
    inactive: gbm,wayland,x11,device-1
  API: OpenGL v: 4.6.0 compat-v: 4.5 vendor: mesa v: 25.2.8-0ubuntu0.24.04.1
    note: console (EGL sourced) renderer: NVIDIA RTX A4000/PCIe/SSE2, llvmpipe (LLVM 20.1.2 256
    bits)
Audio:
  Device-1: Intel vendor: Lenovo driver: snd_hda_intel v: kernel bus-ID: 00:1f.3
  Device-2: NVIDIA GA104 High Definition Audio driver: snd_hda_intel v: kernel bus-ID: 3b:00.1
  API: ALSA v: k6.8.0-107-generic status: kernel-api
Network:
  Device-1: Intel Ethernet I219-LM vendor: Lenovo driver: e1000e v: kernel port: N/A
    bus-ID: 00:1f.6
  IF: eno2 state: up speed: 1000 Mbps duplex: full mac: <filter>
  Device-2: Intel I210 Gigabit Network vendor: Lenovo driver: igb v: kernel port: 2000
    bus-ID: 04:00.0
  IF: eno1 state: down mac: <filter>
  IF-ID-1: br-f0b7d1ecd45c state: down mac: <filter>
  IF-ID-2: docker0 state: down mac: <filter>
  IF-ID-3: tailscale0 state: unknown speed: -1 duplex: full mac: N/A
Drives:
  Local Storage: total: 3.64 TiB used: 732.12 GiB (19.6%)
  ID-1: /dev/nvme0n1 vendor: Samsung model: SSD 980 PRO 2TB size: 1.82 TiB temp: 26.9 C
  ID-2: /dev/sda vendor: Hitachi model: HUA722020ALA330 45W6276 59Y1813IBM size: 1.82 TiB
Partition:
  ID-1: / size: 195.8 GiB used: 28.53 GiB (14.6%) fs: ext4 dev: /dev/nvme0n1p2
  ID-2: /boot/efi size: 1.05 GiB used: 6.1 MiB (0.6%) fs: vfat dev: /dev/nvme0n1p1
  ID-3: /home size: 491.08 GiB used: 302.15 GiB (61.5%) fs: ext4 dev: /dev/nvme0n1p3
  ID-4: /opt size: 245.02 GiB used: 40 KiB (0.0%) fs: ext4 dev: /dev/nvme0n1p5
  ID-5: /var size: 343.44 GiB used: 57.39 GiB (16.7%) fs: ext4 dev: /dev/nvme0n1p4
Swap:
  ID-1: swap-1 type: file size: 8 GiB used: 0 KiB (0.0%) file: /swap.img
  ID-2: swap-2 type: file size: 100 GiB used: 0 KiB (0.0%) file: /mnt/backup/swapfile
Sensors:
  System Temperatures: cpu: 44.0 C pch: 40.0 C mobo: N/A gpu: nvidia temp: 44 C
  Fan Speeds (rpm): N/A
Info:
  Memory: total: 128 GiB available: 125.51 GiB used: 2.89 GiB (2.3%)
  Processes: 540 Uptime: 22d 38m Init: systemd target: graphical (5)
  Packages: 1403 Compilers: gcc: 13.3.0 Shell: Bash v: 5.2.21 inxi: 3.3.34
