
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




