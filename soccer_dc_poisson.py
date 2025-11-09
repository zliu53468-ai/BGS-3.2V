import math

class SoccerDCPoisson:
    """
    Double Poisson + Dixon-Coles ρ 調整（簡化版）
    hmu、amu 可由市場（總分線/盤口）或歷史估計傳入
    """
    def __init__(self, home_mu: float = 1.40, away_mu: float = 1.15, rho: float = 0.05, maxg: int = 10):
        self.hmu = max(0.05, home_mu)
        self.amu = max(0.05, away_mu)
        self.rho = rho
        self.maxg = maxg

    @staticmethod
    def _pois(mu, k):
        return math.exp(-mu) * (mu**k) / math.factorial(k)

    def _dc_adj(self, i, j):
        # Dixon-Coles 小比分相關修正（只調整 0/1 低比分）
        if i==0 and j==0: return 1 - self.hmu*self.amu*self.rho
        if i==0 and j==1: return 1 + self.hmu*self.rho
        if i==1 and j==0: return 1 + self.amu*self.rho
        if i==1 and j==1: return 1 - self.rho
        return 1.0

    def pmatrix(self):
        P = [[0.0]*(self.maxg+1) for _ in range(self.maxg+1)]
        for i in range(self.maxg+1):
            for j in range(self.maxg+1):
                P[i][j] = self._pois(self.hmu,i) * self._pois(self.amu,j) * self._dc_adj(i,j)
        # Normalize to avoid drift
        Z = sum(sum(row) for row in P)
        if Z>0:
            for i in range(self.maxg+1):
                for j in range(self.maxg+1):
                    P[i][j] /= Z
        return P

    def prob_moneyline(self):
        P = self.pmatrix()
        ph=0.0; pa=0.0; pd=0.0
        for i in range(self.maxg+1):
            for j in range(self.maxg+1):
                if i>j: ph+=P[i][j]
                elif i<j: pa+=P[i][j]
                else: pd+=P[i][j]
        return ph, pd, pa

    def prob_total_over(self, line: float):
        P = self.pmatrix()
        s=0.0
        for i in range(self.maxg+1):
            for j in range(self.maxg+1):
                if i+j > line: s+=P[i][j]
        return s

    def prob_handicap_home(self, line: float):
        """亞洲讓球（home -line），例如 -0.5/-0.25/-1.0"""
        P = self.pmatrix()
        win=0.0; push=0.0
        for i in range(self.maxg+1):
            for j in range(self.maxg+1):
                diff = i - j + line
                if diff>0: win+=P[i][j]
                elif diff==0: push+=P[i][j]
        return win + 0.5*push  # 退水當 0.5（簡化）
