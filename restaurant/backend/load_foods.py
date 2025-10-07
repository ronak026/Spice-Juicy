from backend.models import Category, MenuItem
from backend.data.foods import foods

def load_foods():
    for food in foods:
        category_name = food.get("category", "Uncategorized")
        category, created = Category.objects.get_or_create(name=category_name)

        image_url = food.get("image")
        if not image_url or not image_url.strip():
            image_url = None

        menu_item, created = MenuItem.objects.get_or_create(
            name=food["name"],
            defaults={
                "description": food.get("description", ""),
                "price": food.get("price", 0),
                "category": category,
                "image_url": image_url,
                "available": True,
            },
        )
    print("Food data loaded successfully.")