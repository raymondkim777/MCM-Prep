# Declaring packages
using JuMP, GLPK, HiGHS


# Preparing an optimization model
m = Model(HiGHS.Optimizer)


# Setting model parameters
t = 120                                     # days
w = 1                                       # number of reviews per restaurant
r = 1                                       # number of reviews per reviewer per days
c_r = 100.0                                 # salary per review
c_f = 100.0		                            # food allowance per review
c_t = 50			                        # travel allowance per review


# Adding data
R = [121, 315, 1768, 161, 86, 186, 139]     # array of restaurant cnts per region
P = [Inf for i in R]                        # array of max reviewers available per region


# Declaring variables
@variable(m, p[1:length(R)] >= 0, Int)


# Setting the objective
@objective(m, Min, sum(p))


# Adding constraints
# @constraint(m, people[i in 1:length(R)], p[i] <= P[i])
@constraint(m, reviews[i in 1:length(R)], p[i] * r * t >= R[i] * w)


# Printing the prepared optimization model
model_file = open("model.lp", "w")
print(model_file, m)
println(model_file)
close(model_file)

# Solving the optimization problem
JuMP.optimize!(m)

# Print the information about the optimum
results_file = open("results.lp", "w")
println(results_file, "PARAMETERS:")
println(results_file, "Days = ", t)
println(results_file, "Reviews per restaurant = ", w)
println(results_file, "Review rate = ", r)
println(results_file, "Review salary = \$", c_r)
println(results_file, "Food allowance = \$", c_f)
println(results_file, "Travel allowance = \$", c_t)

println(results_file, "\nRESULTS:")
println(results_file, "Total reviewers needed: ", objective_value(m))
println(results_file, "Reviewers needed per region: ")
println(results_file, value.(p))

# Compute total cost
let total_cost = 0
    for i in 1:length(p)
        total_cost += value.(p)[i] * r * ceil(R[i] * w / (value.(p)[i] * r)) * (c_r + c_f + c_t)
    end

    println(results_file, "\nTotal cost for ", t, " days:")
    println(results_file, "\$", total_cost)
end
# total_cost = objective_value(m) * r * t * (c_r + c_f + c_t)

close(results_file)
