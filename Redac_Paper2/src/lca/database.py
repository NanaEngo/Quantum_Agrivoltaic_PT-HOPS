from ..config_loader import ConfigModel


class AmortizationAnalysis:
    """
    Computes socioeconomic amortization models, return on investment (ROI),
    and cooperative payback periods to evaluate technology accessibility.
    """

    def __init__(self, config: ConfigModel):
        self.config = config
        self.coop_members = config.lca.cooperative.coop_members
        self.subsidy_rate = config.lca.cooperative.capex_subsidy_rate

    def calculate_payback_years(
        self, initial_capex: float, annual_revenue: float, annual_opex: float
    ) -> float:
        """
        Calculates CAPEX payback years accounting for cooperative cost division and subsidies.
        """
        # Apply subsidy and split costs among cooperative members
        net_capex = initial_capex * (1.0 - self.subsidy_rate)
        capex_per_member = net_capex / self.coop_members

        # Calculate net revenue per member
        net_annual_revenue_per_member = (annual_revenue - annual_opex) / self.coop_members

        if net_annual_revenue_per_member <= 0.0:
            return float("inf")

        return float(capex_per_member / net_annual_revenue_per_member)
