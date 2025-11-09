% Configuration for Electrostatic Tractor Debris Removal
% IIT Kanpur Research Hackathon 2025

function config = config_electrostatic()
    %% Physical Constants
    config.k_coulomb = 8.987551e9;      % N*m^2/C^2 (Coulomb's constant)
    config.mu_earth = 398600;           % km^3/s^2 (Earth's gravitational parameter)
    config.R_earth = 6371;              % km (Earth's radius)

    %% Chaser Spacecraft Parameters
    config.chaser.mass = 1270;          % kg
    config.chaser.charge_max = 1.0;     % Coulombs
    config.chaser.charge_min = -1.0;    % Coulombs
    config.chaser.voltage_max = 100e3;  % Volts (100 kV)
    config.chaser.energy_capacity = 1e9; % Joules (1 GJ)
    config.chaser.energy_initial = 5e8; % Joules (500 MJ)

    % Initial orbit (400 km altitude, circular)
    config.chaser.altitude = 400;       % km
    config.chaser.orbit_radius = config.R_earth + config.chaser.altitude; % km
    config.chaser.orbit_velocity = sqrt(config.mu_earth / config.chaser.orbit_radius); % km/s
    config.chaser.mean_motion = sqrt(config.mu_earth / config.chaser.orbit_radius^3); % rad/s

    %% Target Debris Parameters
    config.debris.mass = 50;            % kg
    config.debris.charge = -0.001;      % Coulombs (1 mC, naturally charged)
    config.debris.conductivity = 1e6;   % S/m (aluminum)

    % Tumbling rate
    config.debris.omega_init = [0.1; 0.05; 0.15]; % rad/s
    config.debris.omega_target = 0.01;  % rad/s (target after detumbling)

    % Target orbit (600 km altitude)
    config.debris.altitude = 600;       % km
    config.debris.orbit_radius = config.R_earth + config.debris.altitude; % km

    %% Mission Phases
    % Phase 2: Far-range approach
    config.phase2.initial_separation = 10.0;  % km
    config.phase2.final_separation = 0.05;    % km (50 m)
    config.phase2.duration = 7200;            % seconds (2 hours)
    config.phase2.dt = 1.0;                   % time step (1 second)

    % Phase 3: Proximity operations
    config.phase3.initial_separation = 50;    % m
    config.phase3.final_separation = 5;       % m
    config.phase3.duration = 3600;            % seconds (1 hour)
    config.phase3.dt = 0.1;                   % time step (0.1 second)

    % Phase 5: Capture
    config.phase5.final_separation = 0.5;     % m
    config.phase5.approach_velocity = 0.01;   % m/s
    config.phase5.duration = 600;             % seconds (10 min)
    config.phase5.dt = 0.1;                   % time step

    %% Control Parameters (LQR)
    % State weights [x, y, z, vx, vy, vz]
    config.lqr.Q = diag([1000, 1000, 1000, 100, 100, 100]);
    config.lqr.R = diag([1, 1, 1]);  % Control weights [ax, ay, az]

    %% Convergence Tolerances
    config.tol.position = 0.001;      % km (1 meter)
    config.tol.velocity = 1e-6;       % km/s (1 mm/s)
    config.tol.omega = 0.001;         % rad/s

    %% Simulation Settings
    config.sim.max_iterations = 100000;
    config.sim.verbose = true;
    config.sim.plot_interval = 100;

    fprintf('Configuration loaded successfully.\n');
    fprintf('Chaser orbit: %.0f km, Debris orbit: %.0f km\n', ...
            config.chaser.altitude, config.debris.altitude);
    fprintf('Mean motion: %.6f rad/s (Period: %.1f min)\n', ...
            config.chaser.mean_motion, 2*pi/config.chaser.mean_motion/60);
end
