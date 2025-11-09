%% MAGNETO-COULOMBIC ACTIVE DEBRIS REMOVAL SIMULATION
% Two-Phase Approach:
% Phase 1: Lorentz force propulsion using Earth's magnetic field (10 km → 10 m)
% Phase 2: Electrostatic tractor for final approach and deorbit (10 m → capture)
%
% Innovation: Propellantless control via charged shells interacting with
% Earth's geomagnetic field (F = q × v × B)

clear; close all; clc;

%% MISSION PARAMETERS
% Target debris
debris_altitude = 500;  % [km] LEO altitude
debris_mass = 10;       % [kg] 500mm cubesat mass
initial_separation = 10; % [km] initial relative distance

% Chaser spacecraft
m_chaser = 50;  % [kg] including shells, electronics, propulsion backup

%% EARTH'S MAGNETIC FIELD MODEL
% Simplified dipole model for LEO
% B-field strength varies with latitude and altitude
% Typical LEO values: 25,000 - 65,000 nT

% Earth parameters
R_earth = 6371;  % [km] Earth radius
altitude_km = debris_altitude;
r_orbit = R_earth + altitude_km;  % [km] orbital radius

% Magnetic field strength (dipole approximation)
% At equator: B ≈ B0 * (R_earth / r)^3
B0_equator = 31000e-9;  % [T] field at Earth's surface (equator)
B_orbit = B0_equator * (R_earth / r_orbit)^3;  % [T] field at orbit

% For simulation, use average LEO value
B_field_strength = 40e-6;  % [T] 40,000 nT (conservative LEO average)

fprintf('=== MAGNETO-COULOMBIC ADR SIMULATION ===\n\n');
fprintf('Orbital Parameters:\n');
fprintf('  Altitude: %d km\n', altitude_km);
fprintf('  Magnetic Field: %.1f µT (%.0f nT)\n', B_field_strength*1e6, B_field_strength*1e9);

%% ORBITAL DYNAMICS SETUP
mu = 398600;  % [km^3/s^2] Earth gravitational parameter
n = sqrt(mu / r_orbit^3);  % [rad/s] mean motion
v_orbital = sqrt(mu / r_orbit);  % [km/s] orbital velocity
v_orbital_ms = v_orbital * 1000;  % [m/s] for Lorentz force

fprintf('  Orbital Velocity: %.2f km/s (%.0f m/s)\n', v_orbital, v_orbital_ms);
fprintf('  Mean Motion: %.6f rad/s\n\n', n);

%% CHARGED SHELL CONFIGURATION
% 6 shells at spacecraft extremities (±x, ±y, ±z in body frame)
n_shells = 6;
shell_separation = 0.5;  % [m] distance from center to each shell

% Shell positions in body frame [x; y; z] (meters)
shell_positions = [
     shell_separation,  0,                 0;     % +X
    -shell_separation,  0,                 0;     % -X
     0,                 shell_separation,  0;     % +Y
     0,                -shell_separation,  0;     % -Y
     0,                 0,                 shell_separation;  % +Z
     0,                 0,                -shell_separation   % -Z
]';  % 3×6 matrix

% Charge capacity per shell
Q_max_shell = 1e-6;  % [C] 1 µC at ±50 kV

fprintf('Charged Shell Configuration:\n');
fprintf('  Number of shells: %d\n', n_shells);
fprintf('  Shell separation: %.2f m\n', shell_separation);
fprintf('  Charge capacity: ±%.1f µC per shell\n', Q_max_shell*1e6);
fprintf('  Total charge capacity: ±%.1f µC\n\n', n_shells*Q_max_shell*1e6);

%% ELECTROSTATIC TRACTOR PARAMETERS (Phase 2)
% Debris charging via electron gun
Q_debris_target = -6e-3;  % [C] -6 mC (negative charge on debris)
charging_rate = 1e-4;     % [C/s] electron gun charging rate
Q_debris_current = 0;     % [C] starts uncharged

% Coulomb force parameters
k_e = 8.99e9;  % [N⋅m²/C²] Coulomb constant

% Debye shielding consideration (LEO plasma)
% Debye length in LEO: λ_D ≈ 1-10 cm
% Effective range for electrostatic forces: ~5-10 m (with active plasma management)
lambda_D = 0.05;  % [m] 5 cm typical LEO Debye length
effective_range_tractor = 10;  % [m] maximum effective range for tractor

