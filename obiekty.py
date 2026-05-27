
import random
from data import ACHIEVEMENT_NAMES

class BaseAgent:
    """Baza dla wszystkich postaci i wrogów na statku."""
    def __init__(self, identity, hp_pool):
        self.name = identity
        self.health = hp_pool
        self.max_health = hp_pool

    def take_damage(self, dmg_value):
        self.health -= dmg_value
        if self.health < 0:
            self.health = 0

    def heal(self, heal_value):
        self.health += heal_value
        if self.health > self.max_health:
            self.health = self.max_health

    @property
    def alive(self):
        return self.health > 0


class Item:
    """Obiekt ekwipunku, narzędzie lub implant."""
    def __init__(self, name, description, heal=0, damage=0, price=0):
        self.name = name
        self.description = description
        self.heal = heal
        self.damage = damage
        self.price = price


class BlackMarket:
    """Punkt zaopatrzenia technicznego w module startowym."""
    def __init__(self, stock_list):
        self.items = stock_list

    def execute_purchase(self, selection, user_agent):
        if not selection.isdigit():
            print("Terminal zaopatrzenia nie rozumie tego zapytania.")
            return

        pos = int(selection) - 1
        if pos < 0 or pos >= len(self.items):
            print("Brak takiej części w magazynie.")
            return

        target_item = self.items[pos]
        if user_agent.gold >= target_item.price:
            user_agent.gold -= target_item.price
            user_agent.add_item(
                Item(target_item.name, target_item.description, target_item.heal, target_item.damage, target_item.price)
            )
            print("Zainstalowano w ekwipunku kombinezonu:", target_item.name)
        else:
            print("Za mało kredytów na koncie inżyniera.")

    def display_stock(self):
        print("\n=== PUNKT ZAOPATRZENIA ===")
        for idx, item in enumerate(self.items, 1):
            print(f"{idx} - {item.name} ({item.price} kredytow)")
            print(f"    {item.description}")


class HackingJournal:
    """Rejestrator misji i osiągnięć."""
    def __init__(self):
        self.notes = []
        self.achievements = []

    def print_achievements(self):
        print("\n====== STATUS REJESTRU OSIAGNIEC ======")
        for name in ACHIEVEMENT_NAMES:
            status = "[x]" if name in self.achievements else "[ ]"
            print(status, name)
        print("=======================================")

    def unlock_achievement(self, ach_id):
        if ach_id not in self.achievements:
            self.achievements.append(ach_id)
            print("Osiągnięcie zapisane w dzienniku pancerza:", ach_id)

    def print_logs(self):
        if not self.notes:
            print("Brak zarejestrowanych wpisów w czarnej skrzynce.")
            return
        print("\n====== CZARNA SKRZYNKA STATKU ======")
        for log in self.notes:
            print("-", log)
        print("====================================")

    def record_log(self, text_log):
        if text_log not in self.notes:
            self.notes.append(text_log)


class SystemClock:
    """Zegar procesów pokładowych i warunków środowiskowych."""
    def __init__(self):
        self.day = 1
        self.weather = "pochmurno"

    def update_network_status(self):
        roll = random.randint(1, 5)
        if roll == 1:
            self.weather = "slonce"
        elif roll == 2:
            self.weather = "deszcz"
        elif roll == 3:
            self.weather = "wiatr"
        elif roll == 4:
            self.weather = "pochmurno"
        else:
            self.weather = "dym"

    def advance_cycle(self):
        self.day += 1
        self.update_network_status()


class Enemy(BaseAgent):
    """Zbuntowane drony i systemy zabezpieczeń statku."""
    def __init__(self, identity, hp_pool, base_dmg, reward_gold, reward_xp):
        super().__init__(identity, hp_pool)
        self.damage = base_dmg
        self.gold = reward_gold
        self.exp = reward_xp

    def execute_attack(self):
        return random.randint(1, self.damage)


