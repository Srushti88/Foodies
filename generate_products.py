import json
import random

categories = [
    "Burgers", "Pizza", "Fried Chicken", "Tacos & Wraps", "Sides & Appetizers",
    "Beverages", "Desserts", "Salads & Healthy Options", "Breakfast Items", "Limited Time Specials"
]

dietary_tags_options = ["spicy", "vegetarian", "vegan", "gluten_free", "contains_gluten", "dairy_free", "nuts_free"]
mood_tags_options = ["adventurous", "comfort", "indulgent", "healthy", "classic"]
allergens_options = ["gluten", "soy", "dairy", "nuts", "shellfish", "eggs"]
ingredients_samples = [
    "beef patty", "chicken breast", "lettuce", "tomato", "cheese", "brioche bun", "kimchi",
    "gochujang sauce", "jalapenos", "onion rings", "potato fries", "black beans", "tortilla",
    "ice cream", "chocolate chips", "caramel sauce", "vanilla", "coffee", "almond milk"
]

def generate_product(product_id):
    category = random.choice(categories)
    name = " ".join(random.sample(["Spicy", "Classic", "Fusion", "Dragon", "Burger", "Taco", "Pizza", "Fresh", "Crispy", "Sweet", "Savory"], k=3))
    description = f"Delicious {category.lower()} with unique flavors and fresh ingredients."
    ingredients = random.sample(ingredients_samples, k=random.randint(3,6))
    price = round(random.uniform(5, 20), 2)
    calories = random.randint(200, 900)
    prep_time = f"{random.randint(5,15)}-{random.randint(15,30)} mins"
    dietary_tags = random.sample(dietary_tags_options, k=random.randint(1,2))
    mood_tags = random.sample(mood_tags_options, k=random.randint(1,2))
    allergens = random.sample(allergens_options, k=random.randint(0,2))
    popularity_score = random.randint(50, 100)
    chef_special = random.choice([True, False])
    limited_time = random.choice([True, False])
    spice_level = random.randint(1, 10)
    image_prompt = f"image of a {name.lower()}"

    return {
        "product_id": f"FF{str(product_id).zfill(3)}",
        "name": name.strip(),
        "category": category,
        "description": description,
        "ingredients": ingredients,
        "price": price,
        "calories": calories,
        "prep_time": prep_time,
        "dietary_tags": dietary_tags,
        "mood_tags": mood_tags,
        "allergens": allergens,
        "popularity_score": popularity_score,
        "chef_special": chef_special,
        "limited_time": limited_time,
        "spice_level": spice_level,
        "image_prompt": image_prompt
    }

products = [generate_product(i) for i in range(1, 101)]

with open("fast_food_products.json", "w") as f:
    json.dump(products, f, indent=2)

print("Generated fast_food_products.json with 100 products.")
