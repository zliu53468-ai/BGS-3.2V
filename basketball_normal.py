import math

class BasketballNormal:
    """
    margin ~ N(m_mu, m_sig^2)；total ~ N(t_mu, t_sig^2)
    m_mu 由讓分線近似，t_mu 由大小分線近似；σ 可視聯盟常數
    """
    def __init__(self, margin_mu=0.0, margin_sigma=12.0, total_mu=220.0, total_sigma=15.0):
        self.m_mu = margin_mu
        self.m_sig = margin_sigma
        self.t_mu = total_mu
        self.t_sig = total_sigma

    @staticmethod
    def _phi(x):  # 標準常態 CDF
        return 0.5*(1+math.erf(x/math.sqrt(2)))

    @classmethod
    def from_market(cls, spread_line=None, total_line=None,
                    margin_sigma=12.0, total_sigma=15.0):
        m_mu = -(spread_line or 0.0)   # 主隊讓分 -3.5 → 主隊 margin_mu ≈ +3.5
        t_mu = (total_line or 220.0)
        return cls(margin_mu=m_mu, margin_sigma=margin_sigma,
                   total_mu=t_mu, total_sigma=total_sigma)

    def p_moneyline_home(self):
        return 1 - self._phi((-self.m_mu)/self.m_sig)

    def p_cover_home(self, line: float):
        return 1 - self._phi((line - self.m_mu)/self.m_sig)

    def p_total_over(self, line: float):
        return 1 - self._phi((line - self.t_mu)/self.t_sig)
