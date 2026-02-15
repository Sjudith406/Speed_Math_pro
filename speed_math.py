import random
import time
import threading
import json
import os
import tkinter as tk
from tkinter import messagebox

# Import de pygame pour la musique avec gestion d'erreur propre
PYGAME_AVAILABLE = False
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    pass

# ==========================================
# GESTION DES SCORES (Persistance JSON)
# ==========================================
class ScoreManager:
    def __init__(self, filename="scores.json"):
        # Chemin absolu pour garantir que le fichier reste au même endroit
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.filename = os.path.join(base_dir, filename)

    def is_username_taken(self, username):
        """Vérifie si le pseudo existe déjà dans le fichier de scores."""
        data = self.load_scores()
        return username in data

    def save_score(self, username, score):
        """Sauvegarde le record de l'utilisateur."""
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
            print(f"Erreur lors de la sauvegarde : {e}")

    def load_scores(self):
        """Charge les données du fichier JSON."""
        if not os.path.exists(self.filename):
            return {}
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                content = f.read()
                if not content:
                    return {}
                return json.loads(content)
        except (json.JSONDecodeError, Exception) as e:
            print(f"Erreur lors de la lecture des scores : {e}")
            return {}

    def get_top_scores(self, limit=10):
        """Retourne les meilleurs scores triés."""
        scores = self.load_scores()
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_scores[:limit]

# ==========================================
# GESTION DU SON (Programmation Concurrente)
# ==========================================
class MusicPlayer:
    def __init__(self):
        self.enabled = PYGAME_AVAILABLE
        if self.enabled:
            try:
                pygame.mixer.init()
            except Exception as e:
                print(f"Système audio non disponible : {e}")
                self.enabled = False

    def play_background_music(self):
        """Lance la musique de fond si le fichier existe."""
        if self.enabled:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            music_path = os.path.join(base_dir, "background_music.mp3")
            
            if os.path.exists(music_path):
                try:
                    pygame.mixer.music.load(music_path)
                    pygame.mixer.music.play(-1)
                except Exception as e:
                    print(f"Erreur audio : {e}")

    def stop_music(self):
        """Arrête la musique proprement."""
        if self.enabled:
            try:
                pygame.mixer.music.stop()
            except:
                pass

