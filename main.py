from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from databases import Database
from sqlalchemy import Table, Column, String, Float, Integer, MetaData, Boolean, JSON, create_engine, select, and_, func
import json

DATABASE_URL = "sqlite:///./foodiebot.db"

database = Database(DATABASE_URL)
metadata = MetaData()
from fastapi.middleware.cors import CORSMiddleware


# Product Table Model
products = Table(
    "products",
    metadata,
    Column("product_id", String, primary_key=True),
    Column("name", String, nullable=False),
    Column("category", String, nullable=False),
    Column("description", String),
    Column("ingredients", String),  # Stored as JSON string
    Column("price", Float),
    Column("calories", Integer),
    Column("prep_time", String),
    Column("dietary_tags", String),  # JSON string list
    Column("mood_tags", String),     # JSON string list
    Column("allergens", String),     # JSON string list
    Column("popularity_score", Integer),
    Column("chef_special", Boolean),
    Column("limited_time", Boolean),
    Column("spice_level", Integer),
    Column("image_prompt", String),
)

engine = create_engine(DATABASE_URL)
metadata.create_all(engine)

class Product(BaseModel):
    product_id: str
    name: str
    category: str
    description: Optional[str]
    ingredients: List[str]
    price: float
    calories: Optional[int]
    prep_time: Optional[str]
    dietary_tags: List[str]
    mood_tags: List[str]
    allergens: List[str]
    popularity_score: Optional[int]
    chef_special: Optional[bool]
    limited_time: Optional[bool]
    spice_level: Optional[int]
    image_prompt: Optional[str]

