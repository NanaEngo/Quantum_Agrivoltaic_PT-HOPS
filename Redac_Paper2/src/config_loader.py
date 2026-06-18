import yaml
from pydantic import BaseModel, Field


class SolverConfig(BaseModel):
    hierarchy_depth: int = Field(default=8, ge=1, le=20)
    time_step_fs: float = Field(default=0.5, gt=0.0)


class FmoConfig(BaseModel):
    sites: int = Field(..., ge=1, le=8)
    coupling_reaction_center: float = Field(..., ge=0.0)
    mode_volume_nm3: float = Field(..., gt=0.0)


class FloquetConfig(BaseModel):
    driving_amplitude: float = Field(..., ge=0.0)
    driving_frequency: float = Field(..., ge=0.0)


class SersConfig(BaseModel):
    optomechanical_coupling: float = Field(..., ge=0.0)


class QuantumSection(BaseModel):
    solver: SolverConfig
    fmo: FmoConfig
    floquet: FloquetConfig
    sers: SersConfig


class SimulationSection(BaseModel):
    temperature_k: float = Field(..., gt=0.0)
    solar_flux_threshold: float = Field(..., ge=0.0)


class GreenhouseConfig(BaseModel):
    shading_factor: float = Field(..., ge=0.0, le=1.0)
    crop_coefficient: float = Field(..., ge=0.0)


class MicroclimateSection(BaseModel):
    greenhouse: GreenhouseConfig


class CooperativeConfig(BaseModel):
    coop_members: int = Field(..., ge=1)
    capex_subsidy_rate: float = Field(..., ge=0.0, le=1.0)


class LcaSection(BaseModel):
    cooperative: CooperativeConfig
    carbon: dict


class QkdConfig(BaseModel):
    channel_noise_rate: float = Field(..., ge=0.0, le=1.0)
    key_length_bits: int = Field(..., ge=1)


class SecuritySection(BaseModel):
    qkd: QkdConfig


class ConfigModel(BaseModel):
    simulation: SimulationSection
    quantum: QuantumSection
    microclimate: MicroclimateSection
    lca: LcaSection
    security: SecuritySection


def load_config(path: str) -> ConfigModel:
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return ConfigModel(**data)
