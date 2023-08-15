from flask import Flask, request, jsonify

# from fastapi import FastAPI, Request
# from pydantic import BaseModel

app = Flask(__name__)
# fast_app = FastAPI()

#Health Criteria
def to_snake_case(value):
    return "_".join(value.lower().split())

ingredient_map = {
    "Calories": "calories",
    "Total Fat": to_snake_case("Total Fat"),
    "Saturated Fat": to_snake_case("Saturated Fat"),
    "Trans Fat": to_snake_case("Trans Fat"),
    "Cholesterol": to_snake_case("Cholestorol"),
    "Sodium": "sodium",
    "Total Carbohydrate": "carbohydrates",
    "Dietary Fiber": "fiber",
    "Sugar": "sugar",
    "Added Sugars": to_snake_case("Added Sugars"),
    "Protein": "protein",
    "Vitamin A": "vitamin_a",
    "Calcium": "calcium",
    "Vitamin C": "vitamin_c",
    "Vitamin D": "vitamin_d",
    "Iron": "iron"
    
}


#Weights for overall health criteria (Subject to change)
health_criteria_weights = {
    'nutrient_density': 0.4,
    'macronutrient_balance': 0.3,
    'absence_of_harmful_ingredients': 0.2,
    'adherence_to_dietary_principles': 0.1
}

nutrient_density_criteria = {
    'vitamin_a' : {'threshold': 0.125, 'weight': 0.4},
    'vitamin_c' : {'threshold': 0.1, 'weight': 0.3},
    'vitamin_d' : {'threshold': 0.1, 'weight': 0.2},
    'fiber' : {'threshold': 3, 'weight': 0.2},
    'iron': {'threshold': 0.5, 'weight': 0.2}
}

macronutrient_balance_criteria = {
    'carbohydrates': {'threshold': 40, 'weight': 0.4},
    'protein': {'threshold': 20, 'weight': 0.3},
    'total_fat': {'threshold': 30, 'weight': 0.3}
}
    
absence_of_harmful_ingredients_criteria = {
    'trans_fat': {'threshold': 0.5, 'weight': 0.5},
    'sodium': {'threshold': 200, 'weight': 0.5},
    'added_sugars': {'threshold': 10, 'weight': 0.5}
}
    
# Criterion 4: Adherence to Dietary Principles
adherence_to_dietary_principles_criteria = {
    'gluten_free': {'value': True, 'weight': 1.0},
    'organic': {'value': True, 'weight': 0.5}
}

nutrient_density_weight = health_criteria_weights['nutrient_density']
macronutrient_balance_weight = health_criteria_weights['macronutrient_balance']
absence_of_harmful_ingredients_weight = health_criteria_weights['absence_of_harmful_ingredients']
adherence_to_dietary_principles_weight = health_criteria_weights['adherence_to_dietary_principles']


def calculate_health_score(food_item):
    # Normalize Weights
    serving_size = food_item['serving_size']

    nutrient_density_score = calculate_weight_score(food_item, nutrient_density_criteria, 0)
    macronutrient_balance_score = calculate_weight_score(food_item, macronutrient_balance_criteria, 1)
    absence_of_harmful_ingredients_score = calculate_weight_score(food_item, absence_of_harmful_ingredients_criteria, 1)
    adherence_to_dietary_principles_score = calculate_weight_score(food_item, adherence_to_dietary_principles_criteria, 2)

    overall_score = (
        nutrient_density_weight * nutrient_density_score +
        macronutrient_balance_weight * macronutrient_balance_score +
        absence_of_harmful_ingredients_weight * absence_of_harmful_ingredients_score +
        adherence_to_dietary_principles_weight * adherence_to_dietary_principles_score
    )

    return overall_score
    


def calculate_weight_score(food_item, criteria, comparator):
    score = 0
    if comparator == 0:
        for nutrient, c in criteria.items():
            if nutrient in food_item and food_item[nutrient] >= c['threshold']:
                score += c['weight']
    elif comparator == 1:
        for nutrient, c in criteria.items():
            if nutrient in food_item and food_item[nutrient] <= c['threshold']:
                score += c['weight']
    else:
        for nutrient, c in criteria.items():
            if nutrient in food_item and food_item[nutrient] == c['value']:
                score += c['weight']

    return score


# @fast_app.get('/hello')
@app.route('/')
def start():
    return "Hello World"

# @fast_app.post('/score')
@app.route('/score', methods=["POST"])
def calculate_score():
    content = request.json["content"]
    contents = content.split('\n')
    serving_sizes = ["Serving Size", "serving size", "Serving size", "serving Size"]
    # print(contents)
    food_dict = dict()
    for i in range(1, len(contents)):
        curr = contents[i]
        split_str = curr.rsplit(" ", 1)
        # print(curr)
        # print(split_str)
        if "Serving size"in split_str[0]:
            food_dict["serving_size"] = int(''.join(filter(str.isdigit, split_str[1])))

        if "Percent" in split_str[0]:
            break

        elif split_str[0] in ingredient_map.keys() and len(split_str) == 1:
            next_split = contents[i+1].rsplit(" ", 1)
            food_dict[ingredient_map[split_str[0]]] = int(next_split[0])


            
        elif split_str[0] in ingredient_map.keys():
            if '%' in split_str[1]:
                split_str[1] = float(split_str[1].strip("%")) / 100
                food_dict[ingredient_map[split_str[0]]] = split_str[1]

            else: 
                food_dict[ingredient_map[split_str[0]]] = int(''.join(filter(str.isdigit, split_str[1])))
    # print(content)

    # print(food_dict)
    new_calculated_food_score = calculate_health_score(food_dict)
    # print(new_calculated_food_score)
    return str(new_calculated_food_score)
    # return jsonify(content)




if __name__ == "__main__":
    app.run(debug=True)