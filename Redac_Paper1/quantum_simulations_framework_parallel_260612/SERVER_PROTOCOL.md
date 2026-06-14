# SERVER PROTOCOL — PenavoraServer (100.73.21.40)

## 1. Connexion

### Prérequis
- Tailscale actif sur le laptop
- `sshpass` installé (ou clé SSH configurée)

### Connexion
```bash
ssh nanaengo@100.73.21.40
```

### Transfert du code
```bash
# Depuis le laptop (code canonique)
tar czf /tmp/quantum_sim_fw.tar.gz \
  /quantum_simulations_framework_parallel_260612/
scp /tmp/quantum_sim_fw.tar.gz nanaengo@100.73.21.40:~/
ssh nanaengo@100.73.21.40 "cd ~/ && tar xzf quantum_sim_fw.tar.gz"
```

---

## 2. Environnement Conda

```bash
# L'environnement s'appelle MesoHOP-sim
~/miniforge3/envs/MesoHOP-sim/bin/python script.py

# Lister les packages
~/miniforge3/envs/MesoHOP-sim/bin/pip list
```

### Création (déjà fait)
```bash
~/miniforge3/bin/mamba create -n MesoHOP-sim python=3.12 \
  numpy scipy numba matplotlib joblib pyyaml pandas tqdm psutil
~/miniforge3/envs/MesoHOP-sim/bin/pip install -e ~/mesohops
```

---

## 3. Simulation de production

### Lancement
```bash
cd ~/quantum_simulations_framework_parallel_260612
nohup ~/miniforge3/envs/MesoHOP-sim/bin/python \
  reproducibility/main.py --parallel --skip-audit \
  > ~/production_run.log 2>&1 &
```

### Monitorer
```bash
tail -f ~/production_run.log           # Temps réel
grep -E "batch|ERROR|WARNING" ~/production_run.log   # Résumé
wc -l ~/production_run.log             # Progression approximative
```

### Arrêt
```bash
pkill -f "main.py --parallel"
```

---

## 4. Figure 2 — Temperature Sweep

```bash
cd ~/quantum_simulations_framework_parallel_260612
nohup ~/miniforge3/envs/MesoHOP-sim/bin/python \
  reproducibility/run_temp_sweep_only.py \
  > ~/sweep_cluster.log 2>&1 &
```

---

## 5. Matériel

| Ressource | Disponible | Notes |
|-----------|-----------|-------|
| CPU | 48 cœurs | AMD64 |
| RAM | 125 GB (119 GB dispo) | |
| GPU | 1× NVIDIA | **Driver mismatch** (NVML v580.159 vs module) |
| Stockage | ~200 GB dispo | |

### GPU — Fix du driver
```bash
# Vérifier la version NVIDIA installée
cat /proc/driver/nvidia/version
dpkg -l | grep nvidia-driver

# Réinstaller (choisir la version appropriée)
sudo apt-get install --reinstall nvidia-driver-580
# ou
sudo apt-get install --reinstall nvidia-driver-585
sudo reboot
```

---

## 6. Récupération des résultats

```bash
# Depuis le laptop
scp nanaengo@100.73.21.40:~/quantum_simulations_framework_parallel_260612/data/converged/*.csv \
  ./data/converged/
scp nanaengo@100.73.21.40:~/quantum_simulations_framework_parallel_260612/reproducibility/results/*.csv \
  ./reproducibility/results/
```

---

## 7. Commandes rapides

| Action | Commande |
|--------|----------|
| Vérifier RAM | `free -h` |
| Vérifier CPU | `htop` ou `nproc` |
| Vérifier GPU | `nvidia-smi` (si driver fixé) |
| Vérifier processes | `ps aux \| grep python` |
| Vérifier disque | `df -h ~/` |
| Vérifier logs | `tail -100 ~/production_run.log` |
