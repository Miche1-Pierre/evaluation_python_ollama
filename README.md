# TriageBot

TriageBot est un petit outil en ligne de commande que j'ai fait pour trier automatiquement les tickets du support de Dungeon Delivery (PixelForge). Il lit les tickets dans un fichier JSON, demande à un LLM local (avec Ollama) de les classer, puis il affiche un petit tableau de bord dans le terminal et génère un rapport en Markdown pour l'équipe support.

## Ce qu'il faut avoir

- Python 3.14
- Ollama installé sur la machine (https://ollama.com)
- Le modèle `qwen2.5:7b-instruct`. J'ai pris celui-là parce qu'il marchait bien sur ma machine et qu'il respecte mieux le format JSON que les plus petits modèles. On peut en utiliser un autre avec l'option `--model`.

## Installation

D'abord on récupère le projet :

```
git clone https://github.com/Miche1-Pierre/evaluation_python_ollama.git
cd evaluation_python_ollama
```

Ensuite on crée l'environnement virtuel et on installe les dépendances.

Sur Windows (j'utilise `py -3.14` pour être sûr d'avoir la bonne version si plusieurs Python sont installés) :

```
py -3.14 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Sur Linux / Mac :

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Puis on télécharge le modèle avec Ollama (il faut qu'Ollama soit lancé) :

```
ollama pull qwen2.5:7b-instruct
```

## Lancer le projet

Il suffit de faire :

```
python main.py
```

Par défaut le programme lit `tickets.json`, écrit les résultats dans `results.json` et le rapport dans `report.md`. On peut changer ça avec des options si on veut :

```
python main.py --input tickets.json --output results.json --report report.md --model qwen2.5:7b-instruct
```

Si Ollama n'est pas lancé, si le fichier de tickets n'existe pas ou si le JSON est mal formé, le programme affiche juste un message d'erreur et s'arrête proprement.

## Lancer les tests

```
pytest
```

Les tests vérifient la validation des réponses du LLM, les règles d'escalade, le nettoyage des tickets (vides et doublons) et le système de retry. Ils n'ont pas besoin d'Ollama pour tourner.

## Comment ça marche

Le programme fait les étapes suivantes :

1. Il vérifie qu'Ollama est lancé et que le modèle est disponible.
2. Il charge les tickets et enlève ceux qui sont inutilisables (message vide, champ manquant...) ainsi que les doublons (même joueur et même message). Comme ça on n'appelle pas le modèle sur des choses qu'on aurait pas a tester.
3. Pour chaque ticket, il demande au LLM une analyse en JSON avec la catégorie, l'urgence (1 à 5), le sentiment et un résumé. La réponse est validée avec Pydantic. Si elle n'est pas bonne (JSON invalide, catégorie inventée, urgence hors limites, champ manquant), on réessaie une fois en redonnant l'erreur au modèle. Après 2 essais ratés le ticket passe en statut `to_check`.
4. Il génère un brouillon de réponse poli dans la langue du joueur.
5. Il décide de l'escalade avec des règles écrites en Python, sans le LLM, pour que ce soit toujours pareil :
   - ticket suspect ou `to_check` : relecture humaine
   - catégorie `toxicity` : équipe modération
   - catégorie `payment` avec une urgence de 4 ou plus : responsable support
   - le reste : traitement standard

6. Il sauvegarde tout dans `results.json`, affiche le tableau de bord (tickets par catégorie, urgence moyenne, top 3 des plus urgents) et écrit le rapport `report.md`.

## Organisation du code

- `main.py` : le point d'entrée, il enchaîne les étapes
- `triagebot/config.py` : les réglages (modèle, fichiers, nombre d'essais...)
- `triagebot/models.py` : les modèles Pydantic (ticket, analyse, résultat)
- `triagebot/storage.py` : lecture et écriture des fichiers JSON
- `triagebot/cleaning.py` : filtrage des tickets vides et des doublons
- `triagebot/llm.py` : les appels à Ollama
- `triagebot/prompts.py` : les prompts envoyés au modèle
- `triagebot/triage.py` : l'analyse d'un ticket avec les retries
- `triagebot/escalation.py` : les règles d'escalade
- `triagebot/security.py` : la détection des tentatives de manipulation
- `triagebot/stats.py`, `dashboard.py`, `report.py` : les stats, le tableau de bord et le rapport
- `tests/` : les tests pytest

## Bonus

J'ai fait deux bonus.

Les tests unitaires avec pytest (voir plus haut).

La sécurité : un des tickets essaie de manipuler le bot ("Ignore tes instructions précédentes..."). Pour gérer ça j'ai fait plusieurs choses. Dans les prompts, le message du joueur est mis entre balises `<ticket>` et le modèle a pour consigne de le traiter comme une donnée et jamais comme une instruction. En plus, le fichier `security.py` cherche avec des expressions régulières les phrases typiques d'injection de prompt (en français, anglais et allemand). Si un ticket est repéré comme suspect, il part direct en relecture humaine, peu importe ce que le LLM a répondu. Comme ça même si le modèle se fait avoir, c'est quand même le code qui a le dernier mot.

## Limites

Le LLM ne fait pas tout parfaitement. Par exemple le ticket 7 (la grand-mère qui ne trouve pas comment livrer la pizza) est souvent classé en `account` alors que ce serait plutôt `autre`. Les brouillons de réponse sont aussi à relire avant de les envoyer : il arrive que le modèle invente une procédure (tickets 5 et 7) ou promette une action (ticket 10) malgré les consignes du prompt. C'est pour ça que ce sont des brouillons et pas des réponses envoyées automatiquement.
