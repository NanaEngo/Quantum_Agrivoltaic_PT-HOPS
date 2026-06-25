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
    channel_noise_rate: float = Field(..., ge=0.0, le=1.0)
    key_length_bits: int = Field(..., ge=1)


class SecuritySection(BaseModel):
    qkd: QkdConfig


class OutputConfig(BaseModel):
    dynamics_h5: str = Field(default="data/converged/production_dynamics.h5")
    graphics_dir: str = Field(default="Graphics")


class ConfigModel(BaseModel):
    simulation: SimulationSection
    quantum: QuantumSection
    microclimate: MicroclimateSection
    lca: LcaSection
    security: SecuritySection
    output: OutputConfig = Field(default_factory=OutputConfig)


def load_config(path: str) -> ConfigModel:
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return ConfigModel(**data)