fprintf('Electrostatic Tractor Parameters:\n');
fprintf('  Target debris charge: %.1f mC\n', Q_debris_target*1e3);
fprintf('  Charging rate: %.1f mC/s\n', charging_rate*1e3);
fprintf('  Debye length (LEO): %.0f cm\n', lambda_D*100);
fprintf('  Effective tractor range: %.0f m\n\n', effective_range_tractor);

%% CONTROL PARAMETERS
% Phase 1: Lorentz force control (far range: 10 km → 10 m)
phase1_threshold = 0.010;  % [km] 10 m - switch to Phase 2
lambda_lorentz = 0.5;      % Lorentz control gain
k_lorentz = 1.5;           % Lorentz stabilization gain

% Phase 2: Electrostatic tractor control (close range: 10 m → 0.6 m)
phase2_threshold = 0.0006; % [km] 600 mm target approach distance
lambda_tractor = 0.3;      % Tractor control gain
k_tractor = 1.2;           % Tractor stabilization gain

% Success criteria
max_distance_target = 0.0006;  % [km] < 600 mm
max_velocity_target = 0.001;   % [km/s] < 1 m/s

%% SIMULATION PARAMETERS
dt = 1.0;         % [s] time step
t_max = 15000;    % [s] maximum simulation time (~4.2 hours)
time = 0:dt:t_max;
n_steps = length(time);

%% STATE INITIALIZATION
% Initial relative state [x, y, z, vx, vy, vz] in LVLH frame
x0 = initial_separation;  % [km] radial (initially at 10 km)
y0 = 0;                   % [km] along-track
z0 = 0;                   % [km] cross-track
vx0 = 0;                  % [km/s]
vy0 = 0;                  % [km/s]
vz0 = 0;                  % [km/s]

state = [x0; y0; z0; vx0; vy0; vz0];

% History arrays
state_history = zeros(6, n_steps);
control_history = zeros(3, n_steps);
charge_history = zeros(n_shells, n_steps);
lorentz_force_history = zeros(3, n_steps);
coulomb_force_history = zeros(3, n_steps);
phase_history = zeros(1, n_steps);  % 1 = Lorentz, 2 = Tractor

%% SIMULATION LOOP
fprintf('Starting simulation...\n');
fprintf('Phase 1: Lorentz force approach (10 km → 10 m)\n');
fprintf('Phase 2: Electrostatic tractor (10 m → 600 mm)\n\n');

current_phase = 1;  % Start with Lorentz phase

