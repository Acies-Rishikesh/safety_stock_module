# from backend.safety_stock.rule_based_safety_stock import calculate_rule_based_safety_stock
from ..backend.modules.rule_based import calculate_rule_based_safety_stock

# Sample service level mapping (simulate UI choices)
service_level_dict = {
    ('SKU001', 'DC'): 0.97,
    ('SKU002',): 0.90,
    ('DC',): 0.92,
    ('South',): 0.93,
    ('GLOBAL',): 0.95
}

result_df = calculate_rule_based_safety_stock(cleaned_actual_df, service_level_dict)
print(result_df.head())
