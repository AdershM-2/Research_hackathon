% Comparison: Electrostatic Tractor vs Chemical Propulsion
% IIT Kanpur Research Hackathon 2025

clear; clc; close all;

fprintf('========================================\n');
fprintf('ELECTROSTATIC vs CHEMICAL PROPULSION\n');
fprintf('Comparison Analysis\n');
fprintf('IIT Kanpur Research Hackathon 2025\n');
fprintf('========================================\n\n');

%% Load Configuration
config = config_electrostatic();

%% Run Electrostatic Tractor Simulation
fprintf('Running Electrostatic Tractor simulation...\n');
results_electro = simulate_approach(config, ...
    config.phase2.initial_separation, ...
    config.phase2.final_separation, ...
    config.phase2.duration, ...
    config.phase2.dt);

%% Calculate Chemical Propulsion Equivalent
fprintf('\nCalculating chemical propulsion equivalent...\n');

% For chemical propulsion, same delta-v is needed
dv_total = results_electro.total_dv * 1000; % Convert to m/s

% Rocket equation: m_fuel = m_dry * (exp(dv/Isp/g) - 1)
% Typical chemical thruster: Isp = 300 s
Isp = 300; % seconds
g0 = 9.81; % m/s^2
m_dry = config.chaser.mass; % kg

% Fuel mass required
m_fuel_chemical = m_dry * (exp(dv_total/(Isp*g0)) - 1);

% Mission time for chemical (assume 10x faster acceleration)
time_chemical = results_electro.total_time / 10; % seconds

%% Comparison Table
fprintf('\n========================================\n');
fprintf('COMPARISON RESULTS\n');
fprintf('========================================\n\n');

fprintf('%-30s | %-15s | %-15s\n', 'Metric', 'Chemical', 'Electrostatic');
fprintf('%s\n', repmat('-', 1, 65));

fprintf('%-30s | %12.1f kg | %12.1f kg\n', 'Propellant Mass', m_fuel_chemical, 0);
fprintf('%-30s | %12.1f kg | %12.1f kg\n', 'Total Mass', m_dry + m_fuel_chemical, m_dry);
fprintf('%-30s | %12.1f m/s | %12.1f m/s\n', 'Mission Delta-v', dv_total, dv_total);
fprintf('%-30s | %12.1f min | %12.1f min\n', 'Mission Duration', time_chemical/60, results_electro.total_time/60);
fprintf('%-30s | %12.1f MJ | %12.1f MJ\n', 'Energy Used', 0, results_electro.energy_used/1e6);
fprintf('%-30s | %15s | %15s\n', 'Reusable', 'No', 'Yes');
fprintf('%-30s | %15s | %15s\n', 'Contact Risk', 'High', 'Zero');

fprintf('\n');

%% Savings Analysis
fprintf('========================================\n');
fprintf('SAVINGS ANALYSIS\n');
fprintf('========================================\n\n');

mass_savings = m_fuel_chemical;
mass_savings_percent = (mass_savings / (m_dry + m_fuel_chemical)) * 100;

fprintf('MASS SAVINGS:\n');
fprintf('  Fuel eliminated: %.1f kg\n', mass_savings);
fprintf('  Percentage reduction: %.1f%%\n', mass_savings_percent);
fprintf('  Launch cost savings (est): $%.1f M\n', mass_savings * 10000 / 1e6);

fprintf('\nOPERATIONAL ADVANTAGES:\n');
fprintf('  Electrostatic: Reusable for infinite missions\n');
fprintf('  Chemical: Single-use (fuel depleted)\n');
fprintf('  Electrostatic: Zero collision risk (contactless)\n');
fprintf('  Chemical: High risk (contact-based capture)\n');

fprintf('\nTRADE-OFFS:\n');
fprintf('  Time penalty: %.1fx longer\n', results_electro.total_time/time_chemical);
fprintf('  Complexity: Electrostatic more complex\n');
fprintf('  TRL: Chemical (9), Electrostatic (3-4)\n');

%% Economic Analysis
fprintf('\n========================================\n');
fprintf('ECONOMIC ANALYSIS (10-Mission Lifecycle)\n');
fprintf('========================================\n\n');

% Cost assumptions
cost_per_kg_launch = 10000; % $/kg
cost_chemical_fuel = 500; % $/kg
cost_electro_energy = 0.1; % $/MJ (solar recharged, minimal cost)
cost_spacecraft_base = 50e6; % $50M base cost

% Chemical system (10 missions = 10 spacecraft)
num_missions = 10;
cost_chemical_total = num_missions * (cost_spacecraft_base + ...
                      (m_dry + m_fuel_chemical) * cost_per_kg_launch + ...
                      m_fuel_chemical * cost_chemical_fuel);

% Electrostatic system (1 reusable spacecraft)
cost_electro_spacecraft = cost_spacecraft_base * 1.2; % 20% more complex
cost_electro_launch = m_dry * cost_per_kg_launch;
cost_electro_energy_total = num_missions * results_electro.energy_used/1e6 * cost_electro_energy;
cost_electro_total = cost_electro_spacecraft + cost_electro_launch + cost_electro_energy_total;

