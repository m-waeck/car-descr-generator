message = """Beschreibe das Auto {car_name} in 4 Sätzen auf Deutsch."""

response = """It is subjective to determine the 'best' French cheese as it largely depends on personal preference. Here are some famous and beloved French cheeses in various categories:

1. Brie: Brie de Meaux or Brie de Melun are popular choices for their velvety texture and mild, buttery flavor.
2. Camembert: Originally from Normandy, Camembert is known for its earthy, pungent aroma and tangy, creamy taste.
3. Roquefort: A blue-veined cheese from the Massif Central region, Roquefort is renowned for its strong, piquant flavor and crumbly texture.
4. Comté: This nutty, slightly sweet cheese from the Franche-Comté region is made from unpasteurized cow's milk and has a firm, yet creamy texture.
5. Munster: Munster is a pungent, smelly, soft-rinded cheese hailing from the Alsace region. Its strong aroma and spicy, piquant flavor are not for the faint-hearted.

Consider trying a few of these cheeses to determine which one suits your taste buds best. Remember, the "best" cheese is the one that brings you the most enjoyment."""

# print(message)

# print(response)

# add message and response together
chat = "Message:\n" + message + """\n---\n""" + "Response:\n" + response



from mistral_api import get_response

# print(get_response("Beschreibe das Auto VW GTI in 4 Sätzen auf Deutsch."))

import toml
 
with open('secrets.toml', 'r') as f:
    config = toml.load(f)
 
# Access values from the config
print(config['mistral']['key'])

