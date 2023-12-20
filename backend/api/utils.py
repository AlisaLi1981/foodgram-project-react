from io import StringIO


def generate_shopping_list(ingredients_dict):
    shopping_list_text = StringIO()

    for ingredient_name, details in ingredients_dict.items():
        quantity = details['quantity']
        unit = details['unit']
        shopping_list_text.write(
            f'{ingredient_name} ({unit}) — {quantity}\n'
        )

    return shopping_list_text.getvalue()
