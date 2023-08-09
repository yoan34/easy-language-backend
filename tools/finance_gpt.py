gpt3_input = 0.0015
gpt3_output = 0.002

# On peut dire que 2.000 tokens semble être une bonne base de travail par utilisateur actif par jours.

# A chaque requête imaginons que j'ai un context de 4.000 tokens soit:

request_and_response_price = gpt3_output * 0.118
user_price_per_day = request_and_response_price*50

print(user_price_per_day * 1000)