# ==========================================
# MOTEUR DU JEU (Logique Métier)
# ==========================================
class GameEngine:
    def __init__(self):
        self.score = 0
        self.current_question = ""
        self.current_answer = 0
        self.hint = "" 

    def generate_question(self):
        """Génère un nouveau calcul avec difficulté progressive."""
        ops = ['+', '-', '*']
        op = random.choice(ops)
        level = 10 + (self.score // 2) * 5
        a = random.randint(1, level)
        b = random.randint(1, level)
        
        self.current_question = f"{a} {op} {b}"
        self.current_answer = eval(self.current_question)
        self.hint = ""

        # Indice pour les multiplications complexes (ex: 23 * 12)
        if op == '*' and a >= 10 and b >= 10:
            dizaine_b = (b // 10) * 10
            unite_b = b % 10
            if unite_b != 0:
                self.hint = f"Indice : ({a} × {dizaine_b}) + ({a} × {unite_b})"
            else:
                self.hint = f"Indice : C'est {a} × {dizaine_b//10} avec un zéro à la fin !"

        return self.current_question

    def check_answer(self, user_answer):
        """Vérifie la réponse utilisateur."""
        try:
            if int(user_answer) == self.current_answer:
                self.score += 1
                return True
            return False
        except ValueError:
            return False

# ==========================================
# GESTION DU TIMER (Thread séparé)
# ==========================================
class TimerThread(threading.Thread):
    def __init__(self, duration, callback_tick, callback_timeout):
        threading.Thread.__init__(self)
        self.duration = duration
        self.remaining = duration
        self.callback_tick = callback_tick
        self.callback_timeout = callback_timeout
        self.running = True
        self.daemon = True

    def run(self):
        while self.running and self.remaining > 0:
            time.sleep(0.1)
            self.remaining -= 0.1
            self.callback_tick(self.remaining)
            
        if self.running and self.remaining <= 0:
            self.callback_timeout()

    def stop(self):
        self.running = False

# ==========================================
# INTERFACE GRAPHIQUE (IHM - Tkinter)
# ==========================================
class GuiApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Speed Math Pro - Officiel")
        self.root.geometry("600x750")
        self.root.configure(bg="#2c3e50")
        
        self.engine = GameEngine()
        self.manager = ScoreManager()
        self.music = MusicPlayer()
        self.timer_thread = None
        
        self.game_mode = "simple"
        self.username = tk.StringVar()
        self.user_answer = tk.StringVar()
        self.question_text = tk.StringVar(value="Prêt ?")
        self.score_text = tk.StringVar(value="Score: 0")
        self.timer_text = tk.StringVar(value="15.0s")

        self.setup_ui()

    def setup_ui(self):
        """Écran d'accueil du jeu."""
        self.clear_screen()
        container = tk.Frame(self.root, bg="#2c3e50")
        container.pack(expand=True)

        tk.Label(container, text="SPEED MATH", font=("Verdana", 32, "bold"), fg="#f1c40f", bg="#2c3e50").pack(pady=30)
        
        tk.Label(container, text="Entre ton pseudo :", fg="white", bg="#2c3e50", font=("Arial", 12)).pack()
        entry_name = tk.Entry(container, textvariable=self.username, justify='center', font=("Arial", 14), 
                             bg="#0f3460", fg="white", insertbackground="white", width=20)
        entry_name.pack(pady=10)

        tk.Label(container, text="Mode de jeu :", fg="#ffffff", bg="#2c3e50", font=("Arial", 12, "bold")).pack(pady=15)
        
        btn_frame = tk.Frame(container, bg="#2c3e50")
        btn_frame.pack()

        tk.Button(btn_frame, text="Simple\n(Entraînement)", command=lambda: self.pre_start_game("simple"), 
                  bg="#0f3460", fg="white", font=("Arial", 10, "bold"), width=15, height=3).grid(row=0, column=0, padx=10)
        
        tk.Button(btn_frame, text="Challenge\n(15s)", command=lambda: self.pre_start_game("challenge"), 
                  bg="#e94560", fg="white", font=("Arial", 10, "bold"), width=15, height=3).grid(row=0, column=1, padx=10)
        
        tk.Button(container, text=" Classement mondial (:", command=self.show_scores, 
                  bg="#2c3e50", fg="#95a5a6", bd=0, cursor="hand2", font=("Arial", 15, "underline")).pack(pady=25)

    def pre_start_game(self, mode):
        """Vérifie la disponibilité du pseudo avant de lancer le jeu."""
        name = self.username.get().strip()
        if not name:
            messagebox.showwarning("Attention", "Veuillez entrer un pseudo !")
            return
        
        if self.manager.is_username_taken(name):
            messagebox.showerror("Pseudo déjà pris", 
                                 f"Le pseudo '{name}' est déjà utilisé.\nChoisis un autre nom pour ton record !")
            return

        self.start_game(mode)

    def start_game(self, mode):
        """Lance l'interface de jeu active."""
        self.game_mode = mode
        self.engine = GameEngine()
        self.music.play_background_music()
        self.clear_screen()
        
        # Barre de score
        tk.Label(self.root, textvariable=self.score_text, fg="#4ecca3", bg="#1a1a2e", font=("Arial", 16, "bold")).pack(pady=15)
        
        if self.game_mode == "challenge":
            self.timer_label = tk.Label(self.root, textvariable=self.timer_text, font=("Courier", 30, "bold"), 
                                       fg="#f1c40f", bg="#2c3e50")
            self.timer_label.pack(pady=5)
        else:
            tk.Label(self.root, text="Mode Entraînement", fg="#7f8c8d", bg="#2c3e50", font=("Arial", 10, "italic")).pack()
        
        # Zone de calcul
        tk.Label(self.root, textvariable=self.question_text, fg="white", bg="#2c3e50", font=("Arial", 56, "bold")).pack(pady=30)
        
        # Bouton Indice (caché par défaut)
        self.hint_button = tk.Button(self.root, text=" VOIR L'INDICE", command=self.show_hint, 
                                    bg="#533483", fg="white", font=("Arial", 10, "bold"), padx=10)
        
        # Zone de saisie
        self.entry = tk.Entry(self.root, textvariable=self.user_answer, font=("Arial", 40), justify='center', 
                             width=8, bg="#16213e", fg="white", insertbackground="white", bd=2)
        self.entry.pack(pady=20)
        self.entry.bind('<Return>', lambda e: self.check_action())
        self.entry.focus_set()
        
        # Contrôles
        tk.Button(self.root, text="VALIDER", command=self.check_action, bg="#4ecca3", fg="#1a1a2e", 
                  font=("Arial", 16, "bold"), width=20, height=2).pack(pady=10)
        
        tk.Button(self.root, text="Quitter la partie", command=self.quit_game, bg="#1a1a2e", 
                  fg="#e94560", bd=0, font=("Arial", 10)).pack(side="bottom", pady=20)

        self.next_question()

    def show_hint(self):
        if self.engine.hint:
            messagebox.showinfo("Coup de pouce", self.engine.hint)
        self.entry.focus_set()

    def next_question(self):
        if self.timer_thread:
            self.timer_thread.stop()
            
        self.engine.generate_question()
        self.question_text.set(self.engine.current_question)
        self.user_answer.set("")
        self.score_text.set(f"Score: {self.engine.score}")
        
        # Gestion dynamique du bouton indice
        if self.engine.hint:
            self.hint_button.pack(pady=5)
        else:
            self.hint_button.pack_forget()
        
        if self.game_mode == "challenge":
            self.timer_thread = TimerThread(15.0, self.update_timer_ui, self.timeout_event)
            self.timer_thread.start()

    def update_timer_ui(self, remaining):
        if remaining > 7: color = "#4ecca3"
        elif remaining > 3: color = "#f1c40f"
        else: color = "#e94560"
        self.timer_text.set(f"{max(0, remaining):.1f}s")
        if hasattr(self, 'timer_label'):
            self.timer_label.config(fg=color)

    def timeout_event(self):
        self.root.after(0, lambda: self.game_over("TEMPS ÉCOULÉ !"))

    def check_action(self):
        if self.engine.check_answer(self.user_answer.get()):
            self.next_question()
        else:
            self.game_over(f"ERREUR !\nLa réponse était {self.engine.current_answer}")

    def game_over(self, reason):
        if self.timer_thread: self.timer_thread.stop()
        self.music.stop_music()
        self.manager.save_score(self.username.get(), self.engine.score)
        messagebox.showinfo("Partie terminée", f"{reason}\nScore final : {self.engine.score}")
        self.setup_ui()

    def quit_game(self):
        if self.timer_thread: self.timer_thread.stop()
        self.music.stop_music()
        self.setup_ui()

    def show_scores(self):
        scores = self.manager.get_top_scores()
        if not scores:
            messagebox.showinfo("Classement", "Aucun record enregistré.")
            return
        text = " LES MEILLEURS SCORES :\n\n"
        for i, (u, s) in enumerate(scores, 1):
            text += f"{i}. {u} — {s} points\n"
        messagebox.showinfo("Leaderboard", text)

    def clear_screen(self):
        for w in self.root.winfo_children(): w.destroy()

# ==========================================
# LANCEMENT
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    # Empêcher le redimensionnement pour garder l'interface propre
    root.resizable(False, False)
    app = GuiApplication(root)
    root.mainloop()