for idx = 1:n_steps
    % Extract current state
    x = state(1); y = state(2); z = state(3);
    vx = state(4); vy = state(5); vz = state(6);

    % Relative distance and velocity
    r_rel = sqrt(x^2 + y^2 + z^2);  % [km]
    v_rel = sqrt(vx^2 + vy^2 + vz^2);  % [km/s]

    % Direction vectors
    if r_rel > 1e-6
        ex = x / r_rel;
        ey = y / r_rel;
        ez = z / r_rel;
    else
        ex = 1; ey = 0; ez = 0;
    end

    %% PHASE DETERMINATION
    if r_rel > phase1_threshold
        current_phase = 1;  % Lorentz phase (far range)
    else
        current_phase = 2;  % Electrostatic tractor phase (close range)
    end

    %% HCW NATURAL DYNAMICS (always present)
    % Acceleration due to orbital mechanics
    ax_natural = 3*n^2*x + 2*n*vy;
    ay_natural = -2*n*vx;
    az_natural = -n^2*z;

    %% CONTROL ACCELERATION (phase-dependent)
    if current_phase == 1
        %% ===== PHASE 1: LORENTZ FORCE CONTROL =====

        % Control law: exponential stabilization
        error = [x; y; z];
        error_dot = [vx; vy; vz];

        % Desired acceleration (feedforward + feedback)
        a_des_x = -lambda_lorentz * (vx + k_lorentz * x) - ax_natural;
        a_des_y = -lambda_lorentz * (vy + k_lorentz * y) - ay_natural;
        a_des_z = -lambda_lorentz * (vz + k_lorentz * z) - az_natural;

        a_des = [a_des_x; a_des_y; a_des_z];  % [km/s²]
        a_des_mag = norm(a_des);

        % LORENTZ FORCE GENERATION
        % F_Lorentz = q × (v × B)
        % For simplicity, assume B-field perpendicular to velocity (worst case)
        % Direction of B in LVLH: assume primarily in +Z direction (north)
        B_vec = [0; 0; B_field_strength];  % [T] simplified

        % Velocity vector in m/s (orbital + relative)
        % Dominant component is orbital velocity in +Y direction
        v_total = [vx*1000; v_orbital_ms + vy*1000; vz*1000];  % [m/s]

        % Calculate required total charge for desired force
        % F = Q_total × |v × B|
        v_cross_B = cross(v_total, B_vec);  % [m/s × T]
        v_cross_B_mag = norm(v_cross_B);

        % Required force [N]
        F_required = a_des_mag * m_chaser * 1e6;  % Convert km/s² to m/s²

        % Required total charge [C]
        if v_cross_B_mag > 1e-10
            Q_total_required = F_required / v_cross_B_mag;
        else
            Q_total_required = 0;
        end

        % Saturate to available charge capacity
        Q_total_max = n_shells * Q_max_shell;
        Q_total = max(-Q_total_max, min(Q_total_max, Q_total_required));

        % Distribute charge among shells (uniform for net force)
        % For attitude control, would use differential charging
        shell_charges = ones(n_shells, 1) * (Q_total / n_shells);

        % Calculate actual Lorentz force
        F_lorentz = Q_total * v_cross_B;  % [N] vector
        F_lorentz_mag = norm(F_lorentz);

        % Acceleration from Lorentz force [km/s²]
        a_lorentz = F_lorentz / (m_chaser * 1e3) / 1000;  % Convert to km/s²

        % Control acceleration (Lorentz only in Phase 1)
        a_control = a_lorentz;

        % No Coulomb force in Phase 1
        F_coulomb = [0; 0; 0];

    else
        %% ===== PHASE 2: ELECTROSTATIC TRACTOR CONTROL =====

        % Charge debris via electron gun (if not fully charged)
        if Q_debris_current > Q_debris_target
            Q_debris_current = max(Q_debris_target, Q_debris_current - charging_rate * dt);
        end

        % Control law for tractor phase
        error = [x; y; z];
        error_dot = [vx; vy; vz];

        a_des_x = -lambda_tractor * (vx + k_tractor * x) - ax_natural;
        a_des_y = -lambda_tractor * (vy + k_tractor * y) - ay_natural;
        a_des_z = -lambda_tractor * (vz + k_tractor * z) - az_natural;

        a_des = [a_des_x; a_des_y; a_des_z];
        a_des_mag = norm(a_des);

        % COULOMB FORCE CALCULATION
        % F = k_e × Q_chaser × Q_debris / r²

        % Required force [N]
        F_required = a_des_mag * m_chaser * 1e6;

        % Distance in meters
        r_meters = r_rel * 1000;

        % Solve for required chaser charge (opposite polarity for attraction)
        if r_meters > 0.1  % Avoid singularity
            Q_chaser_required = -F_required * r_meters^2 / (k_e * Q_debris_current);
        else
            Q_chaser_required = 0;
        end

        % Saturate to available charge
        Q_total_max = n_shells * Q_max_shell;
        Q_chaser = max(-Q_total_max, min(Q_total_max, Q_chaser_required));

        % Distribute charge (uniform)
        shell_charges = ones(n_shells, 1) * (Q_chaser / n_shells);

        % Actual Coulomb force
        if r_meters > 0.1
            F_coulomb_mag = k_e * abs(Q_chaser * Q_debris_current) / r_meters^2;
        else
            F_coulomb_mag = 0;
        end

        % Direction: opposite charges attract (toward debris)
        if Q_chaser * Q_debris_current < 0
            % Attraction (pull toward debris)
            F_coulomb_x = -F_coulomb_mag * ex;
            F_coulomb_y = -F_coulomb_mag * ey;
            F_coulomb_z = -F_coulomb_mag * ez;
        else
            % Repulsion (push away)
            F_coulomb_x = F_coulomb_mag * ex;
            F_coulomb_y = F_coulomb_mag * ey;
            F_coulomb_z = F_coulomb_mag * ez;
        end

        F_coulomb = [F_coulomb_x; F_coulomb_y; F_coulomb_z];  % [N]

        % Acceleration from Coulomb force [km/s²]
        a_coulomb = F_coulomb / (m_chaser * 1e3) / 1000;

        % Minimal Lorentz in Phase 2 (can be used for attitude)
        % For now, disable to isolate tractor performance
        a_lorentz = [0; 0; 0];
        F_lorentz = [0; 0; 0];

        % Control acceleration (Coulomb only in Phase 2)
        a_control = a_coulomb;
    end

    %% TOTAL ACCELERATION
    ax_total = ax_natural + a_control(1);
    ay_total = ay_natural + a_control(2);
    az_total = az_natural + a_control(3);

    %% STATE PROPAGATION (Euler integration)
    vx_new = vx + ax_total * dt;
    vy_new = vy + ay_total * dt;
    vz_new = vz + az_total * dt;

    x_new = x + vx * dt;
    y_new = y + vy * dt;
    z_new = z + vz * dt;

    % Update state
    state = [x_new; y_new; z_new; vx_new; vy_new; vz_new];

    %% STORE HISTORY
    state_history(:, idx) = state;
    control_history(:, idx) = a_control;
    charge_history(:, idx) = shell_charges;
    lorentz_force_history(:, idx) = norm(F_lorentz) * [ex; ey; ez];  % Simplified
    coulomb_force_history(:, idx) = F_coulomb;
    phase_history(idx) = current_phase;

    %% CONVERGENCE CHECK
    if r_rel*1000 < max_distance_target*1000 && v_rel*1000 < max_velocity_target*1000
        fprintf('SUCCESS! Converged at t = %.1f s (%.2f min)\n', time(idx), time(idx)/60);
        fprintf('  Final distance: %.2f mm\n', r_rel*1e6);
        fprintf('  Final velocity: %.2f mm/s\n\n', v_rel*1e6);

        % Truncate arrays
        time = time(1:idx);
        state_history = state_history(:, 1:idx);
        control_history = control_history(:, 1:idx);
        charge_history = charge_history(:, 1:idx);
        lorentz_force_history = lorentz_force_history(:, 1:idx);
        coulomb_force_history = coulomb_force_history(:, 1:idx);
        phase_history = phase_history(1:idx);
        break;
    end
