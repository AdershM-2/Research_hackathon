function plot_results(results, title_prefix)
    % Plot simulation results
    %
    % Inputs:
    %   results - Results structure from simulate_approach
    %   title_prefix - Prefix for plot titles

    if nargin < 2
        title_prefix = '';
    end

    % Extract data
    t = results.time;
    states = results.states;
    controls = results.controls;
    forces = results.forces;
    charges = results.charges;
    energy = results.energy;

    % Position and velocity
    pos = states(:, 1:3);
    vel = states(:, 4:6);

    % Calculate distances
    distances = vecnorm(pos', 2)';

    %% Figure 1: 3D Trajectory
    figure('Name', [title_prefix ' - 3D Trajectory'], 'Position', [100, 100, 800, 600]);
    plot3(pos(:,1), pos(:,2), pos(:,3), 'b-', 'LineWidth', 1.5);
    hold on;
    plot3(pos(1,1), pos(1,2), pos(1,3), 'go', 'MarkerSize', 10, 'MarkerFaceColor', 'g');
    plot3(pos(end,1), pos(end,2), pos(end,3), 'ro', 'MarkerSize', 10, 'MarkerFaceColor', 'r');
    plot3(0, 0, 0, 'k*', 'MarkerSize', 15, 'LineWidth', 2);
    grid on;
    xlabel('x (km)');
    ylabel('y (km)');
    zlabel('z (km)');
    title([title_prefix ' - 3D Trajectory (Chaser to Debris)']);
    legend('Trajectory', 'Start', 'End', 'Target (Debris)', 'Location', 'best');
    axis equal;

    %% Figure 2: State History
    figure('Name', [title_prefix ' - State History'], 'Position', [150, 150, 1000, 700]);

    % Position
    subplot(2, 1, 1);
    plot(t, pos(:,1)*1000, 'r-', 'LineWidth', 1.5); hold on;
    plot(t, pos(:,2)*1000, 'g-', 'LineWidth', 1.5);
    plot(t, pos(:,3)*1000, 'b-', 'LineWidth', 1.5);
    plot(t, distances*1000, 'k--', 'LineWidth', 2);
    grid on;
    xlabel('Time (s)');
    ylabel('Position (m)');
    title([title_prefix ' - Position History']);
    legend('x', 'y', 'z', 'Distance', 'Location', 'best');

    % Velocity
    subplot(2, 1, 2);
    plot(t, vel(:,1)*1000, 'r-', 'LineWidth', 1.5); hold on;
    plot(t, vel(:,2)*1000, 'g-', 'LineWidth', 1.5);
    plot(t, vel(:,3)*1000, 'b-', 'LineWidth', 1.5);
    vel_mag = vecnorm(vel', 2)';
    plot(t, vel_mag*1000, 'k--', 'LineWidth', 2);
    grid on;
    xlabel('Time (s)');
    ylabel('Velocity (m/s)');
    title([title_prefix ' - Velocity History']);
    legend('v_x', 'v_y', 'v_z', '|v|', 'Location', 'best');

    %% Figure 3: Control and Forces
    figure('Name', [title_prefix ' - Control History'], 'Position', [200, 200, 1000, 700]);

    % Acceleration
    subplot(3, 1, 1);
    plot(t, controls(:,1)*1e6, 'r-', 'LineWidth', 1.5); hold on;
    plot(t, controls(:,2)*1e6, 'g-', 'LineWidth', 1.5);
    plot(t, controls(:,3)*1e6, 'b-', 'LineWidth', 1.5);
    grid on;
    xlabel('Time (s)');
    ylabel('Acceleration (mm/s²)');
    title([title_prefix ' - Control Acceleration']);
    legend('a_x', 'a_y', 'a_z', 'Location', 'best');

    % Coulomb Force
    subplot(3, 1, 2);
    plot(t, forces, 'b-', 'LineWidth', 1.5);
    grid on;
    xlabel('Time (s)');
    ylabel('Force (N)');
    title([title_prefix ' - Coulomb Force Magnitude']);

    % Chaser Charge
    subplot(3, 1, 3);
    plot(t, charges*1e6, 'r-', 'LineWidth', 1.5);
    grid on;
    xlabel('Time (s)');
    ylabel('Charge (μC)');
    title([title_prefix ' - Chaser Charge']);

    %% Figure 4: Energy History
    figure('Name', [title_prefix ' - Energy'], 'Position', [250, 250, 800, 500]);
    plot(t, energy/1e6, 'b-', 'LineWidth', 2);
    grid on;
    xlabel('Time (s)');
    ylabel('Energy (MJ)');
    title([title_prefix ' - Remaining Energy']);

    %% Figure 5: Distance vs Time
    figure('Name', [title_prefix ' - Distance'], 'Position', [300, 300, 800, 500]);
    semilogy(t, distances*1000, 'b-', 'LineWidth', 2);
    grid on;
    xlabel('Time (s)');
    ylabel('Distance to Debris (m)');
    title([title_prefix ' - Separation Distance (Log Scale)']);

    fprintf('\nPlots generated successfully.\n');
end
