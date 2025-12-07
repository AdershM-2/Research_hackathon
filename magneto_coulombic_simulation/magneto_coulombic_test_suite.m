%% MAGNETO-COULOMBIC ADR - COMPREHENSIVE TEST SUITE
% Tests the two-phase approach (Lorentz + Electrostatic Tractor) across
% varied operational scenarios
%
% Test Parameters:
% - Initial separation distance (5-20 km)
% - Debris mass (5-20 kg)
% - Orbital altitude (400-600 km) - affects B-field & velocity
% - Debris charge magnitude (3-12 mC)
% - Shell charge capacity (0.5-2 µC per shell)

clear; close all; clc;

fprintf('====================================\n');
fprintf('MAGNETO-COULOMBIC ADR TEST SUITE\n');
fprintf('====================================\n\n');

%% DEFINE TEST CASES
n_cases = 10;
test_cases = struct();

% Case 1: Nominal scenario
test_cases(1).name = 'Nominal';
test_cases(1).altitude = 500;
test_cases(1).initial_dist = 10;
test_cases(1).debris_mass = 10;
test_cases(1).debris_charge = 6e-3;
test_cases(1).shell_charge_capacity = 1e-6;

% Case 2: Closer initial separation
test_cases(2).name = 'Close Start';
test_cases(2).altitude = 500;
test_cases(2).initial_dist = 5;
test_cases(2).debris_mass = 10;
test_cases(2).debris_charge = 6e-3;
test_cases(2).shell_charge_capacity = 1e-6;

% Case 3: Farther initial separation
test_cases(3).name = 'Far Start';
test_cases(3).initial_dist = 20;
test_cases(3).altitude = 500;
test_cases(3).debris_mass = 10;
test_cases(3).debris_charge = 6e-3;
test_cases(3).shell_charge_capacity = 1e-6;

% Case 4: Heavier debris
test_cases(4).name = 'Heavy Debris';
test_cases(4).altitude = 500;
test_cases(4).initial_dist = 10;
test_cases(4).debris_mass = 20;
test_cases(4).debris_charge = 6e-3;
test_cases(4).shell_charge_capacity = 1e-6;

% Case 5: Lighter debris
test_cases(5).name = 'Light Debris';
test_cases(5).altitude = 500;
test_cases(5).initial_dist = 10;
test_cases(5).debris_mass = 5;
test_cases(5).debris_charge = 6e-3;
test_cases(5).shell_charge_capacity = 1e-6;

% Case 6: Lower altitude (stronger B-field)
test_cases(6).name = 'Low Altitude';
test_cases(6).altitude = 400;
test_cases(6).initial_dist = 10;
test_cases(6).debris_mass = 10;
test_cases(6).debris_charge = 6e-3;
test_cases(6).shell_charge_capacity = 1e-6;

% Case 7: Higher altitude (weaker B-field)
test_cases(7).name = 'High Altitude';
test_cases(7).altitude = 600;
test_cases(7).initial_dist = 10;
test_cases(7).debris_mass = 10;
test_cases(7).debris_charge = 6e-3;
test_cases(7).shell_charge_capacity = 1e-6;

% Case 8: Lower debris charge
test_cases(8).name = 'Low Debris Q';
test_cases(8).altitude = 500;
test_cases(8).initial_dist = 10;
test_cases(8).debris_mass = 10;
test_cases(8).debris_charge = 3e-3;
test_cases(8).shell_charge_capacity = 1e-6;

% Case 9: Higher debris charge
test_cases(9).name = 'High Debris Q';
test_cases(9).altitude = 500;
test_cases(9).initial_dist = 10;
test_cases(9).debris_mass = 10;
test_cases(9).debris_charge = 12e-3;
test_cases(9).shell_charge_capacity = 2e-6;

% Case 10: Combined challenging case
test_cases(10).name = 'Challenging';
test_cases(10).altitude = 600;
test_cases(10).initial_dist = 15;
test_cases(10).debris_mass = 15;
test_cases(10).debris_charge = 4e-3;
test_cases(10).shell_charge_capacity = 0.8e-6;

