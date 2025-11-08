"""
Mission Configuration for Active Debris Removal
IIT Kanpur Research Hackathon 2025
"""

import numpy as np

# ====================
# PHYSICAL CONSTANTS
# ====================
MU_EARTH = 398600.0  # km^3/s^2
R_EARTH = 6371.0  # km
G_ACCEL = 9.81e-3  # km/s^2

# ====================
# CHASER SPACECRAFT
# ====================
CHASER = {
    'mass': 1270.0,  # kg
    'fuel_mass': 870.0,  # kg (optimized for complete mission success)
    'dry_mass': 400.0,  # kg
    'isp': 300.0,  # seconds
    've': 300.0 * 9.81e-3,  # km/s (exhaust velocity)

    # Dimensions (assume 1m cube)
    'dimensions': np.array([1.0, 1.0, 1.0]),  # meters

    # Inertia tensor (kg·m^2) - cube approximation
    'inertia': np.diag([800.0 * (1.0**2 + 1.0**2) / 12.0,
                       800.0 * (1.0**2 + 1.0**2) / 12.0,
                       800.0 * (1.0**2 + 1.0**2) / 12.0]),

    # Thruster capabilities
    'max_thrust': 20.0,  # N
    'min_thrust': 0.1,  # N
    'max_torque': 0.5,  # N·m

    # Initial orbit (400 km altitude, circular)
    'altitude_init': 400.0,  # km
    'orbit_radius_init': 6371.0 + 400.0,  # km
    'inclination': 51.6,  # degrees (ISS-like)
}

# ====================
# TARGET DEBRIS
# ====================
TARGET = {
    'mass': 50.0,  # kg
    'dimensions': np.array([0.5, 0.5, 0.5]),  # meters (500mm cube)

    # Inertia tensor (kg·m^2) - cube
    'inertia': np.diag([50.0 * (0.5**2 + 0.5**2) / 12.0,
                       50.0 * (0.5**2 + 0.5**2) / 12.0,
                       50.0 * (0.5**2 + 0.5**2) / 12.0]),

    # Initial tumbling (rad/s)
    'omega_init': np.array([0.1, 0.05, 0.15]),

    # Target orbit (600 km altitude, circular)
    'altitude_init': 600.0,  # km
    'orbit_radius_init': 6371.0 + 600.0,  # km
    'inclination': 51.6,  # degrees
}

# ====================
# MISSION PHASES
# ====================
MISSION_PHASES = {
    'phase_1_transfer': {
        'name': 'Hohmann Transfer',
        'duration': 3600.0,  # seconds (1 hour)
        'dt': 1.0,  # time step
    },

    'phase_2_approach': {
        'name': 'Far-range Approach',
        'duration': 21600.0,  # seconds (6 hours)
        'dt': 10.0,
        'initial_separation': 10.0,  # km
        'final_separation': 0.05,  # km (50m)
    },

    'phase_3_proximity': {
        'name': 'Proximity Operations',
        'duration': 3600.0,  # seconds (1 hour)
        'dt': 1.0,
        'initial_separation': 50.0,  # m
        'final_separation': 5.0,  # m
    },

    'phase_4_detumbling': {
        'name': 'Active Detumbling',
        'duration': 1800.0,  # seconds (30 min)
        'dt': 0.5,
        'target_omega': 0.01,  # rad/s (target tumbling rate)
        'ion_beam_force': 0.001,  # N·m (torque)
    },

    'phase_5_capture': {
        'name': 'Final Approach & Capture',
        'duration': 600.0,  # seconds (10 min)
        'dt': 0.1,
        'approach_velocity': 0.1,  # m/s
    },

    'phase_6_deorbit': {
        'name': 'Deorbit Burn',
        'target_altitude': 250.0,  # km (will decay naturally)
        'dt': 1.0,
    }
}

# ====================
# CONTROLLER PARAMETERS
# ====================
CONTROLLERS = {
    'mpc': {
        'horizon': 20,
        'Q': np.diag([100, 100, 100, 10, 10, 10]),  # State weights
        'R': np.diag([1, 1, 1]),  # Control weights
        'max_dv': 0.05,  # km/s per step
    },

    'pid_translation': {
        'Kp': 0.01,
        'Ki': 0.001,
        'Kd': 0.05,
        'max_output': 0.01,  # km/s
    },

    'pid_attitude': {
        'Kp': 0.5,
        'Ki': 0.01,
        'Kd': 0.1,
        'max_torque': 0.5,  # N·m
    },

    'lqr': {
        'Q': np.diag([1000, 1000, 1000, 100, 100, 100]),
        'R': np.diag([1, 1, 1]),
    }
}

# ====================
# SIMULATION SETTINGS
# ====================
SIMULATION = {
    'convergence_tolerance': {
        'position': 1e-3,  # km (1 meter)
        'velocity': 1e-6,  # km/s (1 mm/s)
        'attitude': 1e-3,  # rad
        'angular_velocity': 1e-3,  # rad/s
    },

    'max_iterations': 100000,
    'save_interval': 100,
    'verbose': True,
}

# ====================
# DEORBIT TARGET
# ====================
DEORBIT = {
    'target_perigee': 250.0,  # km altitude
    'target_perigee_radius': 6371.0 + 250.0,  # km
}
