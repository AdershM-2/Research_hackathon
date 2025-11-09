function results = simulate_approach(config, initial_sep, final_sep, duration, dt)
    % Simulate electrostatic tractor approach phase
    %
    % Inputs:
    %   config - Configuration structure
    %   initial_sep - Initial separation (km)
    %   final_sep - Final separation (km)
    %   duration - Simulation duration (seconds)
    %   dt - Time step (seconds)
    %
    % Outputs:
    %   results - Structure containing simulation results

    fprintf('\n=== ELECTROSTATIC TRACTOR APPROACH ===\n');
    fprintf('Initial separation: %.3f km\n', initial_sep);
    fprintf('Target separation: %.3f km\n', final_sep);
    fprintf('Duration: %.1f seconds (%.1f minutes)\n', duration, duration/60);

    % Initialize state
    % Start with debris at [initial_sep, 0, 0] with zero relative velocity
    state = [initial_sep; 0; 0; 0; 0; 0]; % [x, y, z, vx, vy, vz] in km, km/s
    target_state = [final_sep; 0; 0; 0; 0; 0];

    % Get parameters
    n = config.chaser.mean_motion;
    m_chaser = config.chaser.mass;
    q_debris = config.debris.charge;
    k = config.k_coulomb;

    % Storage for results
    num_steps = ceil(duration / dt);
    time_history = zeros(num_steps, 1);
    state_history = zeros(num_steps, 6);
    control_history = zeros(num_steps, 3);
    force_history = zeros(num_steps, 1);
    charge_history = zeros(num_steps, 1);
    energy_history = zeros(num_steps, 1);

    % Initial energy
    energy = config.chaser.energy_initial;

    % Simulation loop
    step = 1;
    converged = false;

    for t = 0:dt:duration
        % Current position vector (from chaser to debris)
        position_vector = state(1:3);
        distance = norm(position_vector);

        % LQR controller: compute desired acceleration
        [u_desired, ~] = lqr_controller(state, target_state, n, ...
                                        config.lqr.Q, config.lqr.R);

        % Required force magnitude for desired acceleration
        F_required = m_chaser * norm(u_desired) * 1000; % Convert km/s^2 to m/s^2, then N

        % Calculate required charge for this force
        % F = k * |q_chaser * q_debris| / r^2
        % q_chaser = F * r^2 / (k * |q_debris|)
        distance_m = distance * 1000; % Convert to meters
        q_required = (F_required * distance_m^2) / (k * abs(q_debris));

        % Limit charge to maximum capacity
        q_chaser = sign(q_debris) * min(abs(q_required), config.chaser.charge_max);

        % If q_debris is negative, we want positive q_chaser for attraction
        if q_debris < 0
            q_chaser = -abs(q_chaser); % Make it positive (opposite sign)
        else
            q_chaser = abs(q_chaser); % Make it negative
        end

        % Calculate actual Coulomb force and acceleration
        [~, F_mag, acceleration] = coulomb_force(q_chaser, q_debris, ...
                                                 position_vector, m_chaser, k);

        % Energy consumption (charging capacitors)
        % E = Q^2 / (2*C), assume C = 1 F for simplicity
        energy_used = (q_chaser^2) / (2 * 1.0) * config.chaser.voltage_max / 100e3;
        energy = energy - energy_used;

        % Store results
        time_history(step) = t;
        state_history(step, :) = state';
        control_history(step, :) = acceleration';
        force_history(step) = F_mag;
        charge_history(step) = q_chaser;
        energy_history(step) = energy;

        % Propagate state using RK4
        k1 = hcw_dynamics(t, state, acceleration, n);
        k2 = hcw_dynamics(t + dt/2, state + dt/2*k1, acceleration, n);
        k3 = hcw_dynamics(t + dt/2, state + dt/2*k2, acceleration, n);
        k4 = hcw_dynamics(t + dt, state + dt*k3, acceleration, n);
        state = state + (dt/6) * (k1 + 2*k2 + 2*k3 + k4);

        % Check convergence
        pos_error = norm(state(1:3) - target_state(1:3));
        vel_error = norm(state(4:6) - target_state(4:6));

        if pos_error < config.tol.position && vel_error < config.tol.velocity
            converged = true;
            fprintf('✓ Converged at t = %.1f seconds!\n', t);
            break;
        end

        % Progress update
        if mod(step, config.sim.plot_interval) == 0 && config.sim.verbose
            fprintf('t = %6.1f s | dist = %8.3f km | error = %8.3f km | F = %8.2e N\n', ...
                    t, distance, pos_error, F_mag);
        end

        step = step + 1;
        if step > num_steps
            break;
        end
    end

    % Trim arrays
    time_history = time_history(1:step-1);
    state_history = state_history(1:step-1, :);
    control_history = control_history(1:step-1, :);
    force_history = force_history(1:step-1);
    charge_history = charge_history(1:step-1);
    energy_history = energy_history(1:step-1);

    % Calculate final errors
    final_pos_error = norm(state(1:3) - target_state(1:3));
    final_vel_error = norm(state(4:6) - target_state(4:6));

    % Calculate total delta-v
    total_dv = sum(vecnorm(control_history', 2)') * dt;

    % Results structure
    results.success = converged;
    results.final_state = state;
    results.final_pos_error = final_pos_error;
    results.final_vel_error = final_vel_error;
    results.total_dv = total_dv;
    results.total_time = time_history(end);
    results.energy_used = config.chaser.energy_initial - energy;
    results.energy_remaining = energy;
    results.time = time_history;
    results.states = state_history;
    results.controls = control_history;
    results.forces = force_history;
    results.charges = charge_history;
    results.energy = energy_history;

    % Print summary
    fprintf('\n--- RESULTS ---\n');
    fprintf('Final position error: %.3f km (%.1f m)\n', final_pos_error, final_pos_error*1000);
    fprintf('Final velocity error: %.6f km/s (%.3f mm/s)\n', final_vel_error, final_vel_error*1e6);
    fprintf('Total Δv: %.3f km/s (%.1f m/s)\n', total_dv, total_dv*1000);
    fprintf('Energy used: %.2f MJ\n', results.energy_used/1e6);
    fprintf('Energy remaining: %.2f MJ\n', results.energy_remaining/1e6);
    fprintf('Converged: %s\n', mat2str(converged));
end
