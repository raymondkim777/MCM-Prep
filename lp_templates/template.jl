# Declaring packages
using JuMP, HiGHS


# Preparing an optimization model
m = Model(HiGHS.Optimizer)


# Setting model parameters
param1 = 1 
param2 = 2 


# Adding model data
dataset1 = [1, 2, 3, 4, 5, 6]
dataset2 = [2, 4, 6, 8, 10, 12]


# Declaring variables
@variable(m, var1 >= 0, Int)
@variable(m, var2 >= 0, Bin)
@variable(m, vars[1:5] >= 0, Int)


# Setting the objective
@objective(m, Min, param1 * var1 + var2)


# Adding constraints
@constraint(m, constraint1, -var1 + param2 * var2 <= 1)
@constraint(m, constraints[i in 1:length(vars)], vars[i] + var1 >= 8)


# Printing the optimization model
model_file = open("model.lp", "w")
println(model_file, m)
close(model_file)


# Solving the optimization problem
JuMP.optimize!(m)


# Print optimum information
results_file = open("results.lp", "w")
println(results_file, "PARAMETERS:")
println(results_file, "param1 = ", param1)
println(results_file, "param2 = ", param2)
println(results_file, "\nRESULTS:")
println(results_file, "Optimum objective: ", objective_value(m))
println(results_file, "Optimum variable: ", value(var1))
println(results_file, "Optimum variable list: ", value.(vars))
close(results_file)
