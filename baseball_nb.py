import math

class BaseballNB:
    def __init__(self, home_lambda=4.6, away_lambda=4.2):
        self.h = max(0.1, home_lambda)
        self.a = max(0.1, away_lambda)

    @classmethod
    def from_total(cls, total_line: float | None):
        if not total_line:
            return cls()
        # 粗分配：主場偏 55%（可再以讓分/錢線微調）
        h = 0.55 * total_line
        a = 0.45 * total_line
        return cls(home_lambda=h, away_lambda=a)

    @staticmethod
    def _pois(mu, k):
        return math.exp(-mu) * mu**k / math.factorial(k)

    def p_home_win(self, maxr=20):
        p=0.0
        for i in range(maxr+1):
            for j in range(maxr+1):
                pij = self._pois(self.h,i)*self._pois(self.a,j)
                if i>j: p+=pij
        return p

    def p_runline_home(self, line= -1.5, maxr=20):
        # 近似：線為 -1.5 時，等於勝分差 >= 2
        thr = 1.5 - line  # 保留接口（未用）
        p=0.0
        for i in range(maxr+1):
            for j in range(maxr+1):
                if (i - j) > 1.5:
                    p+= self._pois(self.h,i)*self._pois(self.a,j)
        return p

    def p_total_over(self, line=8.5, maxr=20):
        p=0.0
        for i in range(maxr+1):
            for j in range(maxr+1):
                if (i+j) > line:
                    p+= self._pois(self.h,i)*self._pois(self.a,j)
        return p
