% Generate Comprehensive Plots from Test Results
% IIT Kanpur Research Hackathon 2025

clear; clc; close all;

fprintf('Generating plots from test results...\n');

% Load results
results_dir = '../Electrostatic_Test_Results';
load([results_dir '/comprehensive_test_summary.mat']);

% Create plots directory
plots_dir = [results_dir '/plots'];
if ~exist(plots_dir, 'dir')
    mkdir(plots_dir);
end

%% PLOT 1: Orbital Altitude Performance
figure('Position', [100, 100, 1000, 600]);

altitudes = [results_altitudes.altitude];
energies = [results_altitudes.energy_used] / 1e6;
errors = [results_altitudes.final_error] * 1000;
dvs = [results_altitudes.total_dv] * 1000;

subplot(1, 3, 1);
bar(altitudes, energies, 'FaceColor', [0.2 0.6 0.8]);
xlabel('Debris Altitude (km)');
ylabel('Energy Used (MJ)');
title('Energy vs Orbital Altitude');
grid on;

subplot(1, 3, 2);
bar(altitudes, errors, 'FaceColor', [0.8 0.4 0.2]);
xlabel('Debris Altitude (km)');
ylabel('Final Position Error (m)');
title('Convergence vs Altitude');
grid on;

subplot(1, 3, 3);
bar(altitudes, dvs, 'FaceColor', [0.4 0.8 0.4]);
xlabel('Debris Altitude (km)');
ylabel('Total Δv (m/s)');
title('Δv Budget vs Altitude');
grid on;

sgtitle('Test Suite 1: Orbital Altitude Variation', 'FontSize', 14, 'FontWeight', 'bold');
saveas(gcf, [plots_dir '/test1_altitude_performance.png']);

%% PLOT 2: Chaser Charge Capacity
figure('Position', [150, 150, 1000, 600]);

charges = [results_charges.charge_max];
max_forces = [results_charges.max_force];
avg_forces = [results_charges.avg_force];
charge_energies = [results_charges.energy_used] / 1e6;

subplot(1, 3, 1);
semilogy(charges, max_forces, 'bo-', 'LineWidth', 2, 'MarkerSize', 8, 'MarkerFaceColor', 'b');
hold on;
semilogy(charges, avg_forces, 'rs--', 'LineWidth', 2, 'MarkerSize', 8, 'MarkerFaceColor', 'r');
xlabel('Maximum Chaser Charge (C)');
ylabel('Force (N)');
title('Coulomb Force vs Charge Capacity');
legend('Max Force', 'Avg Force', 'Location', 'northwest');
grid on;

subplot(1, 3, 2);
plot(charges, charge_energies, 'go-', 'LineWidth', 2, 'MarkerSize', 10, 'MarkerFaceColor', 'g');
xlabel('Maximum Chaser Charge (C)');
ylabel('Energy Used (MJ)');
title('Energy Consumption vs Charge');
grid on;

subplot(1, 3, 3);
charge_errors = [results_charges.final_error] * 1000;
bar(charges, charge_errors, 'FaceColor', [0.7 0.3 0.7]);
xlabel('Maximum Chaser Charge (C)');
ylabel('Final Error (m)');
title('Convergence vs Charge Capacity');
grid on;

sgtitle('Test Suite 2: Chaser Charge Capacity Variation', 'FontSize', 14, 'FontWeight', 'bold');
saveas(gcf, [plots_dir '/test2_charge_capacity.png']);

%% PLOT 3: Orbital Inclination
figure('Position', [200, 200, 800, 600]);

inclinations = [results_inclinations.inclination];
incl_dvs = [results_inclinations.total_dv] * 1000;
incl_energies = [results_inclinations.energy_used] / 1e6;

subplot(2, 1, 1);
plot(inclinations, incl_dvs, 'bo-', 'LineWidth', 2, 'MarkerSize', 10, 'MarkerFaceColor', 'b');
xlabel('Orbital Inclination (degrees)');
ylabel('Total Δv (m/s)');
title('Δv Budget vs Inclination');
grid on;
xticks(inclinations);
xticklabels({'Equatorial', 'Cape', 'ISS', 'Polar', 'SSO'});

subplot(2, 1, 2);
plot(inclinations, incl_energies, 'rs-', 'LineWidth', 2, 'MarkerSize', 10, 'MarkerFaceColor', 'r');
xlabel('Orbital Inclination (degrees)');
ylabel('Energy Used (MJ)');
title('Energy Consumption vs Inclination');
grid on;
xticks(inclinations);
xticklabels({'Equatorial', 'Cape', 'ISS', 'Polar', 'SSO'});

sgtitle('Test Suite 3: Orbital Inclination Effects', 'FontSize', 14, 'FontWeight', 'bold');
saveas(gcf, [plots_dir '/test3_inclinations.png']);

%% PLOT 4: Debris Charge Variation
figure('Position', [250, 250, 1000, 600]);

debris_charges = [results_debris_charges.debris_charge];
debris_forces = [results_debris_charges.max_force];
debris_energies = [results_debris_charges.energy_used] / 1e6;