fprintf('CHEMICAL PROPULSION (10 missions):\n');
fprintf('  10 spacecraft @ $50M each:     $%.1f M\n', num_missions * cost_spacecraft_base / 1e6);
fprintf('  Launch costs (10 missions):     $%.1f M\n', num_missions * (m_dry + m_fuel_chemical) * cost_per_kg_launch / 1e6);
fprintf('  Fuel costs:                     $%.1f M\n', num_missions * m_fuel_chemical * cost_chemical_fuel / 1e6);
fprintf('  TOTAL:                          $%.1f M\n\n', cost_chemical_total / 1e6);

fprintf('ELECTROSTATIC TRACTOR (10 missions, reusable):\n');
fprintf('  1 spacecraft (advanced):        $%.1f M\n', cost_electro_spacecraft / 1e6);
fprintf('  Launch cost (1 time):           $%.1f M\n', cost_electro_launch / 1e6);
fprintf('  Energy costs (10 missions):     $%.1f M\n', cost_electro_energy_total / 1e6);
fprintf('  TOTAL:                          $%.1f M\n\n', cost_electro_total / 1e6);

cost_savings = cost_chemical_total - cost_electro_total;
cost_savings_percent = (cost_savings / cost_chemical_total) * 100;

fprintf('LIFECYCLE SAVINGS:\n');
fprintf('  Absolute savings: $%.1f M\n', cost_savings / 1e6);
fprintf('  Percentage savings: %.1f%%\n', cost_savings_percent);

%% Visualizations
fprintf('\n========================================\n');
fprintf('Generating comparison plots...\n');
fprintf('========================================\n');

% Plot 1: Mass Comparison
figure('Name', 'Mass Comparison', 'Position', [100, 100, 800, 500]);
categories = categorical({'Chemical', 'Electrostatic'});
mass_data = [m_dry + m_fuel_chemical, m_dry];
bar(categories, mass_data);
hold on;
bar(categories, [m_fuel_chemical, 0], 'FaceColor', 'r');
ylabel('Mass (kg)');
title('Total Mass Comparison');
legend('Dry Mass', 'Propellant Mass', 'Location', 'best');
grid on;

% Plot 2: Cost Comparison
figure('Name', 'Cost Comparison', 'Position', [150, 150, 800, 500]);
cost_data = [cost_chemical_total, cost_electro_total] / 1e6;
bar(categories, cost_data);
ylabel('Cost (Million $)');
title('10-Mission Lifecycle Cost Comparison');
grid on;
text(1, cost_data(1)+20, sprintf('$%.1fM', cost_data(1)), 'HorizontalAlignment', 'center');
text(2, cost_data(2)+20, sprintf('$%.1fM', cost_data(2)), 'HorizontalAlignment', 'center');

% Plot 3: Reusability
figure('Name', 'Reusability', 'Position', [200, 200, 800, 500]);
missions = 1:10;
chemical_mass = (m_dry + m_fuel_chemical) * missions;
electro_mass = m_dry * ones(size(missions));
plot(missions, chemical_mass/1000, 'r-o', 'LineWidth', 2, 'MarkerSize', 8); hold on;
plot(missions, electro_mass/1000, 'b-s', 'LineWidth', 2, 'MarkerSize', 8);
xlabel('Number of Missions');
ylabel('Cumulative Launch Mass (tons)');
title('Reusability Advantage');
legend('Chemical (New S/C each mission)', 'Electrostatic (Reusable)', 'Location', 'northwest');
grid on;

%% Summary
fprintf('\n========================================\n');
fprintf('KEY FINDINGS\n');
fprintf('========================================\n\n');

fprintf('✓ Electrostatic Tractor eliminates %.1f kg of fuel per mission\n', mass_savings);
fprintf('✓ %.1f%% mass reduction vs chemical system\n', mass_savings_percent);
fprintf('✓ Reusable spacecraft enables multi-mission operations\n');
fprintf('✓ $%.1fM cost savings over 10-mission lifecycle\n', cost_savings / 1e6);
fprintf('✓ Zero collision risk (contactless operation)\n');
fprintf('✗ Mission duration %.1fx longer than chemical\n', results_electro.total_time/time_chemical);
fprintf('✗ Lower TRL (3-4) requires development\n');

fprintf('\nRECOMMENDATION:\n');
fprintf('Electrostatic Tractor is ideal for:\n');
fprintf('  - Non-urgent debris removal missions\n');
fprintf('  - Cost-constrained programs\n');
fprintf('  - Multiple debris targets (reusability)\n');
fprintf('  - Risk-averse operations (contactless)\n');

fprintf('\n========================================\n');
fprintf('COMPARISON COMPLETE\n');
fprintf('========================================\n');

%% Save Results
save('comparison_results.mat', 'results_electro', 'config', ...
     'm_fuel_chemical', 'cost_chemical_total', 'cost_electro_total');
fprintf('\nResults saved to: comparison_results.mat\n');
