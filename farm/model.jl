# Declaring packages
using JuMP, HiGHS, PrettyTables


# Preparing an optimization model
m = Model(HiGHS.Optimizer)


# Setting model parameters
crop_idx = Dict{String, Integer}(
    "wheat" => 1,
    "beans" => 2,
    "onions" => 3, 
    "cotton" => 4, 
    "maize" => 5,
    "tomatoes" => 6,
)
crop_idx_r = Dict{Integer, String}(
    1 => "wheat",
    2 => "beans",
    3 => "onions", 
    4 => "cotton", 
    5 => "maize",
    6 => "tomatoes"
)

crop_yield = [1.50, 1.00, 6.00, 1.50, 1.75, 6.00]    # ton/ha
crop_price = [1000, 2000, 750, 3500, 700, 800]       # $/ton
bundle = [
    [0, 1.20, 0, 0, 0.15, 0.25],     # bundle 1 
    [0, 0.73, 0, 0, 1.50, 0.25],     # bundle 2
    [0, 0.70, 0, 0, 1.00, 0.75]      # bundle 3
]

land_total = 10                 # total land available (ha)
land = [                        # fraction of month t that crop c occupies land --> land[t][c]
    [1, 1, 1, 0, 0, 0], 
    [1, 1, 1, 0, 0, 0], 
    [1, 1, 1, 0.5, 0, 0], 
    [1, 1, 1, 1, 0, 0], 
    [1, 0, 0.25, 1, 0.25, 0], 
    [0, 0, 0, 1, 1, 0], 
    [0, 0, 0, 1, 1, 0.75], 
    [0, 0, 0, 1, 1, 1], 
    [0, 0, 0, 1, 1, 1], 
    [0, 0, 0, 1, 0.5, 1], 
    [0.5, 0.25, 0.5, 0.75, 0, 0.75], 
    [1, 1, 1, 0, 0, 0], 
]

labor = [                       # labor required during month t for crop c --> labor[t][c] (hr per ha)
    [14, 6, 41, 0, 0, 0], 
    [4, 6, 40, 0, 0, 0], 
    [8, 6, 40, 40, 0, 0], 
    [8, 128, 155, 40, 0, 0], 
    [137, 0, 19, 72, 34, 0], 
    [0, 0, 0, 16, 40, 0], 
    [0, 0, 0, 12, 57, 136], 
    [0, 0, 0, 16, 64, 120], 
    [0, 0, 0, 8, 35, 96], 
    [0, 0, 0, 46, 9, 56], 
    [19, 60, 89, 34, 0, 48], 
    [11, 6, 37, 0, 0, 0], 
]
wage_rate_family = 4144         # family labor, dollars per year per man
wage_rate_perm = 5180           # permanent labor, dollars per year per man
wage_rate_temp = 4              # temporary labor, dollars per hour (per man doesn't apply, its only by hours)
labor_monthly_hr = [160, 160, 184, 176, 168, 176, 176, 176, 176, 168, 176, 176]   # working hours in month t (hr per man)
labor_family = 1.5              # family labor available (man)

water_annual_limit = 50         # annual water limit (kcub)
water_month_limit = 5           # monthly water limit (kcub)
water = [                       # water requriement for crop c in month t --> water[t][c]
    [0.535, 0.438, 0.452, 0, 0, 0], 
    [0.802, 0.479, 0.507, 0, 0, 0], 
    [0.556, 0.505, 0.640, 0.197, 0, 0], 
    [0.059, 0.142, 0.453, 0.494, 0, 0], 
    [0, 0, 0, 1.047, 0.303, 0], 
    [0, 0, 0, 1.064, 0.896, 0], 
    [0, 0, 0, 1.236, 1.318, 0.120], 
    [0, 0, 0, 0.722, 0.953, 0.241], 
    [0, 0, 0, 0.089, 0.205, 0.525], 
    [0, 0, 0, 0, 0, 0.881], 
    [0.373, 0.272, 0, 0, 0, 0.865], 
    [0.456, 0.335, 0.305, 0, 0, 0],
]
water_price = 10                # price of water, dollar/kcub


# Declaring variables
@variable(m, crop_amt[1:6] >= 0)        # amount of crop c planted (ha)
@variable(m, labor_perm >= 0)           # permanent labor hired (man)
@variable(m, labor_temp[1:12] >= 0)     # temporary labor hired in month t (hr)
@variable(m, crop_sale[1:6] >= 0)       # sales of crop c (ton)
@variable(m, b_frac[1:3] >= 0)          # fraction of bundle b consumed


# Setting the objective
@objective(m, Max, sum(
    [crop_price[c] * crop_sale[c] for c in 1:6]
) - wage_rate_family * labor_family - wage_rate_perm * labor_perm - wage_rate_temp * sum(
    labor_temp
) - water_price * sum(
    [water[t][c] * crop_amt[c] for c in 1:6 for t in 1:12]
))


# Adding constraints
@constraint(m, land_limitation[t in 1:12], sum(
    [land[t][c] * crop_amt[c] for c in 1:6]
) <= land_total)
@constraint(m, labor_requirements[t in 1:12], sum(
    [labor[t][c]  * crop_amt[c] for c in 1:6]
) <= labor_monthly_hr[t] * (labor_family + labor_perm) + labor_temp[t])
@constraint(m, water_monthly[t in 1:12], sum(
    [water[t][c]  * crop_amt[c] for c in 1:6]
) <= water_month_limit)
@constraint(m, water_annual, sum(
    [water[t][c]  * crop_amt[c] for c in 1:6 for t in 1:12]
) <= water_annual_limit)
@constraint(m, crop_req[c in 1:6], crop_yield[c] * crop_amt[c] == sum(
    [bundle[b][c] * b_frac[b] for b in 1:3]
) + crop_sale[c])
@constraint(m, b_frac_req, sum(b_frac) == 1)


# Printing the optimization model
model_file = open("model.lp", "w")
println(model_file, m)
close(model_file)


# Solving the optimization problem
JuMP.optimize!(m)


# Organize results for printing
data = hcat()


# Print optimum information
results_file = open("results.lp", "w")
println(results_file, "RESULTS:")
println(results_file, "Optimum objective: ", round(objective_value(m), digits=2))
println(results_file, "Optimum crop amounts: ")
for i in 1:6
    println(results_file, "    - ", crop_idx_r[i], ": ", round(value.(crop_amt)[i], digits=2), " ha")
end

println(results_file, "Optimum crop sales: ", value.(crop_sale))
println(results_file, "Optimum permanent labor: ", value.(labor_perm))
println(results_file, "Optimum temporary labor: ", value.(labor_temp))
println(results_file, "Optimum bundle fractions: ", value.(b_frac))
close(results_file)