%% RUN ALL TEST CASES
results = struct();

for idx = 1:n_cases
    fprintf('\n========================================\n');
    fprintf('TEST CASE %d/%d: %s\n', idx, n_cases, test_cases(idx).name);
    fprintf('========================================\n');
    fprintf('  Altitude: %d km\n', test_cases(idx).altitude);
    fprintf('  Initial distance: %.1f km\n', test_cases(idx).initial_dist);
    fprintf('  Debris mass: %.1f kg\n', test_cases(idx).debris_mass);
    fprintf('  Debris charge: %.1f mC\n', test_cases(idx).debris_charge*1e3);
    fprintf('  Shell capacity: %.2f µC\n\n', test_cases(idx).shell_charge_capacity*1e6);

    % Run simulation for this case
    [converged, final_dist, final_vel, sim_time, phase1_time, phase2_time, ...
     mean_lorentz, mean_coulomb] = run_magneto_coulombic_simulation(...
        test_cases(idx).altitude, ...
        test_cases(idx).initial_dist, ...
        test_cases(idx).debris_mass, ...
        test_cases(idx).debris_charge, ...
        test_cases(idx).shell_charge_capacity, ...
        false);  % Don't plot individual cases

    % Store results
    results(idx).name = test_cases(idx).name;
    results(idx).converged = converged;
    results(idx).final_dist = final_dist;
    results(idx).final_vel = final_vel;
    results(idx).sim_time = sim_time;
    results(idx).phase1_time = phase1_time;
    results(idx).phase2_time = phase2_time;
    results(idx).mean_lorentz = mean_lorentz;
    results(idx).mean_coulomb = mean_coulomb;
    results(idx).altitude = test_cases(idx).altitude;
    results(idx).initial_dist = test_cases(idx).initial_dist;
    results(idx).debris_mass = test_cases(idx).debris_mass;
    results(idx).debris_charge = test_cases(idx).debris_charge;

    if converged
        fprintf('\n  Result: SUCCESS\n');
    else
        fprintf('\n  Result: FAILED\n');
    end
    fprintf('  Final distance: %.2f m\n', final_dist);
    fprintf('  Final velocity: %.3f m/s\n', final_vel);
    fprintf('  Total time: %.1f min\n', sim_time/60);
end

%% SUMMARY RESULTS
fprintf('\n\n');
fprintf('=====================================\n');
fprintf('TEST SUITE SUMMARY\n');
fprintf('=====================================\n\n');

success_count = sum([results.converged]);
fprintf('Overall Success Rate: %d/%d (%.1f%%)\n\n', success_count, n_cases, success_count/n_cases*100);

fprintf('%-15s | %-8s | %-10s | %-12s | %-10s\n', ...
    'Test Case', 'Success', 'Dist [m]', 'Time [min]', 'Phase 1 [min]');
fprintf('%s\n', repmat('-', 1, 75));

for idx = 1:n_cases
    if results(idx).converged
        conv_str = 'SUCCESS';
    else
        conv_str = 'FAILED';
    end
    fprintf('%-15s | %-8s | %10.2f | %12.1f | %10.1f\n', ...
        results(idx).name, ...
        conv_str, ...
        results(idx).final_dist, ...
        results(idx).sim_time/60, ...
        results(idx).phase1_time/60);
end

fprintf('\n');

%% SAVE RESULTS TO CSV
fid = fopen('magneto_coulombic_simulation/results/test_summary.csv', 'w');
fprintf(fid, 'Case,Name,Altitude_km,InitDist_km,Mass_kg,DebrisCharge_mC,Success,FinalDist_m,FinalVel_ms,Time_s,Phase1_s,Phase2_s,LorentzForce_uN,CoulombForce_mN\n');
for idx = 1:n_cases
    fprintf(fid, '%d,%s,%d,%.1f,%.1f,%.1f,%d,%.3f,%.4f,%.1f,%.1f,%.1f,%.3f,%.3f\n', ...
        idx, results(idx).name, results(idx).altitude, ...
        results(idx).initial_dist, results(idx).debris_mass, ...
        results(idx).debris_charge*1e3, results(idx).converged, ...
        results(idx).final_dist, results(idx).final_vel, ...
        results(idx).sim_time, results(idx).phase1_time, results(idx).phase2_time, ...
        results(idx).mean_lorentz*1e6, results(idx).mean_coulomb*1e3);