class Netrunner(BaseAgent):
    """Inżynier eksplorujący wrak statku."""
    def __init__(self, alias):
        super().__init__(alias, 25)
        self.gold = 0
        self.level = 1
        self.exp = 0
        self.rested = False
        self.herbs = 0
        self.reputation = 0
        self.training = 0
        self.defense = 0
        self.inventory = []
        self.current_room = None
        self.journal = HackingJournal()

    def print_hardware(self):
        if not self.inventory:
            print("Twoje kieszenie narzędziowe są całkowicie puste.")
            return
        print("\nWyposażenie kombinezonu:")
        for item in self.inventory:
            info = f"- {item.name}: {item.description}"
            if item.damage > 0:
                info += f" (modyfikator broni +{item.damage})"
            if item.heal > 0:
                info += f" (stymulant medyczny {item.heal} hp)"
            print(info)

    def process_xp(self, xp_amount):
        self.exp += xp_amount
        print("Przetworzono dane telemetryczne:", xp_amount, "EXP.")
        if self.exp >= 10:
            self.level += 1
            self.exp -= 10
            self.max_health += 5
            self.health = self.max_health
            print("Zaktualizowano systemy kombinezonu do Wersji", self.level)
            print("Maksymalna integralność pancerza wzrosła do", self.max_health)

    def add_item(self, item_obj):
        self.inventory.append(item_obj)

    def add_note(self, text):
        self.journal.record_log(text)

    def show_notes(self):
        self.journal.print_logs()

    def add_achievement(self, code):
        self.journal.unlock_achievement(code)

    def show_achievements(self):
        self.journal.print_achievements()


class GridNode:
    """Sektor lub moduł statku kosmicznego."""
    def __init__(self, node_title, description_text):
        self.name = node_title
        self.description = description_text
        self.items = []
        self.enemy = None
        self.exits = {}
        self.locked = False
        self.visited = False

    def render_node(self):
        print("\n==========")
        print(self.name)
        print(self.description)
        if not self.visited:
            print("[System]: Zmapowano nowy obszar pokładu USS Horizon.")
            self.visited = True
        if self.enemy and self.enemy.alive:
            print("Wykryto wrogi mechanizm obronny:", self.enemy.name)
        if self.items:
            print("Przedmioty / Komponenty w zasięgu wzroku:")
            for item in self.items:
                print("-", item.name)
        print("Dostępne korytarze / śluzy:")
        for destination in self.exits:
            print("-", destination)
        print("==========")




# import random

# from data import ACHIEVEMENT_NAMES


# class Entity:
#     def __init__(self, name, health):
#         self.name = name
#         self.health = health
#         self.max_health = health

#     @property
#     def alive(self):
#         return self.health > 0

#     def take_damage(self, damage):
#         self.health -= damage

#         if self.health < 0:
#             self.health = 0

#     def heal(self, amount):
#         self.health += amount

#         if self.health > self.max_health:
#             self.health = self.max_health


# class Item:
#     def __init__(self, name, description, heal=0, damage=0, price=0):
#         self.name = name
#         self.description = description
#         self.heal = heal
#         self.damage = damage
#         self.price = price


# class Shop:
#     def __init__(self, items):
#         self.items = items

#     def show(self):
#         print("\n=== SKLEP ===")

#         number = 1

#         for item in self.items:
#             print(str(number) + " - " + item.name + " (" + str(item.price) + " zlota)")
#             print("    " + item.description)
#             number += 1

#     def buy(self, choice, player):
#         if not choice.isdigit():
#             print("Kupiec nie wie, o co prosisz.")
#             return

#         index = int(choice) - 1

#         if index < 0 or index >= len(self.items):
#             print("Nie ma takiego towaru.")
#             return

#         item = self.items[index]

#         if player.gold >= item.price:
#             player.gold -= item.price
#             player.add_item(
#                 Item(item.name, item.description, item.heal, item.damage, item.price)
#             )
#             print("Kupiono:", item.name)
#         else:
#             print("Za malo zlota.")


