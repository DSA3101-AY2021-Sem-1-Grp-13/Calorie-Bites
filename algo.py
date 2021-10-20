# Libraries
import pandas as pd
pd.options.mode.chained_assignment = None

#input basket for 1 week
def optimal_basket(recommended_calorie, product, amt_each_product, product_info, substitute_df):
  #2) calculate total calorie and price of current basket
  total_calorie = 0
  total_price = 0
  can_reduce = False
  for i in amt_each_product:
    if i > 1:
      can_reduce = True
      break
  df = pd.DataFrame(columns=product_info.columns)
  for i in range(len(product)):
    pdt_info = product_info[product_info.Product == product[i]]
    category = pdt_info.Category.tolist()[0]
    if not category in df.Category.unique().tolist():
      df = df.append(product_info[product_info.Category == category])
    total_calorie += list(pdt_info.Calories_kcal)[0] * amt_each_product[i]
    total_price += list(pdt_info.Price)[0] * amt_each_product[i]
    df.loc[df.Product == product[i], 'flag'] = True
  
  #3a) if total_calorie/7 <= recommended_calorie, do nth, is good, will not expect the customer to refine selection(5)
  if (total_calorie/7) <= recommended_calorie:
    return (total_calorie/7, total_price)

  #3b) if total_calorie/7 > recommended_calorie + 100, give slight warning message, will not expect the customer to refine selection(5)
  elif (total_calorie/7) < (recommended_calorie + 100):
    exceeded_cal_amt = total_calorie/7 - recommended_calorie
    return (total_calorie/7, exceeded_cal_amt, total_price)

  #3c) if total_calorie/7 > recommended_calorie by a lot
  else:
    cal_to_print = total_calorie/7
    #find products with healthier substitute
    pdt_with_substitute = substitute_df.antecedents.tolist()
    has_substitute = False
    for i in product:
      if i in pdt_with_substitute:
        has_substitute = True
        break

    new_pdt = []
    pdt_to_replace = []
    substituted_pdt = []
    #3.c.1 if there exist healthier substitute, replace
    if has_substitute:
      for i in range(len(product)):
        if product[i] in pdt_with_substitute:
          substitute = substitute_df[substitute_df.antecedents == product[i]].consequents.tolist()[0]
          if df.loc[df.Product == substitute, 'flag'].tolist()[0] == False:
            
            original_pdt_df = product_info[product_info.Product == product[i]]
            original_calorie = list(original_pdt_df.Calories_kcal)[0] * amt_each_product[i]
            original_price = list(original_pdt_df.Price)[0] * amt_each_product[i]
            
            substitute_d = product_info[product_info.Product == substitute]
            substitute_calorie = list(substitute_d.Calories_kcal)[0] * amt_each_product[i]
            substitute_price = list(substitute_d.Price)[0] * amt_each_product[i]
            df.loc[df.Product == substitute, 'flag'] = True
            substituted_pdt.append(substitute)
            
            df.loc[df.Product == product[i], 'flag'] = False
            pdt_to_replace.append(product[i])
 
            total_price = total_price - original_price + substitute_price
            total_calorie = total_calorie - original_calorie + substitute_calorie
            new_pdt.append(substitute)

          else:
            new_pdt.append(product[i])
        else:
          new_pdt.append(product[i])
          df.loc[df.Product == product[i], 'flag'] = True

      #if result after 3.c.1 is satisfactory
      if (total_calorie/7) < (recommended_calorie + 100):
        result = {'dataframe': df, 'total_price': total_price, 'total_calorie': total_calorie, 'recommended_calorie':recommended_calorie, 'product':new_pdt, 'amt':amt_each_product}
        sub = list(zip(pdt_to_replace, substituted_pdt))
        return [1, cal_to_print, sub, None, result]
      else:
        #3.c.2 if total_calorie still > recommended_calorie by a lot
        #cut down amt_each_product if > 1
        if can_reduce:
          current_set = df[df.flag == True]
          current_set['amt'] = 0
          current_set['initial_amt'] = 0
          for i in range(len(new_pdt)):
            current_set.loc[current_set.Product == new_pdt[i], 'amt'] = amt_each_product[i]
            current_set.loc[current_set.Product == new_pdt[i], 'initial_amt'] = amt_each_product[i]
            current_set.sort_values(by = ['amt', 'Calories_kcal'], inplace = True, ascending = False)
          current_set['total_price'] = [i*j for i, j in zip(current_set['amt'], current_set['Price'])]
          amt_sum = current_set['amt'].sum()

          while amt_sum > len(current_set):
            pdt = current_set.iloc[0].Product
            amt = current_set.loc[current_set.Product == pdt, 'amt']
            current_set.loc[current_set.Product == pdt, 'amt'] = amt - 1
            total_calorie -= current_set.loc[current_set.Product == pdt,'Calories_kcal'].tolist()[0]
            total_price -= current_set.loc[current_set.Product == pdt, 'Price'].tolist()[0]
            current_set.sort_values(by = ['amt', 'Calories_kcal'], inplace = True, ascending = False)
            amt_sum = current_set['amt'].sum()
            current_set['total_price'] = [i*j for i, j in zip(current_set['amt'], current_set['Price'])]
            if (total_calorie/7) < (recommended_calorie + 100):
              break

          if (total_calorie/7) < (recommended_calorie + 100):
            sub = list(zip(pdt_to_replace, substituted_pdt))

            amt_sub = []
            for i in range(len(current_set)):
              current = current_set.iloc[i]
              if current.initial_amt != current.amt:
                amt_sub.append([current.Product, current.initial_amt,current.amt])

            result = {'dataframe': df, 'total_price': total_price, 'total_calorie': total_calorie, 'recommended_calorie':recommended_calorie, 'product':new_pdt, 'amt':current_set.amt.tolist()}
            
            return [2, cal_to_print, sub, amt_sub, result]

          else: #still cannot reduce 3.c.3
            return [3, cal_to_print, None, None, {'dataframe':None, 'total_price': total_price, 'recommended_calorie': None, 'total_calorie': total_calorie, 'product': None, 'amt': None}]

    elif can_reduce: #3.c.4 if no substitute, but can reduce
      current_set = df[df.flag == True]
      current_set['amt'] = 0
      current_set['initial_amt'] = 0
      for i in range(len(product)):
        current_set.loc[current_set.Product == product[i], 'amt'] = amt_each_product[i]
        current_set.loc[current_set.Product == product[i], 'initial_amt'] = amt_each_product[i]
        current_set.sort_values(by = ['amt', 'Calories_kcal'], inplace = True, ascending = False)
        current_set['total_price'] = [i*j for i, j in zip(current_set['amt'], current_set['Price'])]
        amt_sum = current_set['amt'].sum()

        while amt_sum > len(current_set):
          pdt = current_set.iloc[0].Product
          amt = current_set.loc[current_set.Product == pdt, 'amt']
          current_set.loc[current_set.Product == pdt, 'amt'] = amt - 1
          total_calorie -= current_set.loc[current_set.Product == pdt,'Calories_kcal'].tolist()[0]
          total_price -= current_set.loc[current_set.Product == pdt, 'Price'].tolist()[0]
          current_set.sort_values(by = ['amt', 'Calories_kcal'], inplace = True, ascending = False)
          amt_sum = current_set['amt'].sum()
          current_set['total_price'] = [i*j for i, j in zip(current_set['amt'], current_set['Price'])]
          if (total_calorie/7) < (recommended_calorie + 100):
            break
      if (total_calorie/7) < (recommended_calorie + 100):
        amt_sub = []
        for i in range(len(current_set)):
          current = current_set.iloc[i]
          if current.initial_amt != current.amt:
            amt_sub.append([current.Product, current.initial_amt,current.amt])
          
        result = {'dataframe': df, 'total_price': total_price, 'total_calorie': total_calorie, 'recommended_calorie':recommended_calorie, 'product':new_pdt, 'amt':current_set.amt.tolist()}

        return [4, cal_to_print, None, amt_sub, result]

      else: #3.c.5 still not satisfactory
        return [3, cal_to_print, None, None, {'dataframe':None, 'total_price': total_price, 'recommended_calorie': None, 'total_calorie': total_calorie, 'product': None, 'amt': None}]

    else:#no substitute + cannot reduce 3.c.5
      return [3, cal_to_print, None, None, {'dataframe':None, 'total_price': total_price, 'recommended_calorie': None, 'total_calorie': total_calorie, 'product': None, 'amt': None}]

