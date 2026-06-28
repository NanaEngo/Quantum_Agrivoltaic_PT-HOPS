import yaml
from pydantic import BaseModel, Field


class SolverConfig(BaseModel):
    hierarchy_depth: int = Field(default=8, ge=1, le=20)
    time_step_fs: float = Field(default=0.2, gt=0.0)
    simulation_duration_fs: float = Field(default=100.0, gt=0.0)
    n_traj: int = Field(default=2, ge=1, le=100)
    sbd_bundles_per_site: int = Field(default=3, ge=1, le=20)


class FmoConfig(BaseModel):
    sites: int = Field(..., ge=1, le=8)
    coupling_reaction_center: float = Field(..., ge=0.0)
    mode_volume_nm3: float = Field(..., gt=0.0)


class FloquetConfig(BaseModel):
    driving_amplitude: float = Field(..., ge=0.0)
    driving_frequency: float = Field(..., ge=0.0)


class SersConfig(BaseModel):
    optomechanical_coupling: float = Field(..., ge=0.0)


class NpomConfig(BaseModel):
    enabled: bool = True


class QuantumSection(BaseModel):
    solver: SolverConfig
    fmo: FmoConfig
    floquet: FloquetConfig
    sers: SersConfig
    npom: NpomConfig


class SimulationSection(BaseModel):
    temperature_k: float = Field(..., gt=0.0)
    solar_flux_threshold: float = Field(..., ge=0.0)


class GreenhouseConfig(BaseModel):
    shading_factor: float = Field(..., ge=0.0, le=1.0)
    soiling_factor: float = Field(default=0.05, ge=0.0, le=1.0)
    crop_coefficient: float = Field(..., ge=0.0)


class MicroclimateSection(BaseModel):
    greenhouse: GreenhouseConfig
    default_temp_c: float = 25.0
    default_rh_pct: float = 60.0
    default_wind_speed_m_s: float = 1.5
    baseline_water_mm: float = 5.0


class CooperativeConfig(BaseModel):
    coop_members: int = Field(..., ge=1)
    capex_subsidy_rate: float = Field(..., ge=0.0, le=1.0)
    area_m2: float = Field(default=500.0, gt=0.0)  # V5: 500 m2 micro-module
    crop_price_per_kg: float = Field(default=4.5, gt=0.0)  # High-value crop price
    yield_kg_per_m2_yr: float = Field(default=8.2, gt=0.0)  # Floriculture yield
    discount_rate: float = Field(default=0.12, gt=0.0)  # Risk-adjusted discount rate
    annual_training_opex_usd: float = Field(default=1200.0, ge=0.0)  # Extension services
    annual_cleaning_opex_usd: float = Field(default=800.0, ge=0.0)  # OPV panel cleaning


class LcaSection(BaseModel):
    cooperative: CooperativeConfig
    carbon: dict
    pv_efficiency: float = 0.15
    pv_fill_factor: float = 0.8
    reference_biomass_kg: float = 12.0
    default_capex: float = 25000.0
    capex_std: float = 2500.0
    default_annual_revenue: float = 6000.0
    revenue_std: float = 600.0
    default_annual_opex: float = 2000.0
    panel_cleaning_annual_cost: float = 500.0
    scenario_b_yield_factor: float = 0.8
    scenario_b_water_factor: float = 0.9
    scenario_b_power_factor: float = 1.1
    scenario_b_biomass_kg: float = 10.0
    scenario_c_yield_factor: float = 0.7
    scenario_c_water_liters: float = 0.0
    scenario_c_power_kwh: float = 0.0
    scenario_c_biomass_kg: float = 12.0


class QkdConfig(BaseModel):
    channel_type: str = Field(default="fiber")  # V5: "fiber" | "free_space"
    channel_noise_rate: float = Field(..., ge=0.0, le=1.0)
    security_threshold: float = Field(default=0.11, gt=0.0)  # Shor-Preskill limit
    key_length_bits: int = Field(..., ge=1)


class SecuritySection(BaseModel):
    qkd: QkdConfig


class DigitalTwinConfig(BaseModel):
    """
    V6: Agrivoltaic Digital Twin orchestration parameters (Axe 1).

    Defines the data-fusion refresh cadence, grid synchronisation flags,
    and cross-domain feedback thresholds that unify quantum metabolic
    sensing, FAO-56 microclimate, IoT sensor telemetry, and OPV energy
    flux under a single Digital Twin control loop.
    """

    update_interval_seconds: int = Field(default=60, ge=1)
    sync_opv_grid: bool = Field(default=True)
    fusion_enabled: bool = Field(default=True)
    urgency_high_threshold: float = Field(default=2.0, gt=0.0)
    urgency_medium_threshold: float = Field(default=1.0, gt=0.0)
    security_gate_qkd: bool = Field(default=True)


class PhysicsConfig(BaseModel):
    """V5: Environmental degradation and sentinel-sensing physics parameters."""

    soiling_decay_rate_per_day: float = Field(default=0.005, ge=0.0)  # OPV attenuation
    sensing_sentinel_ratio: float = Field(default=0.01, ge=0.0, le=1.0)  # 1% canopy sentinels
    npom_optimal_mode_volume_nm3: float = Field(default=1.2, gt=0.0)


class QuantumSignalConfig(BaseModel):
    """
    V6: Quantum Machine Learning / hybrid signal processing (Axe 6).

    Controls the Quantum Kernel and Tensor Network (MPS) parameters for
    denoising and early-stress detection from noisy SERS/CQD telemetry.
    """

    kernel_gamma: float = Field(default=0.5, gt=0.0)  # RBF kernel width
    kernel_regularization: float = Field(default=1e-3, ge=0.0)  # Tikhonov regularisation
    mps_chi: int = Field(default=16, ge=2, le=256)  # MPS bond dimension
    mps_sweeps: int = Field(default=5, ge=1, le=100)  # DMRG sweeps (reserved)
    stress_anomaly_zscore: float = Field(default=2.0, gt=0.0)  # Z-score threshold for alarm
    noise_sigma_fraction: float = Field(default=0.05, ge=0.0, le=1.0)  # Injected noise fraction


class OutputConfig(BaseModel):
    dynamics_h5: str = Field(default="data/converged/production_dynamics.h5")
    graphics_dir: str = Field(default="Graphics")


class ConfigModel(BaseModel):
    simulation: SimulationSection
    quantum: QuantumSection
    microclimate: MicroclimateSection
    lca: LcaSection
    security: SecuritySection
    digital_twin: DigitalTwinConfig = Field(default_factory=DigitalTwinConfig)  # V6: Digital Twin
    physics: PhysicsConfig = Field(default_factory=PhysicsConfig)  # V5: environmental physics
    quantum_signal: QuantumSignalConfig = Field(default_factory=QuantumSignalConfig)  # V6: QML
    output: OutputConfig = Field(default_factory=OutputConfig)


def load_config(path: str) -> ConfigModel:
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return ConfigModel(**data)
