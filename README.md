# BelloBot

## Un bot discord avec de l'IA qui répond



##### Présentations :

BelloBot est un bot discord qui répond quand on le ping. Il marche avec une API gratuite du nom de huggingface, avec le modèle Llama-3.1-8B-Instruct car plus rapide. Il est juste capable de parler pour l'instant.



##### Comment le mettre sur mon serveur :

-Créer un .env tel que .env.example avec une clé API hugging face obtenable gratuitement sur https://huggingface.co/settings/tokens (pensez à cocher Make calls to Inference Providers, Make calls to your Inference Endpoints et Manage your Inference Endpoints) avec la clé API d'un bot discord que vous avez créé.
-Installer les dépendances nécessaires de requirements.txt (huggingface-hub, python-dotenv et discord)

-L'inviter sur votre serveur avec  le droit d'envoyer des messages dnas les salons et les fils



##### Vie privée :

Attention, le bot gardera en mémoire **TOUT** ce que n'importe qui dit dans n'importe salon du serveur. Les messages sont enregistrés dans messages.txt. Vous êtes prévenus.