end
fclose(fid);
fprintf('Results exported to: magneto_coulombic_simulation/results/test_summary.csv\n');

%% COMPARATIVE PLOTS
figure('Position', [100 100 1400 800]);

% Success/Failure bar chart
subplot(2,3,1);
bar([results.converged], 'FaceColor', [0.2 0.7 0.3]);
xlabel('Test Case'); ylabel('Success (1) / Failure (0)');
title('Convergence Success by Test Case');
xticks(1:n_cases);
xticklabels({results.name});
xtickangle(45);
grid on;
ylim([0 1.2]);

% Final distance comparison
subplot(2,3,2);
bar([results.final_dist]);
xlabel('Test Case'); ylabel('Final Distance [m]');
title('Final Approach Distance');
hold on;
plot([0 n_cases+1], [0.6 0.6], 'r--', 'LineWidth', 2);
xticks(1:n_cases);
xticklabels({results.name});
xtickangle(45);
legend('Final Dist', 'Target (0.6 m)', 'Location', 'best');
grid on;

% Simulation time comparison
subplot(2,3,3);
bar([results.sim_time]/60);
xlabel('Test Case'); ylabel('Total Time [min]');
title('Mission Duration');
xticks(1:n_cases);
xticklabels({results.name});
xtickangle(45);
grid on;

% Phase breakdown
subplot(2,3,4);
phase1_times = [results.phase1_time]/60;
phase2_times = [results.phase2_time]/60;
bar(1:n_cases, [phase1_times; phase2_times]', 'stacked');
xlabel('Test Case'); ylabel('Time [min]');
title('Phase Breakdown (Lorentz vs Tractor)');
legend('Phase 1 (Lorentz)', 'Phase 2 (Tractor)', 'Location', 'best');
xticks(1:n_cases);
xticklabels({results.name});
xtickangle(45);
grid on;

% Force comparison
subplot(2,3,5);
yyaxis left;
bar(1:2:n_cases*2-1, [results.mean_lorentz]*1e6, 'FaceColor', [0.2 0.4 0.8]);
ylabel('Lorentz Force [µN]');
yyaxis right;
bar(2:2:n_cases*2, [results.mean_coulomb]*1e3, 'FaceColor', [0.8 0.2 0.2]);
ylabel('Coulomb Force [mN]');
xlabel('Test Case');
title('Mean Force Comparison');
xticks(1.5:2:n_cases*2);
xticklabels({results.name});
xtickangle(45);
grid on;

% Parameter correlation: Initial distance vs time
subplot(2,3,6);
scatter([results.initial_dist], [results.sim_time]/60, 100, [results.converged], 'filled');
xlabel('Initial Distance [km]');
ylabel('Mission Duration [min]');
title('Distance vs Duration (color = success)');
colormap([1 0 0; 0 1 0]);  % Red = fail, Green = success
colorbar('Ticks', [0 1], 'TickLabels', {'Failed', 'Success'});
grid on;

% sgtitle not supported in Octave
% sgtitle('Magneto-Coulombic ADR Test Suite - Comparative Analysis', ...
%     'FontSize', 14, 'FontWeight', 'bold');

% Save comparison plots
try
    print(gcf, 'magneto_coulombic_simulation/results/test_comparison.png', '-dpng');
    print(gcf, 'magneto_coulombic_simulation/results/test_comparison_highres.png', '-dpng', '-r300');
catch
    fprintf('Warning: Could not save figures\n');
end

fprintf('Comparison plots saved to magneto_coulombic_simulation/results/\n');
fprintf('\nTest suite complete!\n');

%% SIMULATION FUNCTION IS IN SEPARATE FILE: run_magneto_coulombic_simulation.m
