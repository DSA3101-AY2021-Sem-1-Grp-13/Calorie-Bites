def calories_calculator(gender, weight, age_group, occ):
    if occ == 1:
        occ = 1.2
    elif occ == 2:
        occ = 1.35
    elif occ == 3:
        occ = 1.5
    else:
        occ = 1.65

    if gender == "female":
        if age_group == 1:
            calories = int( (13.1*weight+558) * occ )
        elif age_group in (2,3):
            calories = int( (9.74*weight+694) * occ )
        else:
            calories = int( (10.1*weight+569) * occ )
    else:
        if age_group == 1:
            calories = int( (16*weight+545) * occ )
        elif age_group in (2,3):
            calories = int( (14.2*weight+593) * occ )
        else:
            calories = int( (13.5*weight+514) * occ )

    return calories
  
def optimal_calories(gender, weight, age_group, occ): 
  recommended_calorie = calories_calculator(gender, weight, age_group, occ)
  return recommended_calorie
