# Declaring packages
using JuMP, HiGHS                       # You can replace HiGHS with GLPK, but there's really no need.


# Preparing an optimization model
m = Model(HiGHS.Optimizer)


# Setting model parameters
param1 = 1                              # Model parameters, not variables. 
param2 = 2                              # These values will not change once set.


# Adding model data
dataset1 = [1, 2, 3, 4, 5, 6]           # You can add additional data here. 
dataset2 = [2, 4, 6, 8, 10, 12]         # These values won't change either. 


# Declaring variables
@variable(m, var1 >= 0, Int)            # m: our model, var1: variable name, >= 0: non-negative constraints, Int: integer contraint
@variable(m, var2 >= 0, Bin)            # This declares a binary variable (1 or 0, True or False) called var2. 
                                        # Generally it's not recommended to mix variable types (MIP) since it takes much longer to solve. 

@variable(m, vars[1:5] >= 0, Int)       # This declares a list of variables, which you can access via vars[1], vars[2], etc. (1-based index)
                                        # Saves a lot of time, so highly recommend!


# Setting the objective
@objective(m, Min, param1 * var1 + var2)    # m: our model, Min: minimizing objective, (param1 * var1 + var2): objective function
@objective(m, Min, sum(vars))               # Our objective function can be anything. If it's nonlinear, make sure you're using HiGHS, not GLPK!
                                            # Also note: you can only have one objective function. (This code is ass)


# Adding constraints
@constraint(m, constraint1, -var1 + param2 * var2 <= 1)                 # Note: "constraint1" is the name of our constraint, and it's unimportant. 
                                                                        # Our code doesn't use this name. It's only used for the output of the model, 
                                                                        # to show which constraint is currently being processed/fitted.

@constraint(m, constraints[i in 1:length(vars)], vars[i] + var1 >= 8)   # We can group constraints together with iterators. 
                                                                        # Here, the iterator i is declared with the constraint name.


# Printing the optimization model
model_file = open("model.lp", "w")      # This is going to print our model information to a new file called "model.lp". 
println(model_file, m)                  # Feel free to ignore/delete this section if you want. 
close(model_file)                       # It can be useful for debugging, but not really.


# Solving the optimization problem
JuMP.optimize!(m)                       # This function calls the HiGHS optimizer (inputted as direct argument to m).


# Print optimum information
results_file = open("results.lp", "w")                              # This is going to print our optimized result to a new file called "results.lp". 
println(results_file, "PARAMETERS:")                                # You can have it print directly to console (just use print() function), 
println(results_file, "param1 = ", param1)                          # but having it in a dedicated file makes analyzing easier, and you don't lose results. 
println(results_file, "param2 = ", param2) 
println(results_file, "\nRESULTS:")
println(results_file, "Optimum objective: ", objective_value(m))    # The objective_value() function prints the minimized objective value. 
println(results_file, "Optimum variable: ", value(var1))            # The value() function prints the optimized value of a single variable. Don't include the period!
println(results_file, "Optimum variable list: ", value.(vars))      # The value.() function prints each optimum value of our variable list. Don't forget the period!
close(results_file)