end

%% FINAL RESULTS
final_dist = r_rel * 1000;  % [m]
final_vel = v_rel * 1000;   % [m/s]
converged = (final_dist < max_distance_target*1000) && (final_vel < max_velocity_target*1000);

fprintf('=== SIMULATION RESULTS ===\n\n');
if converged
    fprintf('Convergence: SUCCESS\n');
else
    fprintf('Convergence: FAILED\n');
end
fprintf('Final distance: %.2f m (target: < %.2f m)\n', final_dist, max_distance_target*1000);
fprintf('Final velocity: %.3f m/s (target: < %.2f m/s)\n', final_vel, max_velocity_target*1000);
fprintf('Total time: %.1f s (%.2f min)\n', time(end), time(end)/60);

% Phase statistics
phase1_time = sum(phase_history == 1) * dt;
phase2_time = sum(phase_history == 2) * dt;
fprintf('\nPhase Breakdown:\n');
fprintf('  Phase 1 (Lorentz): %.1f s (%.2f min)\n', phase1_time, phase1_time/60);
fprintf('  Phase 2 (Tractor): %.1f s (%.2f min)\n', phase2_time, phase2_time/60);

% Force statistics
lorentz_forces = sqrt(sum(lorentz_force_history.^2, 1));
coulomb_forces = sqrt(sum(coulomb_force_history.^2, 1));
mean_lorentz = mean(lorentz_forces(phase_history == 1));
mean_coulomb = mean(coulomb_forces(phase_history == 2));

fprintf('\nForce Statistics:\n');
fprintf('  Mean Lorentz force (Phase 1): %.2e N (%.3f µN)\n', mean_lorentz, mean_lorentz*1e6);
fprintf('  Mean Coulomb force (Phase 2): %.2e N (%.3f mN)\n', mean_coulomb, mean_coulomb*1e3);

% Charge statistics
total_charges = sum(charge_history, 1);
mean_charge_phase1 = mean(abs(total_charges(phase_history == 1)));
mean_charge_phase2 = mean(abs(total_charges(phase_history == 2)));
fprintf('\nCharge Utilization:\n');
fprintf('  Mean charge Phase 1: %.2f µC (%.1f%% of max)\n', ...
    mean_charge_phase1*1e6, mean_charge_phase1/(n_shells*Q_max_shell)*100);
fprintf('  Mean charge Phase 2: %.2f µC (%.1f%% of max)\n', ...
    mean_charge_phase2*1e6, mean_charge_phase2/(n_shells*Q_max_shell)*100);

%% VISUALIZATION
fprintf('\nGenerating plots...\n');

figure('Position', [100 100 1400 900]);

% Position plot
subplot(3,3,1);
plot(time/60, state_history(1,:)*1000, 'r', 'LineWidth', 1.5); hold on;
plot(time/60, state_history(2,:)*1000, 'g', 'LineWidth', 1.5);
plot(time/60, state_history(3,:)*1000, 'b', 'LineWidth', 1.5);
xlabel('Time [min]'); ylabel('Position [m]');
title('Relative Position vs Time');
legend('x (radial)', 'y (along-track)', 'z (cross-track)', 'Location', 'best');
grid on;

