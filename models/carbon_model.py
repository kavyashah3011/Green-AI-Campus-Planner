def carbon_reduction_kgs(energy_kwh):
    EMISSION_FACTOR = 0.82  # kg CO2 per kWh (India avg)
    return round(energy_kwh * EMISSION_FACTOR, 2)
