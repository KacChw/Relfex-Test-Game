import tkinter as tk
from PIL import Image, ImageTk
import random
import time
import threading
import playsound
import matplotlib.pyplot as plt


class TrafficLight:
    def __init__(self, master):
        self.traffic_reaction_label = None
        self.traffic_reaction_label2 = None
        self.traffic_reaction_time = None
        self.sound_reaction_label = None
        self.sound_reaction_time = None
        self.gracz_label = None

        self.points = 0
        self.points_label = None
        self.game_duration = 30  # Czas trwania gry w sekundach
        self.game_timer = None
        self.is_complex_running = False

        self.master = master
        self.master.title("Reaction Time Game")
        self.master.geometry("1500x800")

        image = Image.open("tlo.jpg")
        # Przeskaluj obraz do rozmiaru okna
        width, height = self.master.winfo_width(), self.master.winfo_height()
        image = image.resize((1700, 900))

        # Konwertuj obraz na format obsługiwany przez Tkinter
        photo = ImageTk.PhotoImage(image)

        # Utwórz etykietę (Label), ustaw tło na obraz i umieść w oknie
        self.background_label = tk.Label(self.master, image=photo)
        self.background_label.image = photo  # Zachowaj referencję, aby obraz nie został wyrzucony przez GC
        self.background_label.place(x=0, y=0)

        self.gracz_entry = tk.Entry(master)
        self.gracz_entry.place(x=180, y=100)

        self.canvas = tk.Canvas(self.master, width=150, height=350, bg="black")
        self.canvas.place(x=70, y=150)

        self.okno = tk.Canvas(width=600, height=400, bg="black")
        self.okno.place(x=900, y=130)

        self.wyniki = tk.Canvas(width=600, height=140, bg="lightgrey")
        self.wyniki.place(x=900, y=650)

        # Dodaj pasek przewijania
        self.scrollbar = tk.Scrollbar(self.master, orient=tk.VERTICAL, command=self.wyniki.yview)
        self.scrollbar.place(x=1500, y=650, height=145)

        # Połącz pasek przewijania z oknem Canvas
        self.wyniki.config(yscrollcommand=self.scrollbar.set)

        # Utwórz ramkę w oknie Canvas, która będzie przechowywać wyniki
        self.results_frame = tk.Frame(self.wyniki, bg="lightgrey")
        self.wyniki.create_window((0, 0), window=self.results_frame, anchor="nw")


        self.red_light = self.canvas.create_oval(50, 50, 100, 100, fill="gray")
        self.yellow_light = self.canvas.create_oval(50, 150, 100, 200, fill="gray")
        self.green_light = self.canvas.create_oval(50, 250, 100, 300, fill="gray")

        self.lights = [self.red_light, self.yellow_light, self.green_light]
        self.light_colors = ["red", "yellow", "green"]

        self.current_light = 0

        self.start_button = tk.Button(self.master, text="Start", command=self.start_traffic_light_game)
        self.start_button.place(x=80, y=550)

        self.start_button2 = tk.Button(self.master, text="Start", command=self.start_sound_game)
        self.start_button2.place(x=570, y=550)

        self.complex_game_button = tk.Button(self.master, text="Start", command=self.start_complex_game)
        self.complex_game_button.place(x=1000, y=550)

        self.stat_button = tk.Button(self.master, text="Statystyki", command=lambda: self.statystyki(self.gracz_entry.get()))
        self.stat_button.place(x=630, y=100)

        self.speaker_image = tk.PhotoImage(file="glosnik.png").subsample(5, 5)
        self.speaker_label = tk.Label(master, image=self.speaker_image, bg="white")
        self.speaker_label.place(x=580, y=200)

        self.gracz_entry = tk.Entry(master)
        self.gracz_entry.place(x=180, y=100)

        self.word_index = 0
        self.colors = {"czerwony": "red", "zielony": "green", "niebieski": "blue", "żółty": "yellow", "czarny": "black",
                       "pomarańczowy": "orange"}#, "szary": "gray", "różowy": "pink", "brązowy": "brown",
                       #"fioletowy": "purple"}
        self.color_label = tk.Label(self.okno, text="", font=("Arial", 50,))
        self.color_label.place(relx=0.5, rely=0.5, width=595, height=395, anchor="center")
        self.change_color_word()

        self.master.bind("<space>", self.space_pressed)
        self.master.bind("<Return>", self.check_points)
        #self.master.bind("<Return>", lambda event: self.change_color_word())

        #self.point_awarded = {color: False for color in self.colors}
        self.start_time_sound = None
        self.start_time_light = None
        self.is_running = False
        self.sound_game = False

    import matplotlib.pyplot as plt

    def statystyki(self, nick):
        with open("wyniki.txt", "r") as file:
            lines = file.readlines()

        data = []
        for line in lines:
            nick_entry, reaction_time_traffic, reaction_time_sound, points = line.strip().split()
            data.append((nick_entry, float(reaction_time_traffic), float(reaction_time_sound), int(points)))

        # Wybierz tylko dane dla danego gracza
        player_data = [entry for entry in data if entry[0] == nick]

        if not player_data:
            print("Brak danych dla podanego gracza.")
            return

        # Oblicz średnie czasy reakcji i wynik gracza
        average_reaction_traffic = sum(entry[1] for entry in data) / len(data)
        average_reaction_sound = sum(entry[2] for entry in data) / len(data)
        average_points = sum(entry[3] for entry in data) / len(data)

        player_reaction_traffic = sum(entry[1] for entry in player_data) / len(player_data)
        player_reaction_sound = sum(entry[2] for entry in player_data) / len(player_data)
        player_points = sum(entry[3] for entry in player_data)

        # Wykres
        categories = ["Eye Reaction", "Sound Reaction", "Points"]
        player_values = [player_reaction_traffic, player_reaction_sound, player_points]
        average_values = [average_reaction_traffic, average_reaction_sound, average_points]

        bar_width = 0.35
        index = range(len(categories))

        plt.bar([i - bar_width / 2 for i in index], player_values, bar_width, color='lightblue', label=nick)
        plt.bar([i + bar_width / 2 for i in index], average_values, bar_width, color='green', alpha=0.3,
                label='Średnia')

        plt.xticks(index, categories)
        plt.ylabel('Wartości')
        plt.title('Statystyki gracza w porównaniu ze średnią')

        # Dodaj komentarze w zależności od wyników
        for i in range(len(categories)):
            if categories[i] == "Eye Reaction":
                if player_values[i] < 0.1:
                    plt.text(i - 0.1, player_values[i] + 0.05, "Doskonale! Nadajesz się na kierowcę F1!", fontsize=8,
                             color='black')
                elif player_values[i] < 0.4:
                    plt.text(i - 0.2, player_values[i] + 0.05, "Bardzo szybka reakcja!", fontsize=8, color='black')
                elif player_values[i] < 0.7:
                    plt.text(i - 0.25, player_values[i] + 0.05, "Czas reakcji jest przeciętny", fontsize=8,
                             color='black')
                else:
                    plt.text(i - 0.35, player_values[i] + 0.05, "Czas rakcji wymaga poprawy", fontsize=8,
                             color='black')
            elif categories[i] == "Sound Reaction":
                if player_values[i] < 0.1:
                    plt.text(i + 0.05, player_values[i] + 0.05, "Doskonale! Nadajesz się na kierowcę F1!", fontsize=8,
                             color='black')
                elif player_values[i] < 0.3:
                    plt.text(i + 0.05, player_values[i] + 0.05, "Bardzo szybka reakcja!", fontsize=8, color='black')
                elif player_values[i] < 0.6:
                    plt.text(i + 0.05, player_values[i] + 0.05, "Czas reakcji jest przeciętny", fontsize=8,
                             color='black')
                else:
                    plt.text(i + 0.05, player_values[i] + 0.05, "Reakcja na dźwięk wymaga poprawy", fontsize=8,
                             color='black')

        plt.legend()
        plt.show()

    def top_test_optyczny(self):
        self.wyniki.delete("all")
        with open("wyniki.txt", "r") as file:
            lines = file.readlines()

        # Przetwarzanie danych do postaci, którą można posortować
        data = []
        for line in lines:
            nick, reaction_time_traffic, _, points = line.strip().split()
            data.append((nick, float(reaction_time_traffic), int(points)))

        # Sortowanie danych według czasu reakcji optycznej (reaction_time_traffic)
        sorted_data = sorted(data, key=lambda x: x[1])

        header = "Nick".ljust(15) + "Czas reakcji optycznej [ms]".ljust(30)
        self.wyniki.create_text(10, 10, anchor="nw", text=header, font=("Arial", 10, "bold"))
        for i, (nick, reaction_time_traffic, points) in enumerate(sorted_data, start=0):
            reaction_time_traffic = round(float(reaction_time_traffic) * 1000, 3)
            row = f"{nick.ljust(30)} {reaction_time_traffic:.3f}"
            self.wyniki.create_text(10, 30 + i * 20, anchor="nw", text=row)

    def top_test_audio(self):
        self.wyniki.delete("all")
        with open("wyniki.txt", "r") as file:
            lines = file.readlines()

        data = []
        for line in lines:
            nick, _, reaction_time_sound, points = line.strip().split()
            data.append((nick, float(reaction_time_sound), int(points)))

        # Sortowanie danych według czasu reakcji dźwiękowej (reaction_time_sound)
        sorted_data = sorted(data, key=lambda x: x[1])

        header = "Nick".ljust(15) + "Czas reakcji na dźwięk [ms]".ljust(30)
        self.wyniki.create_text(10, 10, anchor="nw", text=header, font=("Arial", 10, "bold"))
        for i, (nick, reaction_time_sound, points) in enumerate(sorted_data, start=0):
            reaction_time_sound = round(float(reaction_time_sound) * 1000, 3)
            row = f"{nick.ljust(30)} {reaction_time_sound:.3f}"
            self.wyniki.create_text(10, 30 + i * 20, anchor="nw", text=row)

    def top_test_gra(self):
        self.wyniki.delete("all")
        with open("wyniki.txt", "r") as file:
            lines = file.readlines()

        # Przetwarzanie danych do postaci, którą można posortować
        data = []
        for line in lines:
            nick, reaction_time_traffic, reaction_time_sound, points = line.strip().split()
            data.append((nick, float(reaction_time_traffic), float(reaction_time_sound), int(points)))

        # Sortowanie danych według wyniku gry (points)
        sorted_data = sorted(data, key=lambda x: x[3], reverse=True)

        header = "Nick".ljust(15)+  "Wynik"
        self.wyniki.create_text(10, 10, anchor="nw", text=header, font=("Arial", 10, "bold"))
        for i, (nick, reaction_time_traffic, reaction_time_sound, points) in enumerate(sorted_data, start=0):
            row = f"{nick.ljust(25)} {points}"
            self.wyniki.create_text(10, 30 + i * 20, anchor="nw", text=row)

    def zobacz_wyniki(self):
        self.wyniki.delete("all")
        with open("wyniki.txt", "r") as file:
            lines = file.readlines()

        header = "Nick".ljust(15) + "Czas reakcji 1".ljust(30) + "Czas reakcji 2".ljust(30) + "Wynik"
        self.wyniki.create_text(10, 10, anchor="nw", text=header, font=("Arial", 10, "bold"))
        for i, line in enumerate(lines, start=0):
            nick, reaction_time_traffic, reaction_time_sound, points = line.strip().split()
            reaction_time_traffic = round(float(reaction_time_traffic) * 1000, 3)
            reaction_time_sound = round(float(reaction_time_sound) * 1000, 3)
            row = f"{nick.ljust(25)} {reaction_time_traffic:.3f}".ljust(65) + f"{reaction_time_sound:.3f}".ljust(
                50) + f"{points}"
            self.wyniki.create_text(10, 30 + i * 20, anchor="nw", text=row)

        # Aktualizacja paska przewijania
        self.wyniki.config(scrollregion=self.wyniki.bbox("all"))  # Dopasowanie obszaru przewijania
        self.master.update_idletasks()

    def start_complex_game(self):
        if not self.is_complex_running:
            self.is_running = True
            self.sound_game = False
            self.start_button.config(state=tk.DISABLED)
            self.start_button2.config(state=tk.DISABLED)
            self.complex_game_button.config(state=tk.DISABLED)
            self.points = 0
            self.points_label.config(text=f"Punkty: {self.points}")
            self.start_game_timer()
            self.change_color_word()

    def start_game_timer(self):
        self.game_timer = threading.Timer(self.game_duration, self.end_complex_game)
        self.is_complex_running = True

        self.game_timer.start()

    def end_complex_game(self):
        self.is_complex_running = False
        self.start_button.config(state=tk.NORMAL)
        self.start_button2.config(state=tk.NORMAL)
        self.complex_game_button.config(state=tk.NORMAL)
        self.points_label.config(text=f"Koniec gry! Twój wynik: {self.points}")
        self.color_label.config(text="", fg="black", bg="black")  # Zatrzymaj zmianę kolorów po zakończeniu gry

        # Zapisz wynik z nickiem gracza do pliku
        nick = self.gracz_entry.get()
        with open("wyniki.txt", "a") as file:
            file.write(f"{nick} {self.traffic_reaction_time} {self.sound_reaction_time - 0.2} {self.points}\n")

    def change_color_word(self):
        if self.is_complex_running:
            znaczenie_textu = random.choice(list(self.colors.keys()))
            kolor_tla = random.choice(list(self.colors.keys()))
            kolor_textu = random.choice(list(self.colors.keys()))

            while kolor_tla == kolor_textu:
                kolor_tla = random.choice(list(self.colors.keys()))

            self.color_label.config(text=znaczenie_textu, fg=self.colors[kolor_textu],
                                    bg=self.colors[kolor_tla].lower())
            self.master.after(1300, self.change_color_word)

    def check_points(self, event):
        current_color = self.color_label.cget("foreground")
        current_text = self.color_label.cget("text")
        if self.colors[current_text] == current_color:
            self.points += 1
            self.points_label.config(text=f"Punkty: {self.points}")
        else:
            self.points -= 1
            self.points_label.config(text=f"Punkty: {self.points}")

    def start_traffic_light_game(self):
        if not self.is_running:
            self.is_running = True
            self.sound_game = False
            self.start_button.config(state=tk.DISABLED)
            self.change_light()

    def start_sound_game(self):
        if not self.is_running:
            self.is_running = True
            self.sound_game = True
            self.start_button2.config(state=tk.DISABLED)
            threading.Thread(target=self.play_sound_and_measure_reaction_time).start()

    def change_light(self):
        if self.is_running and not self.sound_game:
            # Turn off previous light
            prev_light = (self.current_light - 1) % len(self.lights)
            self.canvas.itemconfig(self.lights[prev_light], fill="gray")

            # Turn on current light
            self.canvas.itemconfig(self.lights[self.current_light], fill=self.light_colors[self.current_light])

            # Move to the next light
            self.current_light = (self.current_light + 1) % len(self.lights)

            if self.current_light == 0:  # If green light
                self.start_time_light = time.time()

            random_time = random.randint(1000, 5000)  # Random time from 1 to 5 seconds
            self.master.after(random_time, self.change_light)

    def play_sound_and_measure_reaction_time(self):
        if self.is_running and self.sound_game:
            # Play sound after a random delay
            random_delay = random.randint(1000, 5000) / 1000  # Random delay between 1 and 5 seconds
            time.sleep(random_delay)

            playsound.playsound("sound.mp3", False)

            # Start measuring reaction time
            self.start_time_sound = time.time()

    def space_pressed(self, event):
        if self.is_running:
            if self.sound_game and self.start_time_sound is not None:
                reaction_time = time.time() - self.start_time_sound
                if reaction_time < 0.0:
                    # Jeśli reakcja nastąpiła za szybko, wyświetl komunikat i zrestartuj test
                    self.sound_reaction_label.config(text="Za szybko! Spróbuj ponownie.")
                    self.start_sound_game()  # Restartuj test dźwiękowy
                    return
                self.sound_reaction_time = reaction_time
                self.sound_reaction_label.config(text="Czas: {:.4f} sekund".format(reaction_time - 0.2))
            elif not self.sound_game and self.start_time_light is not None:
                reaction_time = time.time() - self.start_time_light
                if reaction_time < 0.0:
                    # Jeśli reakcja nastąpiła za szybko, wyświetl komunikat i zrestartuj test
                    self.traffic_reaction_label.config(text="Za szybko! Spróbuj ponownie.")
                    self.start_traffic_light_game()  # Restartuj test świetlny
                    return
                self.traffic_reaction_time = reaction_time
                self.traffic_reaction_label.config(text="Czas: {:.4f} sekund".format(reaction_time))

            self.is_running = False
            self.start_button.config(state=tk.NORMAL)
            self.start_button2.config(state=tk.NORMAL)


