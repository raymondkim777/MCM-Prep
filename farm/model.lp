Max 1000 crop_sale[1] + 2000 crop_sale[2] + 750 crop_sale[3] + 3500 crop_sale[4] + 700 crop_sale[5] + 800 crop_sale[6] - 5180 labor_perm - 4 labor_temp[1] - 4 labor_temp[2] - 4 labor_temp[3] - 4 labor_temp[4] - 4 labor_temp[5] - 4 labor_temp[6] - 4 labor_temp[7] - 4 labor_temp[8] - 4 labor_temp[9] - 4 labor_temp[10] - 4 labor_temp[11] - 4 labor_temp[12] - 27.810000000000002 crop_amt[1] - 21.71 crop_amt[2] - 23.57 crop_amt[3] - 48.49 crop_amt[4] - 36.75 crop_amt[5] - 26.319999999999997 crop_amt[6] - 6216
Subject to
 crop_req[1] : 1.5 crop_amt[1] - crop_sale[1] == 0
 crop_req[2] : crop_amt[2] - crop_sale[2] - 1.2 b_frac[1] - 0.73 b_frac[2] - 0.7 b_frac[3] == 0
 crop_req[3] : 6 crop_amt[3] - crop_sale[3] == 0
 crop_req[4] : 1.5 crop_amt[4] - crop_sale[4] == 0
 crop_req[5] : 1.75 crop_amt[5] - crop_sale[5] - 0.15 b_frac[1] - 1.5 b_frac[2] - b_frac[3] == 0
 crop_req[6] : 6 crop_amt[6] - crop_sale[6] - 0.25 b_frac[1] - 0.25 b_frac[2] - 0.75 b_frac[3] == 0
 b_frac_req : b_frac[1] + b_frac[2] + b_frac[3] == 1
 land_limitation[1] : crop_amt[1] + crop_amt[2] + crop_amt[3] <= 10
 land_limitation[2] : crop_amt[1] + crop_amt[2] + crop_amt[3] <= 10
 land_limitation[3] : crop_amt[1] + crop_amt[2] + crop_amt[3] + 0.5 crop_amt[4] <= 10
 land_limitation[4] : crop_amt[1] + crop_amt[2] + crop_amt[3] + crop_amt[4] <= 10
 land_limitation[5] : crop_amt[1] + 0.25 crop_amt[3] + crop_amt[4] + 0.25 crop_amt[5] <= 10
 land_limitation[6] : crop_amt[4] + crop_amt[5] <= 10
 land_limitation[7] : crop_amt[4] + crop_amt[5] + 0.75 crop_amt[6] <= 10
 land_limitation[8] : crop_amt[4] + crop_amt[5] + crop_amt[6] <= 10
 land_limitation[9] : crop_amt[4] + crop_amt[5] + crop_amt[6] <= 10
 land_limitation[10] : crop_amt[4] + 0.5 crop_amt[5] + crop_amt[6] <= 10
 land_limitation[11] : 0.5 crop_amt[1] + 0.25 crop_amt[2] + 0.5 crop_amt[3] + 0.75 crop_amt[4] + 0.75 crop_amt[6] <= 10
 land_limitation[12] : crop_amt[1] + crop_amt[2] + crop_amt[3] <= 10
 labor_requirements[1] : 14 crop_amt[1] + 6 crop_amt[2] + 41 crop_amt[3] - 160 labor_perm - labor_temp[1] <= 240
 labor_requirements[2] : 4 crop_amt[1] + 6 crop_amt[2] + 40 crop_amt[3] - 160 labor_perm - labor_temp[2] <= 240
 labor_requirements[3] : 8 crop_amt[1] + 6 crop_amt[2] + 40 crop_amt[3] + 40 crop_amt[4] - 184 labor_perm - labor_temp[3] <= 276
 labor_requirements[4] : 8 crop_amt[1] + 128 crop_amt[2] + 155 crop_amt[3] + 40 crop_amt[4] - 176 labor_perm - labor_temp[4] <= 264
 labor_requirements[5] : 137 crop_amt[1] + 19 crop_amt[3] + 72 crop_amt[4] + 34 crop_amt[5] - 168 labor_perm - labor_temp[5] <= 252
 labor_requirements[6] : 16 crop_amt[4] + 40 crop_amt[5] - 176 labor_perm - labor_temp[6] <= 264
 labor_requirements[7] : 12 crop_amt[4] + 57 crop_amt[5] + 136 crop_amt[6] - 176 labor_perm - labor_temp[7] <= 264
 labor_requirements[8] : 16 crop_amt[4] + 64 crop_amt[5] + 120 crop_amt[6] - 176 labor_perm - labor_temp[8] <= 264
 labor_requirements[9] : 8 crop_amt[4] + 35 crop_amt[5] + 96 crop_amt[6] - 176 labor_perm - labor_temp[9] <= 264
 labor_requirements[10] : 46 crop_amt[4] + 9 crop_amt[5] + 56 crop_amt[6] - 168 labor_perm - labor_temp[10] <= 252
 labor_requirements[11] : 19 crop_amt[1] + 60 crop_amt[2] + 89 crop_amt[3] + 34 crop_amt[4] + 48 crop_amt[6] - 176 labor_perm - labor_temp[11] <= 264
 labor_requirements[12] : 11 crop_amt[1] + 6 crop_amt[2] + 37 crop_amt[3] - 176 labor_perm - labor_temp[12] <= 264
 water_monthly[1] : 0.535 crop_amt[1] + 0.438 crop_amt[2] + 0.452 crop_amt[3] <= 5
 water_monthly[2] : 0.802 crop_amt[1] + 0.479 crop_amt[2] + 0.507 crop_amt[3] <= 5
 water_monthly[3] : 0.556 crop_amt[1] + 0.505 crop_amt[2] + 0.64 crop_amt[3] + 0.197 crop_amt[4] <= 5
 water_monthly[4] : 0.059 crop_amt[1] + 0.142 crop_amt[2] + 0.453 crop_amt[3] + 0.494 crop_amt[4] <= 5
 water_monthly[5] : 1.047 crop_amt[4] + 0.303 crop_amt[5] <= 5
 water_monthly[6] : 1.064 crop_amt[4] + 0.896 crop_amt[5] <= 5
 water_monthly[7] : 1.236 crop_amt[4] + 1.318 crop_amt[5] + 0.12 crop_amt[6] <= 5
 water_monthly[8] : 0.722 crop_amt[4] + 0.953 crop_amt[5] + 0.241 crop_amt[6] <= 5
 water_monthly[9] : 0.089 crop_amt[4] + 0.205 crop_amt[5] + 0.525 crop_amt[6] <= 5
 water_monthly[10] : 0.881 crop_amt[6] <= 5
 water_monthly[11] : 0.373 crop_amt[1] + 0.272 crop_amt[2] + 0.865 crop_amt[6] <= 5
 water_monthly[12] : 0.456 crop_amt[1] + 0.335 crop_amt[2] + 0.305 crop_amt[3] <= 5
 water_annual : 2.781 crop_amt[1] + 2.1710000000000003 crop_amt[2] + 2.357 crop_amt[3] + 4.849 crop_amt[4] + 3.6750000000000003 crop_amt[5] + 2.6319999999999997 crop_amt[6] <= 50
 crop_amt[1] >= 0
 crop_amt[2] >= 0
 crop_amt[3] >= 0
 crop_amt[4] >= 0
 crop_amt[5] >= 0
 crop_amt[6] >= 0
 labor_perm >= 0
 labor_temp[1] >= 0
 labor_temp[2] >= 0
 labor_temp[3] >= 0
 labor_temp[4] >= 0
 labor_temp[5] >= 0
 labor_temp[6] >= 0
 labor_temp[7] >= 0
 labor_temp[8] >= 0
 labor_temp[9] >= 0
 labor_temp[10] >= 0
 labor_temp[11] >= 0
 labor_temp[12] >= 0
 crop_sale[1] >= 0
 crop_sale[2] >= 0
 crop_sale[3] >= 0
 crop_sale[4] >= 0
 crop_sale[5] >= 0
 crop_sale[6] >= 0
 b_frac[1] >= 0
 b_frac[2] >= 0
 b_frac[3] >= 0