def change_product(tmp_df, products_to_change, reason, current_total_price, current_total_calorie, recommended_calorie, product_info):
  # products_to_change is a list of [product, amount] pair

  #remove the one he doesnt like from tmp_df, replace with another option from the same category with the smallest calorie
  can_change = False # as long as one product can be changed, this is True

  replacements = []
  error = False

  for i in range(len(products_to_change)):
    pdt_info = product_info[product_info.Product == products_to_change[i][0]]
    amt = products_to_change[i][1]
    tmp_df.loc[tmp_df.Product == pdt_info.Product.tolist()[0], 'flag'] = True

    original = True 
  #remove from tmp_df
    if reason == 'dislike':
      #sort by calorie
      
      result = helper_dislike(tmp_df, pdt_info, amt, current_total_calorie, recommended_calorie)
      new_product_info = result[0]
      original = result[1]

      #if original == False:
       # current_total_calorie = current_total_calorie - pdt_info.Calories_kcal.tolist()[0] * amt + new_product_info.Calories_kcal.tolist()[0] * amt# update current total calorie
        #current_total_price = current_total_price - pdt_info.Price.tolist()[0] + new_product_info.Price.tolist()[0]
      if original == False:
        current_total_calorie = current_total_calorie - pdt_info.Calories_kcal.tolist()[0] * amt + new_product_info.Calories_kcal * amt # update current total calorie
        current_total_price = current_total_price - pdt_info.Price.tolist()[0] + new_product_info.Price
        replacements.append([pdt_info.Product.tolist()[0], new_product_info.Product])
        can_change = True

    elif reason == 'expensive':
      #filter by price, sort by calories
      result = helper_expensive(tmp_df, pdt_info, amt, current_total_calorie, recommended_calorie)
      new_product_info = result[0]
      original = result[1]

      #if original:
        #current_total_calorie = current_total_calorie - pdt_info['Calories_kcal'].tolist()[0] * amt + new_product_info['Calories_kcal'].tolist()[0] * amt# update current total calorie
        #current_total_price = current_total_price - pdt_info['Price'].tolist()[0] * amt + new_product_info['Price'].tolist()[0] * amt
      if original == False:
        current_total_calorie = current_total_calorie - pdt_info['Calories_kcal'].tolist()[0] * amt + new_product_info['Calories_kcal'] * amt # update current total calorie
        current_total_price = current_total_price - pdt_info['Price'].tolist()[0] * amt + new_product_info['Price'] * amt
        replacements.append([pdt_info.Product.tolist()[0], new_product_info.Product])
        can_change = True

  if can_change == False:
    error = True

  return replacements, error, recommended_calorie, round(current_total_price, 2), round(current_total_calorie/ 7, 2)

