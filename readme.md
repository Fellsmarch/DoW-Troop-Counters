# DoW Troop Counters
This program allows you to find the units in Dawn of War: Soulstorm that do the most damage to a unit of your choice (the unit which counters another unit). The GUI only runs on Windows, but the python script will work to generate the data files that are displayed in the GUI.

# Usage
1. Download the packaged release [here](https://github.com/Fellsmarch/DoW-Troop-Counters/releases)
2. Unzip
3. Generate or download your input files and point the corresponding config values to them
4. Run `view.exe` and the GUI should appear
5. To generate the data and populate the lists go to the `Generate Data` menu option and click `dewit`
6. Select your opponent's race 
7. Select your opponent's troop
8. Select your race
9. The table on the right should poulate showing you which of your units with which weapon do the best DPS against the selected opponent's troop

## Running from source 
### Requirements:
- Python 3.6+
- [PtQt5](https://pypi.org/project/PyQt5/)

### Steps:
1. Clone repository or download zip
2. Generate or download your input files and point the corresponding config values to them
3. Open terminal/command line/powershell and change to directory containing the program
4. Run `python view.py` (or `python3 view.py` depending on your installation). The GUI should appear up
5. Same as above from step 5

## Generating data without the GUI
If you are not on Windows or don't want the GUI for some reason, you can generate all the data that populates the GUI by downloading the source and running `python generate_data.py`, or by calling the `run()` function in `generate_data.py`.


# Config File
The config file allows you to customise input files, output files and logging settings.

- `corsixWeaponDPS` - a path to a csv file containing every weapon's dps (damage per second) against each armour type in the game. See below on how to generate this file
- `loggingLevel` - `DEBUG`, `INFO`, `WARNING` or `ERROR` (case sensitive)
- `loggingOverwrite` - whether or not the logging file should be overwritten (write-mode), or appended to (append-mode)
- `logFile` - the file to save logs to
- `data` files - where each data file should be saved to
- `troops` - an object mapping race names to input directories for those races. These must be present for the program to run, so remove unwanted races from the config file

# Inputs
This program may have issues pointing to directories with with full stops ('.') in the name, use with caution. I personally play Salcol's patch for Ultimate Apocalypse, so I have all the input files generated for `Salcol's 1.23`, you can download them [here](https://drive.google.com/file/d/1vnw8au0XT5l06UgcQaeJhyiR5mP7DUjm/view?usp=sharing) if you want.

## Weapon DPS file
`corsixWeaponDPS` in the config file, this file lists every weapon and it's DPS against every armour type. This method to generate this file is by using [Corsix's Mod Studio](http://modstudio.corsix.org/). 

When you have loaded a mod (or base game) in Corsix's, go to the `Tools` tab (not Relic's Tools) and use the `DoW DPS Calculator`. 

This generates an HTML file you can open in you web browser, do this and then copy the contents of the web page (`Ctrl-a` -> `Ctrl-c`). 

Paste the contents of that web page into Excel (a similar program may work). Save this file as a `.csv` and that is your `corsixWeaponDPS` file.

## Troop files
Troop files are manually time consuming to generate, I have found no .rgd to .lua program that works for me. To generate them, you need Corsix's again.

When you have loaded a mod (or base game) go to `Data` -> `attrib` -> `ebps` -> `races` -> choose a race -> `troops`.

Now you need to go through every .rgd troop file and right click -> `Dump RGD to lua`. You need to do this for every troop and every race you want to have stats for.

Go to the mod folder and copy out the .lua files (e.g. `C:/whatever/Dawn of War Soulstorm/UltimateApocalypse_THB_Salcol`). The lua files are in the same directory as they were in Corsix's (i.e. follow the same flow to get to them as above).

Copy out these files to whatever directory you want and then point the corresponding `troops` entry in the config file to it. 

# File Structure
- `armour_types.py` - generates and formats data to do with armour types
- `config.json` - the config file
- `file_handlers.py` - a helper module for file read/writing
- `generate_data.py` - the 'main' file for generating data, calls all the other data generation files
- `readme.md` - hi
- `requirements.txt` - the pip generated list of requirements which can be use to get all requirements easily with `venv`
- `troops.py` - generates and formats data to do with troops/units
- `view.py` - the file containing the GUI data-mapping and the `__main__` file
- `weapons.py` - generates and formats data to do with weapons (and the initial armour types)
- `window_file.py` - a generated PtQt5 designer file describing the GUI elements

# Troubleshooting / FAQ
### Help! I'm seeing duplicated units to select from!
This is because there a multiple units with the same in-game name, many of them are singleplayer-only units (usually have `sp` in the filename). You can remove these troop files manually or just ignore them