# class Journal:
#     def __init__(self):
#         self.notes = []
#         self.achievements = []

#     def add_note(self, note):
#         if note not in self.notes:
#             self.notes.append(note)

#     def show_notes(self):
#         if len(self.notes) == 0:
#             print("Nie masz jeszcze zadnych notatek.")
#             return

#         print("\n====== NOTATKI ======")

#         for note in self.notes:
#             print("-", note)

#         print("=====================")

#     def add_achievement(self, name):
#         if name not in self.achievements:
#             self.achievements.append(name)
#             print("Osiagniecie:", name)

#     def show_achievements(self):
#         print("\n====== OSIAGNIECIA ======")

#         for name in ACHIEVEMENT_NAMES:
#             if name in self.achievements:
#                 print("[x]", name)
#             else:
#                 print("[ ]", name)

#         print("=========================")


# class GameClock:
#     def __init__(self):
#         self.day = 1
#         self.weather = "pochmurno"

#     def next_day(self):
#         self.day += 1
#         self.change_weather()

#     def change_weather(self):
#         roll = random.randint(1, 5)

#         if roll == 1:
#             self.weather = "slonce"
#         elif roll == 2:
#             self.weather = "deszcz"
#         elif roll == 3:
#             self.weather = "wiatr"
#         elif roll == 4:
#             self.weather = "pochmurno"
#         else:
#             self.weather = "dym"


# class Enemy(Entity):
#     def __init__(self, name, health, damage, gold, exp):
#         super().__init__(name, health)
#         self.damage = damage
#         self.gold = gold
#         self.exp = exp

#     def attack(self):
#         return random.randint(1, self.damage)


# class Player(Entity):
#     def __init__(self, name):
#         super().__init__(name, 25)

#         self.gold = 0
#         self.level = 1
#         self.exp = 0
#         self.rested = False
#         self.herbs = 0
#         self.reputation = 0
#         self.training = 0
#         self.defense = 0

#         self.inventory = []
#         self.current_room = None
#         self.journal = Journal()

#     def add_item(self, item):
#         self.inventory.append(item)

#     def show_inventory(self):
#         if len(self.inventory) == 0:
#             print("Ekwipunek jest pusty.")
#             return

#         print("\nEkwipunek:")

#         for item in self.inventory:
#             text = "- " + item.name + ": " + item.description

#             if item.damage > 0:
#                 text += " (obrazenia +" + str(item.damage) + ")"

#             if item.heal > 0:
#                 text += " (leczenie " + str(item.heal) + " hp)"

#             print(text)

#     def gain_exp(self, amount):
#         self.exp += amount
#         print("Zdobywasz", amount, "EXP.")

#         if self.exp >= 10:
#             self.level += 1
#             self.exp -= 10
#             self.max_health += 5
#             self.health = self.max_health

#             print("Awansowales na poziom", self.level)
#             print("Twoje maksymalne zdrowie wzroslo do", self.max_health)

#     def add_note(self, note):
#         self.journal.add_note(note)

#     def show_notes(self):
#         self.journal.show_notes()

#     def add_achievement(self, name):
#         self.journal.add_achievement(name)

#     def show_achievements(self):
#         self.journal.show_achievements()


# class Room:
#     def __init__(self, name, description):
#         self.name = name
#         self.description = description

#         self.items = []
#         self.enemy = None
#         self.exits = {}
#         self.locked = False
#         self.visited = False

#     def show(self):
#         print("\n==========")
#         print(self.name)
#         print(self.description)

#         if not self.visited:
#             print("Czujesz, ze to miejsce ma swoja tajemnice.")
#             self.visited = True

#         if self.enemy and self.enemy.alive:
#             print("Widzisz przeciwnika:", self.enemy.name)

#         if len(self.items) > 0:
#             print("Przedmioty:")

#             for item in self.items:
#                 print("-", item.name)

#         print("Wyjscia:")

#         for exit_name in self.exits:
#             print("-", exit_name)

#         print("==========")
