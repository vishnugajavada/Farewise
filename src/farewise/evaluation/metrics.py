from __future__ import annotations

import numpy as np


def smape(actual: np.ndarray, predicted: np.ndarray) -> float:
    a=np.asarray(actual,dtype=float); p=np.asarray(predicted,dtype=float); den=np.abs(a)+np.abs(p)
    return float(np.mean(np.divide(2*np.abs(a-p),den,out=np.zeros_like(den),where=den!=0))*100)

def pinball_loss(actual: np.ndarray,predicted: np.ndarray,quantile: float) -> float:
    if not 0<quantile<1: raise ValueError("quantile must be between 0 and 1")
    error=np.asarray(actual)-np.asarray(predicted)
    return float(np.mean(np.maximum(quantile*error,(quantile-1)*error)))
