import random
from data import QUEST_HINTS, ROOM_DETAILS, STORY_CHAPTERS, TRAVEL_RUMORS
from obiekty import Enemy, SystemClock, Item, Netrunner, GridNode, BlackMarket

class Game:
    def __init__(self):
        self.player = Netrunner("Inżynier")
        self.rooms = {}
        self.quest_done = False
        self.clock = SystemClock()
        self.rumor_index = 0
        self.chronicle_read = 0
        self.village_helped = False
        self.river_blessed = False
        self.secret_counter = 0
        self.running = True
        
        self.build_cyber_grid()
        self.setup_command_map()

    def terminate_session(self):
        self.running = False

    def view_status(self):
        print("\n====== METRYKI KOMBINEZONU ======")
        print("Integralność:", self.player.health, "/", self.player.max_health)
        print("Poziom Modułów:", self.player.level)
        print("EXP Telemetrii:", self.player.exp, "/ 10")
        print("Kredyty:", self.player.gold)
        print("Sektor statku:", self.player.current_room.name)
        print("================================")

    def display_help(self):
        print("""
Dostępne komendy pokładowe:
rusz [kierunek]
podnies [przedmiot]
atak
uzyj [przedmiot]
obejrzyj [przedmiot]
ekwipunek
status
regeneruj
rozmawiaj
sklep
mapa
logi [numer]
plotki
skanuj
zbierz
rejestr
misje [nazwa]
cwiczenia
pomoz
dni
czekaj
osiagniecia
wyjdz
        """)

    def access_market(self):
        if self.player.current_room.name != "Moduł Startowy":
            print("Punkt zaopatrzenia dostępny jest tylko w module startowym.")
            return
        self.market_terminal.display_stock()
        input_choice = input("> ")
        self.market_terminal.execute_purchase(input_choice, self.player)

    def query_npc(self):
        node_id = self.player.current_room.name
        if node_id == "Moduł Startowy":
            print("Ranny nawigator mówi: Karta dostępu do śluzy reaktora jest w magazynie bezpieczeństwa.")
            print("Dodaje: Moduł widokowy nad śluzą odpadów skrywa energię do wzmocnienia tarcz.")
        elif node_id == "Warsztat":
            print("Na ekranie warsztatu błyszczy komunikat: Kto idzie do reaktora, niech szuka tytanu.")
        elif node_id == "Moduł Widokowy":
            print("Komputer pokładowy nadaje cicho: Logika bez odwagi w próżni staje się bezużyteczna.")
        else:
            print("Cisza radiowa. Nie ma tu nikogo z kim można nawiązać kontakt.")

    def get_time_metrics(self):
        print("\n====== PARAMETRY SYSTEMOWE ======")
        print("Cykl Misji:", self.clock.day)
        print("Stan Atmosfery:", self.clock.weather)
        print("Zaufanie Załogi:", self.player.reputation)
        print("Zgromadzony Złom:", self.player.herbs)
        print("=================================")

    def player_has_token(self, token_name):
        return any(x.name == token_name for x in self.player.inventory)

    def download_item(self, item_id):
        active_node = self.player.current_room
        for existing_item in active_node.items:
            if existing_item.name == item_id:
                self.player.add_item(existing_item)
                active_node.items.remove(existing_item)
                print("Zabezpieczono i schowano:", existing_item.name)
                if existing_item.name == "klejnot":
                    print("Rdzeń lekko wibruje, emitując potężne ciepło w dłoniach.")
                return
        print("Nie ma tu takiego przedmiotu ani podzespołu.")

    def deploy_item(self, item_id):
        for slot in self.player.inventory:
            if slot.name == item_id:
                if slot.heal > 0:
                    self.player.heal(slot.heal)
                    print("Wstrzyknięto stymulant. Przywrócono", slot.heal, "hp.")
                    self.player.inventory.remove(slot)
                    return
                print("Tego narzędzia nie da się użyć w ten sposób.")
                return
        print("Nie posiadasz takiego przedmiotu w kieszeniach kombinezonu.")

    def analyze_target(self, item_id):
        for obj in self.player.inventory:
            if obj.name == item_id:
                print(obj.name + ":", obj.description)
                return
        for obj in self.player.current_room.items:
            if obj.name == item_id:
                print(obj.name + ":", obj.description)
                return
        print("Skanery nie wykrywają takiego obiektu w pobliżu.")

    def read_archive_log(self, text_digit):
        if not text_digit:
            print("\nDostępne logi i raporty z czarnej skrzynki Horizon:")
            for index, segment in enumerate(STORY_CHAPTERS, 1):
                print(f"{index} - {segment[0]}")
            print("Wpisz: logi [numer]")
            return

        if not text_digit.isdigit():
            print("Podaj poprawny numer raportu, na przykład: logi 1")
            return

        parsed_int = int(text_digit)
        if parsed_int < 1 or parsed_int > len(STORY_CHAPTERS):
            print("Brak takiego zapisu w bazie danych.")
            return

        log_chapter = STORY_CHAPTERS[parsed_int - 1]
        print("\n====== " + log_chapter[0] + " ======")
        for log_line in log_chapter[1:]:
            print(log_line)
        print("==============================")

        self.chronicle_read += 1
        if self.chronicle_read >= 3:
            self.player.add_achievement("Czytelnik kronik")

    def intercept_rumor(self):
        selected_rumor = TRAVEL_RUMORS[self.rumor_index]
        self.rumor_index = (self.rumor_index + 1) % len(TRAVEL_RUMORS)
        print("\nOdebrany komunikat radiowy:")
        print(selected_rumor)
        self.player.add_note(selected_rumor)

    def inspect_subroutines(self, query_id):
        if not query_id:
            print("\n====== REJESTR MISJI ======")
            for name in QUEST_HINTS:
                print("-", name)
            print("Wpisz: misje [nazwa], na przykład: misje klucz")
            print("===========================")
            return

        if query_id not in QUEST_HINTS:
            print("Brak danych na temat takiego zadania.")
            return

        print("\nCel misji:", query_id)
        for point in QUEST_HINTS[query_id]:
            print("-", point)
        self.player.add_note("Zaktualizowano wytyczne dla: " + query_id)

    def display_network_map(self):
        print("""                     I@!Północ!@I
SCHEMAT STATKU USS HORIZON:

                                       [Komora ARES]
                                             |
                                      [Śluza Reaktora]
                                             |
[Hangar Komunikatów] -- [Warsztat] -- [Magazyn Bezp.]
                                             |
   [Moduł Widokowy] -- [Główny K.] -- [Główna Winda]
                             |               |
                      [Śluza Odpadów]  [Bio-Laboratorium]
                             |
                      [Ładownia]
                             |
                      [Moduł Startowy]

                                I@!południe!@I             """)

    def recharge_system(self):
        if self.player.current_room.name != "Moduł Startowy":
            print("Systemy kombinezonu możesz zregenerować tylko w bezpiecznym module startowym.")
            return
        if self.player.rested:
            print("Systemy są już w pełni zoptymalizowane. Czas ucieka.")
            return
        self.player.heal(10)
        self.player.rested = True
        print("Podłączasz kombinezon do stacji dokującej i regenerujesz osłony.")
        print("Stan pancerza:", self.player.health, "/", self.player.max_health)

    def suspend_thread(self):
        if self.player.current_room.enemy and self.player.current_room.enemy.alive:
            print("Nie możesz czearkać, kiedy dron bojowy celuje w twój kombinezon!")
            return

        self.clock.advance_cycle()
        print("Mija czas systemu pokładowego.")
        print("Nowe warunki atmosferyczne w sekcji:", self.clock.weather)

        if self.clock.weather == "deszcz":
            self.player.heal(1)
            print("Uruchomienie zraszaczy awaryjnych chłodzi twój kombinezon. Odzyskujesz 1 hp.")
        elif self.clock.weather == "dym":
            self.player.take_damage(1)
            print("Toksyczny gaz ze spalonych instalacji wdziera się przez filtry. Tracisz 1 hp.")

    def optimize_neuromods(self):
        if self.player.current_room.name != "Moduł Startowy":
            print("Modyfikację modułów kombinezonu możesz przeprowadzić tylko w module startowym.")
            return
        if self.player.gold < 3:
            print("Kalibracja systemu kosztuje 3 kredyty.")
            return
        if self.player.training >= 3:
            print("Konsola inżynieryjna zgłasza: Oprogramowanie osiągnęło limit aktualizacji.")
            return

        self.player.gold -= 3
        self.player.training += 1

        if self.player.training == 1:
            self.player.max_health += 2
            self.player.health += 2
            print("Instalujesz wzmocnienia tytanowe pancerza. Maksymalne zdrowie +2.")
        elif self.player.training == 2:
            self.player.defense += 1
            print("Kalibrujesz generatory mikro-tarcz. Obrażenia od robotów będą mniejsze.")
        else:
            self.player.max_health += 3
            self.player.health += 3
            print("Ostatnia aktualizacja oprogramowania stabilizuje tętno. Maksymalne zdrowie +3.")
            self.player.add_achievement("Uczen trenera")

    def harvest_data_fragments(self):
        node_name = self.player.current_room.name
        if node_name not in ["Główny Korytarz", "Śluza Odpadów", "Moduł Widokowy"]:
            print("W tej sekcji statku nie ma żadnego wartościowego złomu do zebrania.")
            return

        dice_roll = random.randint(1, 6)
        if dice_roll <= 3:
            self.player.herbs += 1
            print("Znaleziono sprawną część zamienną. Masz teraz:", self.player.herbs)
            if self.player.herbs >= 3:
                self.player.add_achievement("Zbieracz ziol")
        elif dice_roll == 4:
            self.player.gold += 1
            print("Zamiast części znajdujesz zagubioną kartę chipową z 1 kredytem.")
        else:
            print("Przeszukujesz korytarz, ale znajdujesz tylko bezużyteczny popiół.")

    def scan_sector(self):
        node_name = self.player.current_room.name
        print("\nUruchamiasz dokładny skaner otoczenia.")

        if node_name in ROOM_DETAILS:
            for piece in ROOM_DETAILS[node_name]:
                print("-", piece)

        item_discovered = False

        if node_name == "Moduł Startowy":
            if not self.village_helped:
                print("Widzisz rannych inżynierów, którzy potrzebują pomocy przy naprawie systemu filtrowania wody.")
            else:
                print("System filtrowania działa sprawnie. Ludzie patrzą na ciebie z nadzieją.")
        elif node_name == "Główny Korytarz":
            if random.randint(1, 2) == 1:
                self.player.herbs += 1
                item_discovered = True
                print("Pod pękniętą osłoną ściany znajdujesz sprawny tranzystor.")
        elif node_name == "Śluza Odpadów":
            if not self.river_blessed:
                print("Możesz spróbować ręcznie zablokować wyciek śmieci komendą 'pomoz'.")
            else:
                print("Śluza została zabezpieczona magnetycznie.")
        elif node_name == "Ładownia":
            if self.secret_counter == 0:
                self.secret_counter += 1
                self.player.gold += 4
                item_discovered = True
                print("Za przewróconym kontenerem znajdujesz portfel z 4 kredytami.")
                self.player.add_achievement("Poszukiwacz sekretow")
            else:
                print("Skanery nie pokazują nic nowego.")
        elif node_name == "Magazyn Bezpieczeństwa":
            if self.player_has_token("klucz"):
                print("Najważniejszy element dostępu z tego sektora masz już przy sobie.")
            else:
                print("Skaner wykrywa sygnaturę karty magnetycznej w pobliżu robotów.")
        elif node_name == "Komora ARES":
            if self.player_has_token("klejnot"):
                print("Zatrzaski po rdzeniu zasilającym iskrzą niebieskim łukiem elektrycznym.")
            else:
                print("Rdzeń zasilający tkwi zablokowany na centralnym postumencie reaktora.")

        if item_discovered:
            self.player.add_note("W sekcji " + node_name + " zlokalizowano przydatne komponenty.")

    def assist_node(self):
        node_name = self.player.current_room.name
        if node_name == "Moduł Startowy":
            if self.village_helped:
                print("Pomogłeś już przy filtrach wody. Ocalali dziękują ci przez interkom.")
                return
            self.village_helped = True
            self.player.reputation += 2
            self.player.gold += 3
            self.player.add_item(Item("mikstura", "Leczy 5 hp", heal=5, price=5))
            self.player.add_note("Załoga zapamięta twoją pomoc przy filtrach.")
            self.player.add_achievement("Przyjaciel wioski")
            print("Naprawiasz filtry i usuwasz skażony osad ze zbiornika.")
            print("Załoga przekazuje ci 3 kredyty oraz apteczkę ze stymulantem.")
            return

        if node_name == "Śluza Odpadów":
            if self.river_blessed:
                print("Śluza jest bezpieczna i ciśnienie wróciło do normy.")
                return
            self.river_blessed = True
            self.player.reputation += 1
            self.player.heal(3)
            self.player.add_note("Zabezpieczono śluzę przed dekompresją.")
            print("Zamykasz ręczne zawory odcinające i zbierasz odłamki metalu z podłogi.")
            print("Syczenie uciekającego powietrza cichnie. Odzyskujesz 3 hp dzięki stabilizacji ciśnienia.")
            return

        if node_name == "Moduł Widokowy":
            if self.player_has_token("amulet"):
                self.player.heal(2)
                print("Chwila odpoczynku przy panoramicznym oknie pozwala ci odetchnąć. Odzyskujesz 2 hp.")
            else:
                print("System sugeruje, abyś zabrał moduł wspomagający ze sobą do dalszych sektorów.")
            return

        print("W tej sekcji statku nie widzisz możliwości podjęcia akcji naprawczej.")

    def execute_move(self, vector):
        active_node = self.player.current_room
        if vector in active_node.exits:
            if active_node.enemy and active_node.enemy.alive:
                print("Systemy obronne wroga blokują to przejście! Musisz najpierw wygrać starcie.")
                return

            target_node = active_node.exits[vector]
            if target_node.locked:
                if self.player_has_token("klucz"):
                    print("Używasz karty magnetycznej. Śluza reaktora otwiera się z sykiem.")
                    target_node.locked = False
                else:
                    print("Grodź jest całkowicie zablokowana. Potrzebujesz karty dostępu reaktora.")
                    return

            self.player.current_room = target_node
            if random.randint(1, 5) == 1:
                hazard_dmg = random.randint(1, 3)
                self.player.take_damage(hazard_dmg)
                print("Wpadłeś na uszkodzoną linię wysokiego napięcia!")
                print("Tracisz", hazard_dmg, "hp z powodu porażenia prądem.")
        else:
            print("Brak korytarza lub śluzy w tym kierunku.")

    def trigger_combat(self):
        active_node = self.player.current_room
        target_adversary = active_node.enemy

        if target_adversary is None or not target_adversary.alive:
            print("Brak aktywnych celów obronnych w tym sektorze.")
            return

        attack_power = random.randint(2, 6)
        for equipment in self.player.inventory:
            if equipment.damage > 0:
                attack_power += equipment.damage

        if self.player_has_token("amulet"):
            attack_power += 1

        target_adversary.take_damage(attack_power)
        print("Zadajesz maszynie", attack_power, "obrażeń energetycznych.")

        if not target_adversary.alive:
            print("Zniszczyłeś i wyłączyłeś proces:", target_adversary.name)
            self.player.gold += target_adversary.gold
            print("Odzyskujesz z wraku", target_adversary.gold, "kredytów.")
            self.player.process_xp(target_adversary.exp)

            if target_adversary.name == "ARES":
                print("\nARES wyłącza się, a czerwone światła awaryjne na pokładzie powoli gasną.")
                if self.player_has_token("klejnot"):
                    print("Posiadasz sprawny Rdzeń Zasilający!")
                    print("URATOWAŁEŚ MISJĘ KOSMICZNĄ I CALĄ ZAŁOGĘ USS HORIZON!")
                else:
                    print("Pokonałeś sztuczną inteligencję, ale zostawiłeś rdzeń w komorze maszynowej.")
                self.running = False
            return

        received_dmg = target_adversary.execute_attack()
        if self.player_has_token("amulet") and received_dmg > 1:
            received_dmg -= 1

        if self.player.defense > 0 and received_dmg > 1:
            received_dmg -= self.player.defense
            if received_dmg < 1:
                received_dmg = 1

        self.player.take_damage(received_dmg)
        print(target_adversary.name, "atakuje cię ładunkiem plazmy, zadając", received_dmg, "obrażeń.")

    def build_cyber_grid(self):
        sword = Item("miecz", "Ciężki klucz francuski z twardej stali magnetycznej", damage=4)
        axe = Item("topor", "Spawarka laserowa warsztatowa", damage=3)
        potion = Item("mikstura", "Stymulant medyczny regenerujący 5 hp", heal=5, price=5)
        big_potion = Item("duza_mikstura", "Zaawansowany pakiet nanobotów leczący 10 hp", heal=10, price=10)
        key = Item("klucz", "Karta magnetyczna z kodem dostępu reaktora")
        amulet = Item("amulet", "Moduł stabilizacji tarczy kombinezonu")
        treasure = Item("klejnot", "Główny Rdzeń Zasilający statku Horizon")

        goblin = Enemy("dron_zwiadowczy", 10, 3, 5, 5)
        wolf = Enemy("cyber_pajak", 8, 3, 3, 4)
        bandit = Enemy("zbuntowany_android", 12, 4, 8, 5)
        skeleton = Enemy("dron_spawalniczy", 15, 4, 10, 6)
        guardian = Enemy("robot_ochronny", 18, 5, 15, 8)
        dragon = Enemy("ARES", 30, 6, 50, 10)

        village = GridNode("Moduł Startowy", "Zniszczona sekcja mieszkalna pełna dymu i rannych kolonistów.")
        forest = GridNode("Główny Korytarz", "Ciemny korytarz z wiszącymi kablami i iskrzącymi panelami.")
        hut = GridNode("Warsztat", "Porzucone stanowisko techniczne pachnące smarami i spalonym tytanem.")
        river = GridNode("Śluza Odpadów", "Szeroka sekcja zsypu śmieci. Ściany noszą ślady dekompresji.")
        cave = GridNode("Ładownia", "Ogromny hangar cargo, gdzie pudła z zaopatrzeniem latają w nieważkości.")
        shrine = GridNode("Moduł Widokowy", "Przeszklony taras obserwacyjny z pięknym, ale zimnym widokiem na gwiazdy.")
        treasury = GridNode("Magazyn Bezpieczeństwa", "Pokój z pancernymi szafami pełnymi zapasowych części i schematów.")
        gate = GridNode("Śluza Reaktora", "Tytanowe, ciężkie wrota odcinające wejście do głównego mainframe'u statku.")
        dragon_room = GridNode("Komora ARES", "Olbrzymia maszynownia rozgrzana do czerwoności. W powietrzu unosi się plazma.")
        
        comm_hangar = GridNode("Hangar Komunikatów", "Sektor nadawczy wypełniony uszkodzonymi przekaźnikami dalekiego zasięgu.")
        bio_lab = GridNode("Laboratorium Bio-Syntetyczne", "Zrujnowane laboratorium pełne potłuczonych kriokapsuł i dziwnego żelu.")
        main_lift = GridNode("Główna Winda", "Olbrzymi szyb towarowy windy, zablokowany pomiędzy pokładami.")

        gate.locked = True

        village.exits["polnoc"] = cave
        cave.exits["poludnie"] = village
        cave.exits["polnoc"] = river
        
        river.exits["poludnie"] = cave
        river.exits["polnoc"] = forest
        
        forest.exits["poludnie"] = river
        forest.exits["zachod"] = shrine
        forest.exits["wschod"] = main_lift
        
        shrine.exits["wschod"] = forest
        
        main_lift.exits["zachod"] = forest
        main_lift.exits["polnoc"] = treasury
        main_lift.exits["poludnie"] = bio_lab
        
        bio_lab.exits["polnoc"] = main_lift
        
        treasury.exits["poludnie"] = main_lift
        treasury.exits["zachod"] = hut
        treasury.exits["polnoc"] = gate
        
        hut.exits["wschod"] = treasury
        hut.exits["zachod"] = comm_hangar
        
        comm_hangar.exits["wschod"] = hut
        
        gate.exits["poludnie"] = treasury
        gate.exits["polnoc"] = dragon_room
        dragon_room.exits["poludnie"] = gate

        forest.enemy = goblin
        hut.enemy = wolf
        river.enemy = bandit
        cave.enemy = skeleton
        treasury.enemy = guardian
        dragon_room.enemy = dragon

        village.items.append(potion)
        hut.items.append(axe)
        cave.items.append(sword)
        shrine.items.append(amulet)
        treasury.items.append(key)
        dragon_room.items.append(treasure)

        self.rooms = {
            "village": village, "forest": forest, "hut": hut, "river": river,
            "cave": cave, "shrine": shrine, "treasury": treasury, "gate": gate, "dragon_room": dragon_room,
            "comm_hangar": comm_hangar, "bio_lab": bio_lab, "main_lift": main_lift
        }

        self.market_terminal = BlackMarket([
            Item("mikstura", "Leczy 5 hp", heal=5, price=5),
            Item("duza_mikstura", "Leczy 10 hp", heal=10, price=10),
        ])

        self.player.current_room = village

    def start(self):
        print("Sztuczna Inteligencja ARES przejęła statek i ukradła Rdzeń Zasilający.")
        print("Od tamtej pory systemy życiowe wysiadają, a w sekcjach słychać ryk przeciążonych reaktorów.")
        print("Twoim celem jest wyłączenie SI ARES i odzyskanie Rdzenia Zasilającego.")
        print("Wpisz 'pomoc' aby zobaczyć dostępne systemowe polecenia.")
        self.player.add_note("Cel misji: pokonać ARES i odzyskać główny rdzeń.")
        self.player.add_achievement("Pierwszy krok")

        init_choice = input("\nKonający nawigator pyta: Chcesz stymulant na drogę? (tak/nie): ").lower()
        if init_choice == "tak":
            self.player.add_item(Item("mikstura", "Leczy 5 hp", heal=5, price=5))
            print("Nawigator podaje ci medykament.")
        else:
            print("Nawigator kiwa głową: Pewna ręka i mocne osłony to też dobry zapas.")

        while self.running and self.player.alive:
            current_node = self.player.current_room
            current_node.render_node()

            if current_node.enemy and current_node.enemy.alive:
                print("\nWrogi mechanizm obronny blokuje śluzę wyjściową!")

            raw_input = input("\n> ").lower().split()
            if not raw_input:
                continue

            action_key = raw_input[0]
            argument = raw_input[1] if len(raw_input) > 1 else ""

            if action_key in self.cmd_dictionary:
                self.cmd_dictionary[action_key](argument)
            else:
                print("Błędna komenda pokładowa.")

            if self.player.health <= 0:
                print("\nTwój kombinezon uległ całkowitemu zniszczeniu w próżni. Zginąłeś.")
                self.running = False

        print("\n[System]: Sesja zakończona. Połączenie przerwane.")

    def setup_command_map(self):
        """Zmapowanie zaktualizowanych poleceń."""
        self.cmd_dictionary = {
            "rusz": lambda t: self.execute_move(t),
            "podnies": lambda t: self.download_item(t),
            "uzyj": lambda t: self.deploy_item(t),
            "logi": lambda t: self.read_archive_log(t),
            "regeneruj": lambda t: self.recharge_system(),
            "sklep": lambda t: self.access_market(),
            "skanuj": lambda t: self.scan_sector(),
            "zbierz": lambda t: self.harvest_data_fragments(),
            "rejestr": lambda t: self.player.show_notes(),
            "misje": lambda t: self.inspect_subroutines(t),
            "czekaj": lambda t: self.suspend_thread(),
            "plotki": lambda t: self.intercept_rumor(),
            "cwiczenia": lambda t: self.optimize_neuromods(),
            "pomoz": lambda t: self.assist_node(),
            "dni": lambda t: self.get_time_metrics(),
            "ekwipunek": lambda t: self.player.print_hardware(),
            "status": lambda t: self.view_status(),
            "mapa": lambda t: self.display_network_map(),
            "osiagniecia": lambda t: self.player.show_achievements(),
            "wyjdz": lambda t: self.terminate_session(),
            "pomoc": lambda t: self.display_help(),
            "atak": lambda t: self.trigger_combat(),
            "obejrzyj": lambda t: self.analyze_target(t),
            "rozmawiaj": lambda t: self.query_npc()
        }  
