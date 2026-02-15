import random
import time
import json
import os

# ==========================================
# GESTION DES SCORES (Partagé avec la GUI)
# ==========================================
class ScoreManager:
    def __init__(self, filename="scores.json"):
        # On utilise le même fichier que la version graphique
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.filename = os.path.join(base_dir, filename)

    def is_username_taken(self, username):
        """Vérifie si le pseudo existe déjà."""
        data = self.load_scores()
        return username in data

    def save_score(self, username, score):
        """Sauvegarde le meilleur score de l'utilisateur."""
        data = self.load_scores()
        if username in data:
            if score > data[username]:
                data[username] = score
        else:
            data[username] = score

        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur de sauvegarde : {e}")

    def load_scores(self):
        """Charge les scores depuis le JSON."""
        if not os.path.exists(self.filename):
            return {}
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                content = f.read()
                if not content: return {}
                return json.loads(content)
        except:
            return {}

# ==========================================
# MOTEUR DE JEU (Logique de calcul)
# ==========================================
class GameEngine:
    def __init__(self):
        self.score = 0
        self.hint = ""

    def generate_question(self):
        """Crée un calcul et génère un indice si c'est complexe."""
        ops = ['+', '-', '*']
        op = random.choice(ops)
        level = 10 + (self.score // 2) * 5
        a = random.randint(1, level)
        b = random.randint(1, level)
        
        question = f"{a} {op} {b}"
        answer = eval(question)
        self.hint = ""

        # Détection des multiplications complexes pour l'indice
        if op == '*' and a >= 10 and b >= 10:
            dizaine_b = (b // 10) * 10
            unite_b = b % 10
            if unite_b != 0:
                self.hint = f"Indice : ({a} × {dizaine_b}) + ({a} × {unite_b})"
            else:
                self.hint = f"Indice : {a} × {dizaine_b//10} et ajoute un zéro."

        return question, answer

# ==========================================
# BOUCLE PRINCIPALE (Programmation Procédurale)
# ==========================================
def run_game():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("="*40)
    print("      SPEED MATH - VERSION CONSOLE")
    print("="*40)

    manager = ScoreManager()
    engine = GameEngine()

    # Phase d'inscription avec vérification
    while True:
        name = input("\nEntrez votre pseudo : ").strip()
        if not name:
            print(" Le pseudo ne peut pas être vide.")
            continue
        
        if manager.is_username_taken(name):
            print(f"! Le pseudo '{name}' est déjà pris. Veuillez en choisir un autre.")
        else:
            break

    print(f"\nBienvenue {name} ! La partie commence.")
    print("Astuce : Tapez 'q' pour abandonner.\n")

    # Boucle de jeu
    while True:
        question_str, correct_answer = engine.generate_question()
        
        print("-" * 20)
        print(f"Calcul : {question_str}")
        if engine.hint:
            print(f" {engine.hint}")
        
        user_input = input("Votre réponse : ").strip()

        if user_input.lower() == 'q':
            print("\nAbandon de la partie.")
            break

        try:
            if int(user_input) == correct_answer:
                engine.score += 1
                print(f" Correct ! Score actuel : {engine.score}")
            else:
                print(f" Erreur ! La réponse était {correct_answer}")
                break
        except ValueError:
            print("⚠️ Veuillez entrer un nombre valide.")

    # Fin de partie et sauvegarde
    print("\n" + "="*40)
    print(f"PARTIE TERMINÉE, {name.upper()} !")
    print(f"Votre score : {engine.score}")
    manager.save_score(name, engine.score)
    print("="*40)
    
    # Affichage du Top 5
    print("\n CLASSEMENT ACTUEL :")
    scores = manager.load_scores()
    top_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
    for i, (u, s) in enumerate(top_scores, 1):
        print(f"{i}. {u} : {s} pts")

if __name__ == "__main__":
    run_game()