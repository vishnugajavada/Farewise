from __future__ import annotations

from collections.abc import Mapping, Sequence


def solve(prices:Mapping[int,float],next_day_ratios:Mapping[int,Sequence[float]]|Sequence[float])->tuple[int,float]:
    """Backward-induct the expected stopping value over days-left states."""
    if not prices:raise ValueError("prices must not be empty")
    days=sorted(prices); values={days[0]:float(prices[days[0]])}; factors={days[0]:1.0}; actions={days[0]:days[0]}
    for index,day in enumerate(days[1:],1):
        samples=next_day_ratios.get(day,[]) if isinstance(next_day_ratios,Mapping) else next_day_ratios
        if not samples:samples=[1.0]
        expected_ratio=float(sum(samples)/len(samples)); previous=days[index-1]
        continuation=float(prices[day])*expected_ratio*factors[previous]
        if float(prices[day])<=continuation:
            values[day]=float(prices[day]);factors[day]=1.0;actions[day]=day
        else:
            values[day]=continuation;factors[day]=continuation/float(prices[day]);actions[day]=actions[previous]
    start=days[-1];return actions[start],values[start]

def optimal_book_day(prices:dict[int,float])->int:
    """Minimum-price hindsight helper, separate from the forward-facing policy."""
    if not prices:raise ValueError("prices must not be empty")
    return min(prices,key=lambda day:(prices[day],-day))