% Velocity plot
subplot(3,3,2);
plot(time/60, state_history(4,:)*1000, 'r', 'LineWidth', 1.5); hold on;
plot(time/60, state_history(5,:)*1000, 'g', 'LineWidth', 1.5);
plot(time/60, state_history(6,:)*1000, 'b', 'LineWidth', 1.5);
xlabel('Time [min]'); ylabel('Velocity [m/s]');
title('Relative Velocity vs Time');
legend('vx', 'vy', 'vz', 'Location', 'best');
grid on;

% Distance plot with phase indicators
subplot(3,3,3);
dist_m = sqrt(sum(state_history(1:3,:).^2, 1)) * 1000;
semilogy(time/60, dist_m, 'k', 'LineWidth', 2); hold on;
plot(time/60, phase1_threshold*1000*ones(size(time)), 'r--', 'LineWidth', 1.5);
plot(time/60, max_distance_target*1000*ones(size(time)), 'g--', 'LineWidth', 1.5);
xlabel('Time [min]'); ylabel('Distance [m] (log scale)');
title('Relative Distance vs Time');
legend('Distance', 'Phase 1→2 (10 m)', 'Target (0.6 m)', 'Location', 'best');
grid on;

% 3D trajectory
subplot(3,3,4);
plot3(state_history(1,:)*1000, state_history(2,:)*1000, state_history(3,:)*1000, 'b', 'LineWidth', 1.5);
hold on;
plot3(state_history(1,1)*1000, state_history(2,1)*1000, state_history(3,1)*1000, 'go', 'MarkerSize', 10, 'LineWidth', 2);
plot3(0, 0, 0, 'r*', 'MarkerSize', 15, 'LineWidth', 2);
xlabel('X [m]'); ylabel('Y [m]'); zlabel('Z [m]');
title('3D Trajectory (LVLH Frame)');
legend('Trajectory', 'Start', 'Debris', 'Location', 'best');
grid on; axis equal;

% Lorentz force
subplot(3,3,5);
plot(time/60, lorentz_forces*1e6, 'b', 'LineWidth', 1.5);
xlabel('Time [min]'); ylabel('Lorentz Force [µN]');
title('Lorentz Force Magnitude');
grid on;

% Coulomb force
subplot(3,3,6);
plot(time/60, coulomb_forces*1e3, 'r', 'LineWidth', 1.5);
xlabel('Time [min]'); ylabel('Coulomb Force [mN]');
title('Coulomb Force Magnitude');
grid on;

% Phase indicator
subplot(3,3,7);
area(time/60, phase_history, 'FaceColor', [0.7 0.9 1.0], 'EdgeColor', 'none');
xlabel('Time [min]'); ylabel('Phase');
title('Mission Phase (1=Lorentz, 2=Tractor)');
ylim([0.5 2.5]);
yticks([1 2]);
yticklabels({'Lorentz', 'Tractor'});
grid on;

% Total charge utilization
subplot(3,3,8);
plot(time/60, total_charges*1e6, 'k', 'LineWidth', 1.5); hold on;
plot(time/60, n_shells*Q_max_shell*1e6*ones(size(time)), 'r--', 'LineWidth', 1);
plot(time/60, -n_shells*Q_max_shell*1e6*ones(size(time)), 'r--', 'LineWidth', 1);
xlabel('Time [min]'); ylabel('Total Charge [µC]');
title('Charge Utilization');
legend('Actual', 'Limits', 'Location', 'best');
grid on;

% Control acceleration
subplot(3,3,9);
control_mag = sqrt(sum(control_history.^2, 1));
semilogy(time/60, control_mag*1e6, 'k', 'LineWidth', 1.5);
xlabel('Time [min]'); ylabel('Control Accel [mm/s²] (log)');
title('Control Acceleration Magnitude');
grid on;

% sgtitle not supported in Octave
% sgtitle('Magneto-Coulombic ADR: Two-Phase Approach (Lorentz + Electrostatic Tractor)', ...
%     'FontSize', 14, 'FontWeight', 'bold');

% Save figure
try
    print(gcf, 'magneto_coulombic_simulation/results/magneto_coulombic_results.png', '-dpng');
    print(gcf, 'magneto_coulombic_simulation/results/magneto_coulombic_results_highres.png', '-dpng', '-r300');
catch
    fprintf('Warning: Could not save figures\n');
end

fprintf('Plots saved to magneto_coulombic_simulation/results/\n');
fprintf('\nSimulation complete!\n');