def helper_dislike(tmp_df, pdt_info, amt, current_total_calorie, recommended_calorie):
    category = pdt_info.Category.tolist()[0]
    candidate_df = tmp_df[(tmp_df.Category == category) &
                          (tmp_df.flag == False)]

    if candidate_df.empty:
      return [pdt_info, True] # return original product

    for i in range(len(candidate_df)):
      
      new_pdt_info = candidate_df.sort_values(['Calories_per_100g', 'Calories_kcal']).iloc[i] # sort based on per 100g first
      if ((current_total_calorie - pdt_info['Calories_kcal'].tolist()[0] * amt + 
           new_pdt_info['Calories_kcal'] * amt) /7) < (recommended_calorie + 100):
        tmp_df.loc[tmp_df.Product == new_pdt_info.Product, 'flag'] = True # change the corresponding flag to True
        return [new_pdt_info, False] # return new product

      elif (i == (len(candidate_df)-1)) & (((current_total_calorie - pdt_info['Calories_kcal'].tolist()[0] * amt + 
                                         new_pdt_info['Calories_kcal'] * amt) /7) > (recommended_calorie + 100)):
        return [pdt_info, True] # return original product


def helper_expensive(tmp_df, pdt_info, amt, current_total_calorie, recommended_calorie):
    category = pdt_info.Category.tolist()[0]
    candidate_df = tmp_df[(tmp_df['Category'] == category) &
                          (tmp_df['flag'] == False) &
                          (tmp_df['Price'] < pdt_info['Price'].tolist()[0])]

    if candidate_df.empty:
      return [pdt_info, True] # return original product

    for i in range(len(candidate_df)):
      new_pdt_info = candidate_df.sort_values(['Calories_per_100g']).iloc[i] # sort based on per 100g first, as all are cheaper alr
      # new_pdt_info no need tolist()[0]

      if ((current_total_calorie - pdt_info['Calories_kcal'].tolist()[0] * amt + new_pdt_info['Calories_kcal'] * amt) /7) < (recommended_calorie + 100):
        tmp_df.loc[tmp_df['Product'] == new_pdt_info['Product'], 'flag'] = True # change the corresponding flag to True
        current_total_calorie = current_total_calorie - pdt_info['Calories_kcal'].tolist()[0] * amt + new_pdt_info['Calories_kcal'] * amt # update current total calorie
        return [new_pdt_info, False] # return new product
        
      elif (i == (len(candidate_df) - 1)) & (((current_total_calorie - pdt_info['Calories_kcal'].tolist()[0] * amt + new_pdt_info['Calories_kcal'] * amt) /7) > (recommended_calorie + 100)):
        return [pdt_info, True] # return original product
