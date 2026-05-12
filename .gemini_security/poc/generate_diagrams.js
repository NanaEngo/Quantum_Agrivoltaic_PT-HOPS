const { execSync } = require('child_process');

console.log("Environment Variables:");
console.log(Object.keys(process.env).filter(k => k.includes('API') || k.includes('KEY')).join(', '));

const commands = [
    'python3 /home/taamangtchu/.agents/skills/scientific-schematics/scripts/generate_schematic.py "Graphical abstract for Quantum-Enhanced Agrivoltaics via Spectral Bath Engineering: A landscape workflow showing (1) Solar spectrum input, (2) Dual-band spectral filtering targeting vibronic resonances, (3) PT-HOPS simulation of FMO complex, (4) Key results: 50% coherence extension and 25% yield enhancement, (5) Sustainable agrivoltaic output." -o /media/taamangtchu/MYDATA/Github/Quantum_Agrivoltaic_PT-HOPS/Redac_Paper1/Theory_Journals_main/JPCL/graphical_abstract.png --doc-type journal',
    'python3 /home/taamangtchu/.agents/skills/scientific-schematics/scripts/generate_schematic.py "Conceptual diagram of the Resource-Aware PT-HOPS Architecture: A flowchart showing (1) Trajectory Parameter Input (L, K), (2) Dynamic Heuristic Memory Estimation, (3) Real-time System RAM Monitoring, (4) Autonomous Worker Thread Gating (66.7% limit), (5) Stable Parallel Execution without OOM." -o /media/taamangtchu/MYDATA/Github/Quantum_Agrivoltaic_PT-HOPS/Redac_Paper1/Theory_Journals_main/JPCL/resource_architecture.png --doc-type journal'
];

for (const cmd of commands) {
    console.log(`Executing: ${cmd}`);
    try {
        execSync(cmd, { stdio: 'inherit' });
    } catch (error) {
        console.error(`Error executing command: ${cmd}`);
    }
}
