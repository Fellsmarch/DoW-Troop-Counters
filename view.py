"""
This module provides a GUI for the DoW Troop Counters program.

Harrison Cook
May 2020
"""
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
        self.originalWindowTitle = "DoW Troop Counters"
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle(self.originalWindowTitle)

        self.ui.actionDewit.triggered.connect(self.generate_data)

        self.first = True

        try:
            self.init()
        except:
            pass


    def init(self):
        """
        Initialises the data display in the GUI
        """
        self.config = load_from_json("config.json")
        self.troops = load_from_json(self.config["data"]["troops"], self.first)
        self.weapons = load_from_json(self.config["data"]["weapons"], self.first)
        self.armour_types = load_from_json(self.config["data"]["armourTypes"], self.first)
        self.counters = load_from_json(self.config["data"]["counters"], self.first)

        self.current_troop_list = list(self.troops)
        self.opponent_race_selected = None

        self.ui.opponentRaceList.currentItemChanged.connect(self.populate_troops)
        self.ui.opponentUnitList.currentItemChanged.connect(self.display_troop)
        self.ui.playerRaceList.currentItemChanged.connect(self.player_race_change)

        self.populate_races()

        self.first = False


    def populate_races(self):
        """
        Populates the race lists.
        """
        self.ui.opponentRaceList.clear()
        self.ui.opponentRaceList.addItems(list(self.troops))
        self.ui.playerRaceList.clear()
        self.ui.playerRaceList.addItems(list(self.troops))


    def populate_troops(self, selected_race):
        """
        Populates the troop lists
        
        :param selected_race: the race that has been selected by the user
        """
        self.ui.opponentUnitList.clear()
        if selected_race:
            self.opponent_race_selected = selected_race.text()
            for troop in self.troops[self.opponent_race_selected]:
                CustomQListWidgetItem(self.troops[self.opponent_race_selected][troop]['display_name'], troop, self.ui.opponentUnitList)


    def display_troop(self, selected_troop):
        """
        Populates the troop information labels when a troop is selected.

        :param selected_troop: the troop that has been selected
        """
        self.reset_table()
        if selected_troop:
            troop = self.troops[self.opponent_race_selected][selected_troop.value]
            self.ui.opponentUnitNameLabel.setText(troop["display_name"])
            self.ui.opponentFileNameLabel.setText(troop["troop_file"])
            self.ui.opponentArmourTypeLabel.setText(troop["armour_types"])
            self.ui.opponentUnitWeaponList.clear()
            self.ui.opponentUnitWeaponList.addItems(troop["weapons"])
        else:
            self.ui.opponentUnitNameLabel.clear()
            self.ui.opponentFileNameLabel.clear()
            self.ui.opponentArmourTypeLabel.clear()
            self.ui.opponentUnitWeaponList.clear()


    def player_race_change(self, selected_race):
        """
        Process the user changing the player race selection.
        """
        if len(self.ui.opponentFileNameLabel.text()) > 0:
            self.populate_table(selected_race)


    def populate_table(self, selected_race):
        """
        Populates the counters (DPS) table.

        :param selected_race: the player race the user has selected
        """
        selected_race = selected_race.text()
        selected_armour_type = self.ui.opponentArmourTypeLabel.text()
        counters = self.counters[selected_race][selected_armour_type]
        table = self.ui.playerCounterTable

        # Troop, Weapon, Damage columns
        table.setColumnCount(3)
        # Table has a min size of 420
        table.setColumnWidth(0, 175)
        table.setColumnWidth(1, 175)
        table.setColumnWidth(2, 45)
        table.setRowCount(len(counters))
        table.setHorizontalHeaderLabels(["Troop", "Weapon", "DPS"])

        for index, counter in enumerate(counters):
            unit_name = self.troops[selected_race][counter["troop_file"]]["display_name"]
            table.setItem(index, 0, QtWidgets.QTableWidgetItem(unit_name)) 
            table.setItem(index, 1, QtWidgets.QTableWidgetItem(counter["weapon"]))
            table.setItem(index, 2, QtWidgets.QTableWidgetItem("{:.1f}".format(counter["damage"])))


    def reset_table(self):
        """
        Resets the counter table.
        """
        table = self.ui.playerCounterTable
        table.setRowCount(0)


    def setWindowStatus(self, new_status):
        """
        Sets the window title status by appending the status to the 
        original window title.

        :param new_status: the new status to display
        """
        self.setWindowTitle(self.originalWindowTitle + " - " + new_status)


    def generate_data(self):
        """
        Runs the data generation script.
        """
        try:
            self.setWindowStatus("Generating data...")
            
            generate_data.run()

            self.setWindowStatus("Populating GUI elements..")

            self.init()
            self.setWindowStatus("Data successfuly generated")
        except Exception as e:
            self.setWindowStatus(f"Failed to generate data: {e}")


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    application = MainWindow()
    application.show()

    sys.exit(app.exec())