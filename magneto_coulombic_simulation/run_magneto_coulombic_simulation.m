function [converged, final_dist, final_vel, sim_time, phase1_time, phase2_time, ...
          mean_lorentz, mean_coulomb] = run_magneto_coulombic_simulation(...
          altitude, initial_separation, debris_mass, Q_debris_target, Q_max_shell, do_plot)

    % Spacecraft parameters
    m_chaser = 50;  % [kg]
    n_shells = 6;

    % Earth & orbital parameters
    R_earth = 6371;  % [km]
    mu = 398600;  % [km^3/s^2]
    r_orbit = R_earth + altitude;
    n = sqrt(mu / r_orbit^3);  % [rad/s]
    v_orbital = sqrt(mu / r_orbit);  % [km/s]
    v_orbital_ms = v_orbital * 1000;  % [m/s]

    % Magnetic field (altitude-dependent)
    B0_equator = 31000e-9;  % [T]
    B_field_strength = B0_equator * (R_earth / r_orbit)^3;
    B_field_strength = max(25e-6, min(65e-6, B_field_strength));  % Clamp to LEO range

    % Coulomb parameters
    k_e = 8.99e9;
    charging_rate = 1e-4;  % [C/s]
    Q_debris_current = 0;

    % Control parameters
    phase1_threshold = 0.010;  % [km] 10 m
    phase2_threshold = 0.0006;  % [km] 600 mm
    lambda_lorentz = 0.5;
    k_lorentz = 1.5;
    lambda_tractor = 0.3;
    k_tractor = 1.2;

    % Success criteria
    max_distance_target = 0.0006;  % [km]
    max_velocity_target = 0.001;  % [km/s]

    % Simulation parameters
    dt = 1.0;
    t_max = 20000;  % Extended time for challenging cases
    time = 0:dt:t_max;
    n_steps = length(time);

    % Initial state
    state = [initial_separation; 0; 0; 0; 0; 0];

    % History
    phase_history = zeros(1, n_steps);
    lorentz_force_history = zeros(1, n_steps);
    coulomb_force_history = zeros(1, n_steps);

    % Main simulation loop
    current_phase = 1;

    for idx = 1:n_steps
        x = state(1); y = state(2); z = state(3);
        vx = state(4); vy = state(5); vz = state(6);

        r_rel = sqrt(x^2 + y^2 + z^2);
        v_rel = sqrt(vx^2 + vy^2 + vz^2);

        if r_rel > 1e-6
            ex = x / r_rel; ey = y / r_rel; ez = z / r_rel;
        else
            ex = 1; ey = 0; ez = 0;
        end

        % Phase determination
        if r_rel > phase1_threshold
            current_phase = 1;
        else
            current_phase = 2;
        end

        % HCW natural dynamics
        ax_natural = 3*n^2*x + 2*n*vy;
        ay_natural = -2*n*vx;
        az_natural = -n^2*z;

        % Control
        if current_phase == 1
            % Lorentz phase
            a_des_x = -lambda_lorentz * (vx + k_lorentz * x) - ax_natural;
            a_des_y = -lambda_lorentz * (vy + k_lorentz * y) - ay_natural;
            a_des_z = -lambda_lorentz * (vz + k_lorentz * z) - az_natural;
            a_des = [a_des_x; a_des_y; a_des_z];
            a_des_mag = norm(a_des);

            % Lorentz force
            B_vec = [0; 0; B_field_strength];
            v_total = [vx*1000; v_orbital_ms + vy*1000; vz*1000];
            v_cross_B = cross(v_total, B_vec);
            v_cross_B_mag = norm(v_cross_B);

            F_required = a_des_mag * m_chaser * 1e6;

            if v_cross_B_mag > 1e-10
                Q_total_required = F_required / v_cross_B_mag;
            else
                Q_total_required = 0;
            end

            Q_total_max = n_shells * Q_max_shell;
            Q_total = max(-Q_total_max, min(Q_total_max, Q_total_required));

            F_lorentz = Q_total * v_cross_B;
            a_control = F_lorentz / (m_chaser * 1e3) / 1000;

            lorentz_force_history(idx) = norm(F_lorentz);
            coulomb_force_history(idx) = 0;

        else
            % Tractor phase
            if Q_debris_current > Q_debris_target
                Q_debris_current = max(Q_debris_target, Q_debris_current - charging_rate * dt);
            end

            a_des_x = -lambda_tractor * (vx + k_tractor * x) - ax_natural;
            a_des_y = -lambda_tractor * (vy + k_tractor * y) - ay_natural;
            a_des_z = -lambda_tractor * (vz + k_tractor * z) - az_natural;
            a_des = [a_des_x; a_des_y; a_des_z];
            a_des_mag = norm(a_des);

            F_required = a_des_mag * m_chaser * 1e6;
            r_meters = r_rel * 1000;

            if r_meters > 0.1
                Q_chaser_required = -F_required * r_meters^2 / (k_e * Q_debris_current);
            else
                Q_chaser_required = 0;
            end

            Q_total_max = n_shells * Q_max_shell;
            Q_chaser = max(-Q_total_max, min(Q_total_max, Q_chaser_required));

            if r_meters > 0.1
                F_coulomb_mag = k_e * abs(Q_chaser * Q_debris_current) / r_meters^2;
            else
                F_coulomb_mag = 0;
            end

            if Q_chaser * Q_debris_current < 0
                a_control = -F_coulomb_mag / (m_chaser * 1e3) / 1000 * [ex; ey; ez];
            else
                a_control = F_coulomb_mag / (m_chaser * 1e3) / 1000 * [ex; ey; ez];
            end

            lorentz_force_history(idx) = 0;
            coulomb_force_history(idx) = F_coulomb_mag;
        end

        phase_history(idx) = current_phase;

        % Propagate
        ax_total = ax_natural + a_control(1);
        ay_total = ay_natural + a_control(2);
        az_total = az_natural + a_control(3);

        vx_new = vx + ax_total * dt;
        vy_new = vy + ay_total * dt;
        vz_new = vz + az_total * dt;

        x_new = x + vx * dt;
        y_new = y + vy * dt;
        z_new = z + vz * dt;

        state = [x_new; y_new; z_new; vx_new; vy_new; vz_new];

        % Check convergence
        if r_rel*1000 < max_distance_target*1000 && v_rel*1000 < max_velocity_target*1000
            time = time(1:idx);
            phase_history = phase_history(1:idx);
            lorentz_force_history = lorentz_force_history(1:idx);
            coulomb_force_history = coulomb_force_history(1:idx);
            break;
        end
    end

    % Results
    final_dist = r_rel * 1000;
    final_vel = v_rel * 1000;
    converged = (final_dist < max_distance_target*1000) && (final_vel < max_velocity_target*1000);
    sim_time = time(end);

    phase1_time = sum(phase_history == 1) * dt;
    phase2_time = sum(phase_history == 2) * dt;

    mean_lorentz = mean(lorentz_force_history(phase_history == 1));
    if sum(phase_history == 2) > 0
        mean_coulomb = mean(coulomb_force_history(phase_history == 2));
    else
        mean_coulomb = 0;
    end
end