def main():
    root = tk.Tk()
    traffic_light = TrafficLight(root)

    traffic_light.traffic_reaction_label = tk.Label(root, text="Czas: ")
    traffic_light.traffic_reaction_label.place(x=80, y=600)
    traffic_light.traffic_reaction_label2 = tk.Label(root, text="Naciśnij 'spacje' po pojawieniu sie zielonego światła! \nKliknij 'start' aby rozpocząć. ")
    traffic_light.traffic_reaction_label2.place(x=120, y=550)

    traffic_light.gracz_label = tk.Label(root, text="Wpisz swoj nick: ")
    traffic_light.gracz_label.place(x=80, y=100)
    traffic_light.wyniki_label = tk.Button(root, text="Wszystkie wyniki ", command=traffic_light.zobacz_wyniki)
    traffic_light.wyniki_label.place(x=310, y=100)
    traffic_light.wyniki_label = tk.Button(root, text="Test optyczny ", command=traffic_light.top_test_optyczny)
    traffic_light.wyniki_label.place(x=420, y=100)
    traffic_light.wyniki_label = tk.Button(root, text="Test audio ", command=traffic_light.top_test_audio)
    traffic_light.wyniki_label.place(x=510, y=100)
    traffic_light.wyniki_label = tk.Button(root, text="Gra  ", command=traffic_light.top_test_gra)
    traffic_light.wyniki_label.place(x=585, y=100)
    # traffic_light.wyniki_label = tk.Button(root, text="Statystyki", command=traffic_light.statystyki)
    # traffic_light.wyniki_label.place(x=630, y=100)



    traffic_light.sound_reaction_label = tk.Label(root, text="Czas: ")
    traffic_light.sound_reaction_label.place(x=570, y=600)
    traffic_light.sound_reaction_label2 = tk.Label(root, text="Naciśnij 'spacje' po usłyszeniu dzwięku! \nKliknij 'start' aby rozpocząć. ")
    traffic_light.sound_reaction_label2.place(x=610, y=550)

    traffic_light.points_label = tk.Label(root, text="Wynik: ")
    traffic_light.points_label.place(x=1000, y=600)
    traffic_light.points_label2 = tk.Label(root,
                                          text="Klikaj 'enter' za każdym razem kiedy kolor tekstu zgadza się z tekstem! \nZa każdą poprawną odpowiedź jest 1 pkt. Za każą złą -1. ")
    traffic_light.points_label2.place(x=1040, y=550)

    root.mainloop()

if __name__ == "__main__":
    main()
