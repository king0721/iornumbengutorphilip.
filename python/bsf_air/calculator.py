def waste_conversion(waste_input: float) -> tuple[float, float]:
    """Estimate larvae and frass output from waste input (kg)."""
    larvae_conversion_rate = 0.20
    frass_rate = 0.50
    larvae_output = waste_input * larvae_conversion_rate
    frass_output = waste_input * frass_rate
    return larvae_output, frass_output


def methane_reduction(waste_kg: float) -> float:
    """Estimate methane avoided (kg CO2e-equivalent approximation)."""
    methane_factor = 0.06
    avoided_methane = waste_kg * methane_factor
    return avoided_methane