app = FastAPI(title="FoodieBot API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post("/products/", response_model=Product)
async def create_product(product: Product):
    # Serialize JSON list fields as strings for storage
    values = product.dict()
    values['ingredients'] = json.dumps(values['ingredients'])
    values['dietary_tags'] = json.dumps(values['dietary_tags'])
    values['mood_tags'] = json.dumps(values['mood_tags'])
    values['allergens'] = json.dumps(values['allergens'])
    query = products.insert().values(**values)
    await database.execute(query)
    return product

def json_array_contains(column, item):
    # SQLite does not have a built-in JSON array contains function,
    # so we check if the item string is contained inside the JSON string.
    # This is a simple workaround; for production, use PostgreSQL JSONB features.
    return func.instr(column, f'"{item}"') > 0

@app.get("/products/", response_model=List[Product])
async def get_products(category: str = None, max_price: float = None, mood: str = None, dietary_restriction: str = None):
    query = products.select()

    conditions = []

    if category:
        conditions.append(products.c.category == category)
    if max_price is not None:
        conditions.append(products.c.price <= max_price)
    if mood:
        conditions.append(json_array_contains(products.c.mood_tags, mood))
    if dietary_restriction:
        # allergen nahi hone condition
        conditions.append(func.instr(products.c.allergens, dietary_restriction) == 0)

    if conditions:
        query = query.where(and_(*conditions))

    rows = await database.fetch_all(query)

    result = []
    for row in rows:
        record = dict(row)
        record['ingredients'] = json.loads(record['ingredients'])
        record['dietary_tags'] = json.loads(record['dietary_tags'])
        record['mood_tags'] = json.loads(record['mood_tags'])
        record['allergens'] = json.loads(record['allergens'])
        result.append(record)

    return result

# Interest scoring factors and logic
ENGAGEMENT_FACTORS = {
    'specific_preferences': 15,
    'dietary_restrictions': 10,
    'budget_mention': 5,
    'mood_indication': 20,
    'question_asking': 10,
    'enthusiasm_words': 8,
    'price_inquiry': 25,
    'order_intent': 30,
}

NEGATIVE_FACTORS = {
    'hesitation': -10,
    'budget_concern': -15,
    'dietary_conflict': -20,
    'rejection': -25,
    'delay_response': -5,
}

# Sample keyword sets for simple intent detection
specific_preferences_keywords = ["spicy", "korean", "burger", "vegetarian", "tacos", "pizza"]
dietary_restrictions_keywords = ["vegetarian", "vegan", "gluten", "allergy", "dairy", "soy"]
budget_keywords = ["under", "below", "less than", "cheap"]
mood_keywords = ["adventurous", "comfort", "indulgent", "healthy"]
question_words = ["how", "what", "when", "where", "is"]
enthusiasm_words = ["amazing", "perfect", "love", "delicious", "great"]
price_inquiries = ["how much", "price", "cost", "$"]
order_intents = ["I'll take it", "add to cart", "order", "buy"]

def simple_interest_score(user_text: str) -> int:
    text = user_text.lower()
    score = 0

    for kw in specific_preferences_keywords:
        if kw in text:
            score += ENGAGEMENT_FACTORS['specific_preferences']
            break

    for kw in dietary_restrictions_keywords:
        if kw in text:
            score += ENGAGEMENT_FACTORS['dietary_restrictions']
            break

    for kw in budget_keywords:
        if kw in text:
            score += ENGAGEMENT_FACTORS['budget_mention']
            break

    for kw in mood_keywords:
        if kw in text:
            score += ENGAGEMENT_FACTORS['mood_indication']
            break

    if any(qw in text for qw in question_words):
        score += ENGAGEMENT_FACTORS['question_asking']

    if any(ew in text for ew in enthusiasm_words):
        score += ENGAGEMENT_FACTORS['enthusiasm_words']

    if any(pi in text for pi in price_inquiries):
        score += ENGAGEMENT_FACTORS['price_inquiry']

    if any(oi in text for oi in order_intents):
        score += ENGAGEMENT_FACTORS['order_intent']

    # Negative factors example checks
    if "maybe" in text or "not sure" in text:
        score += NEGATIVE_FACTORS['hesitation']
    if "too expensive" in text or "pricey" in text:
        score += NEGATIVE_FACTORS['budget_concern']
    if "don't like" in text or "hate" in text:
        score += NEGATIVE_FACTORS['rejection']

    # Clamp score between 0 and 100
    score = max(0, min(100, score))
    return score

class InterestRequest(BaseModel):
    user_text: str

class InterestResponse(BaseModel):
    interest_score: int

@app.post("/interest-score/", response_model=InterestResponse)
async def interest_score(request: InterestRequest):
    score = simple_interest_score(request.user_text)
    return InterestResponse(interest_score=score)

# Simple conversation simulation endpoint
class ConversationRequest(BaseModel):
    user_text: str

class ConversationResponse(BaseModel):
    interest_score: int
    recommended_products: List[Product]

@app.post("/converse/", response_model=ConversationResponse)
async def converse(request: ConversationRequest):
    user_text = request.user_text.lower()
    score = simple_interest_score(user_text)

    # For demo, try to infer category, mood, price from user text and query products
    category = None
    mood = None
    max_price = None

    for cat in ["Burgers", "Pizza", "Fried Chicken", "Tacos & Wraps", "Sides & Appetizers", "Beverages", "Desserts", "Salads & Healthy Options", "Breakfast Items", "Limited Time Specials"]:
        if cat.lower() in user_text:
            category = cat
            break

    for m in ["spicy", "adventurous", "comfort", "indulgent", "healthy"]:
        if m in user_text:
            mood = m
            break

    import re
    price_match = re.search(r"\$?(\d+)", user_text)
    if price_match:
        try:
            max_price = float(price_match.group(1))
        except Exception:
            max_price = None

    # Query products based on detected filters
    products_filtered = await get_products(category=category, max_price=max_price, mood=mood)

    return ConversationResponse(
        interest_score=score,
        recommended_products=products_filtered[:5]  # Return top 5 matches
    )
@app.get("/")
async def root():
    return {"message": "Welcome to FoodieBot API"}

