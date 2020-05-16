import sys
import generate_data

from PyQt5 import QtWidgets, uic

from file_handlers import load_from_json
from window_file import Ui_MainWindow


class CustomQListWidgetItem(QtWidgets.QListWidgetItem):
    def __init__(self, text, value, listWidget):
        super().__init__(text, listWidget)
        self.value = value


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.actionDewit.triggered.connect(self.generate_data)

        try:
            self.init()
        except:
            pass

    def init(self):
        self.config = load_from_json("config.json")
        self.troops = load_from_json(self.config["data"]["troops"])
        self.weapons = load_from_json(self.config["data"]["weapons"])
        self.armour_types = load_from_json(self.config["data"]["armourTypes"])
        self.counters = load_from_json(self.config["data"]["counters"])

        self.current_troop_list = list(self.troops)
        self.opponent_race_selected = None

        self.ui.opponentRaceList.currentItemChanged.connect(self.populate_troops)
        self.ui.opponentUnitList.currentItemChanged.connect(self.select_troop)
        self.ui.playerRaceList.currentItemChanged.connect(self.player_race_change)

        self.populate_boxes()


    def populate_boxes(self):
        self.populate_races()


    def populate_races(self):
        self.ui.opponentRaceList.addItems(list(self.troops))
        self.ui.playerRaceList.addItems(list(self.troops))


    def populate_troops(self, selected_race):
        self.ui.opponentUnitList.clear()
        self.opponent_race_selected = selected_race.text()
        for troop in self.troops[self.opponent_race_selected]:
            CustomQListWidgetItem(self.troops[self.opponent_race_selected][troop]['display_name'], troop, self.ui.opponentUnitList)


    def select_troop(self, widget_item):
        self.reset_table()
        if widget_item:
            troop = self.troops[self.opponent_race_selected][widget_item.value]
            self.ui.opponentUnitNameLabel.setText(troop["display_name"])
            self.ui.opponentFileNameLabel.setText(troop["troop_file"])
            self.ui.opponentArmourTypeLabel.setText(troop["armour_types"])
            self.ui.opponentUnitWeaponList.addItems(troop["weapons"])
        else:
            self.ui.opponentUnitNameLabel.clear()
            self.ui.opponentFileNameLabel.clear()
            self.ui.opponentArmourTypeLabel.clear()
            self.ui.opponentUnitWeaponList.clear()


    def player_race_change(self, selected_race):
        if len(self.ui.opponentFileNameLabel.text()) > 0:
            self.populate_table(selected_race)
        else:
            print("Oopsies")


    def populate_table(self, selected_race):
        selected_race = selected_race.text()
        selected_armour_type = self.ui.opponentArmourTypeLabel.text()
        counters = self.counters[selected_race][selected_armour_type]
        table = self.ui.playerCounterTable

        # Troop, Weapon, Damage
        table.setColumnCount(3)
        table.setRowCount(len(counters))
        table.setHorizontalHeaderLabels(["Troop", "Weapon", "DPS"])

        for index, counter in enumerate(counters):
            unit_name = self.troops[selected_race][counter["troop_file"]]["display_name"]
            table.setItem(index, 0, QtWidgets.QTableWidgetItem(unit_name)) 
            table.setItem(index, 1, QtWidgets.QTableWidgetItem(counter["weapon"]))
            table.setItem(index, 2, QtWidgets.QTableWidgetItem(str(counter["damage"])))


    def reset_table(self):
        table = self.ui.playerCounterTable
        table.setRowCount(0)


    def generate_data(self):
        # Maybe I need to thread this?
        status_label = self.ui.statusLabel

        try:
            status_label.setText("Generating data...")
            status_label.resize(50, 50)
            
            generate_data.run()

            status_label.setText("Populating GUI elements...")
            self.init()

            status_label.setText("Done")
        except Exception as e:
            status_label.setText(f"Failed to generate data: {e}")
        

app = QtWidgets.QApplication([])

application = MainWindow()
application.show()

sys.exit(app.exec())