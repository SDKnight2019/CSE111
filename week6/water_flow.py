def water_column_height(tower_height, tank_height):
    rho = 998.2
    pressure_loss = (-0.04 * rho * fluid_velocity ** 2 * quantity_fittings) / 2000
    return pressure_loss

def reynolds_number(hydraulic_diameter, fluid_velocity):
    rho = 998.2
    mu = 0.0010016
    reynolds = (rho * hydraulic_diameter * fluid_velocity) / mu
    return reynolds

def pressure_loss_from_pipe_reduction(larger_diameter, fluid_velocity, reynolds_number, smaller_diameter):
    rho = 998.2
    k = 0.1 + (50 / reynolds_number) * ((larger_diameter / smaller_diameter) ** 4 - 1)
    pressure_loss = -k * rho * fluid_velocity ** 2 / 2000
    return pressure_loss

def pressure_kpa_to_psi(kpa):
    psi = kpa * 0.145038
    return psi

