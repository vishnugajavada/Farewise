from __future__ import annotations


def advise(current_fare: float, predicted_wait_fare: float, rise_probability: float, minimum_saving: float = 500, max_risk: float = .35, wait_days: int = 1) -> dict[str, object]:
    saving=current_fare-predicted_wait_fare
    action=(f"WAIT {wait_days} DAYS" if saving>=minimum_saving and rise_probability<=max_risk else "BOOK NOW" if saving<0 or rise_probability>max_risk else "EITHER IS FINE")
    return {"action":action,"wait_days":wait_days if action.startswith("WAIT") else 0,"expected_saving_inr":round(saving,2),"expected_saving_percent":round(100*saving/current_fare,2) if current_fare else 0.0,"rise_probability":float(rise_probability)}

def choose_wait(current_fare: float, future_means: dict[int,float], rise_probabilities: dict[int,float], minimum_saving: float, max_risk: float) -> dict[str,object]:
    options=[advise(current_fare,fare,rise_probabilities[days],minimum_saving,max_risk,days) for days,fare in future_means.items()]
    if not options:return advise(current_fare,current_fare,0,minimum_saving,max_risk)
    return max(options,key=lambda result: (result["expected_saving_inr"] if result["action"].startswith("WAIT") else 0,-result["wait_days"]))
