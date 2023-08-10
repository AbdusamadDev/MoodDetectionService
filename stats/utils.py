"""Utilization function `percentage()` to get the percentage of DRF Queryset"""


def percentage(data: dict, user=None) -> dict:
    total = sum([value for value in data.values()])
    data = {param: (data[param] / total) * 100 for param in data}
    data.update({"total": total, "user_id": user})
    return data