subplot(1, 2, 1);
semilogx(abs(debris_charges), debris_forces, 'bo-', 'LineWidth', 2, 'MarkerSize', 10, 'MarkerFaceColor', 'b');
xlabel('Debris Charge Magnitude (C)');
ylabel('Maximum Coulomb Force (N)');
title('Force vs Debris Charge');
grid on;

subplot(1, 2, 2);
semilogx(abs(debris_charges), debris_energies, 'rs-', 'LineWidth', 2, 'MarkerSize', 10, 'MarkerFaceColor', 'r');
xlabel('Debris Charge Magnitude (C)');
ylabel('Energy Used (MJ)');
title('Energy vs Debris Charge');
grid on;

sgtitle('Test Suite 4: Debris Charge Variation', 'FontSize', 14, 'FontWeight', 'bold');
saveas(gcf, [plots_dir '/test4_debris_charges.png']);

%% PLOT 5: Approach Distance vs Efficiency
figure('Position', [300, 300, 1000, 600]);

distances = [results_distances.distance];
dist_energies = [results_distances.energy_used] / 1e6;
dist_times = [results_distances.time] / 60;
efficiencies = [results_distances.efficiency];

subplot(1, 3, 1);
plot(distances, dist_energies, 'bo-', 'LineWidth', 2, 'MarkerSize', 10, 'MarkerFaceColor', 'b');
xlabel('Initial Separation (km)');
ylabel('Energy Used (MJ)');
title('Energy vs Approach Distance');
grid on;

subplot(1, 3, 2);
plot(distances, dist_times, 'rs-', 'LineWidth', 2, 'MarkerSize', 10, 'MarkerFaceColor', 'r');
xlabel('Initial Separation (km)');
ylabel('Mission Time (minutes)');
title('Time vs Approach Distance');
grid on;

subplot(1, 3, 3);
plot(distances, efficiencies, 'g^-', 'LineWidth', 2, 'MarkerSize', 10, 'MarkerFaceColor', 'g');
xlabel('Initial Separation (km)');
ylabel('Efficiency (m/s per MJ)');
title('Mission Efficiency');
grid on;

sgtitle('Test Suite 6: Approach Distance Effects', 'FontSize', 14, 'FontWeight', 'bold');
saveas(gcf, [plots_dir '/test6_approach_distances.png']);

%% PLOT 6: Stress Test Summary
figure('Position', [350, 350, 1000, 700]);

stress_names = {results_stress.name};
stress_success = [results_stress.success];
stress_errors = [results_stress.final_error] * 1000;
stress_dvs = [results_stress.total_dv] * 1000;
stress_energies = [results_stress.energy_used] / 1e6;

subplot(3, 1, 1);
bar(1:length(stress_names), stress_errors, 'FaceColor', [0.8 0.3 0.3]);
ylabel('Final Error (m)');
title('Stress Test: Position Errors');
xticks(1:length(stress_names));
xticklabels(stress_names);
xtickangle(15);
grid on;

subplot(3, 1, 2);
bar(1:length(stress_names), stress_dvs, 'FaceColor', [0.3 0.7 0.3]);
ylabel('Total Δv (m/s)');
title('Stress Test: Δv Budget');
xticks(1:length(stress_names));
xticklabels(stress_names);
xtickangle(15);
grid on;

subplot(3, 1, 3);
bar(1:length(stress_names), stress_energies, 'FaceColor', [0.3 0.3 0.8]);
ylabel('Energy Used (MJ)');
title('Stress Test: Energy Consumption');
xticks(1:length(stress_names));
xticklabels(stress_names);
xtickangle(15);
grid on;

sgtitle('Test Suite 5: Combined Stress Tests', 'FontSize', 14, 'FontWeight', 'bold');
saveas(gcf, [plots_dir '/test5_stress_tests.png']);

%% PLOT 7: Overall Success Rate Summary
figure('Position', [400, 400, 800, 600]);

test_names = {'Altitudes', 'Chaser Charge', 'Inclinations', 'Debris Charge', 'Stress Tests', 'Distances'};
success_rates = [
    sum([results_altitudes.success]) / length(results_altitudes) * 100;
    sum([results_charges.success]) / length(results_charges) * 100;
    sum([results_inclinations.success]) / length(results_inclinations) * 100;
    sum([results_debris_charges.success]) / length(results_debris_charges) * 100;
    sum([results_stress.success]) / length(results_stress) * 100;
    sum([results_distances.success]) / length(results_distances) * 100;
];

bar(success_rates, 'FaceColor', [0.2 0.7 0.4]);
ylabel('Success Rate (%)');
title('Overall Test Suite Success Rates', 'FontSize', 14, 'FontWeight', 'bold');
xticks(1:length(test_names));
xticklabels(test_names);
xtickangle(30);
ylim([0 105]);
grid on;

% Add percentage labels
for i = 1:length(success_rates)
    text(i, success_rates(i)+2, sprintf('%.0f%%', success_rates(i)), ...
         'HorizontalAlignment', 'center', 'FontSize', 11, 'FontWeight', 'bold');
end

saveas(gcf, [plots_dir '/summary_success_rates.png']);

fprintf('\n========================================\n');
fprintf('All plots generated successfully!\n');
fprintf('Saved to: %s\n', plots_dir);
fprintf('========================================\n');
