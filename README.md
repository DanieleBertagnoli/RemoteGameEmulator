## Remote Game Emulator 👾

This project allows both Linux and Windows users to play with game-platform emulators by implementing a game's savings management system. In detail, you must specify the server on which the files will be stored and then every time you play with them, in a few steps you can download them and start playing! Once your game session is terminated, you can also upload the new files to the server. In this way, you can switch computers without losing any progress in your games. The project provides you with compiled versions of the game (one for Windows and one for Linux) without the need for manual compilation (**YOU DON'T NEED PYTHON OR ANY ADDITIONAL LIBRARIES TO RUN THEM!**). You can still make changes in the code and compile the game manually (see next sections).

## Future Roadmap

- [x] Add support for other emulators (NDS, etc...)

## Requirements 📋

You must have a server (either private or public) that can be accessed via SFTP. For now, the connection to the server is password-driven only; therefore, you need both a username and password to access the server via SSH.

## Installation 🚀

First of all, you have to clone this repository using the command:

```
git clone https://github.com/DanieleBertagnoli/GameBoyEmulator.git
```

Now you can directly use the system; the executables are placed in `dist/` and are respectively `main_linux` for Linux users and `main_windows.exe` for Windows users.


### Set up the server configs

The first time you run the system, you will be prompted with some instructions to set up your server's configs. If you want, you can also set them manually by editing the `configs.yml` file (you have to recompile the game, see the next section).

### Compile the project

You can edit the code as you want to fit it to your needs. To do so, I suggest creating a virtual environment and installing the required dependencies using the following commands:

```
python -m venv venv
./venv/bin/activate
pip install -r requirements.txt
```

Or by using anaconda/miniconda:

```
conda create --prefix=./venv
conda activate ./venv
pip install -r requirements.txt
```

This project is written in Python. To produce executables, I used the Python library [PyInstaller](https://pyinstaller.org/en/stable/). Once you have done that, the project can be compiled using the command:

```
pyinstaller --onefile Code/main.py
```

### Run the executables
For windows users it is sufficient to double-click on the `main_windows.exe` file and it will run. 

For Linux users instead, ensure that the file has the execution permissions by typing in the terminal the following command:

```
sudo chmod +x dist/main_linux
```

and then you can run the system by typing:

```
./dist/main_linux
```

### Set up Games directory

To play with the emulator, you need the ROM file of the game (you can find them on many sites). Once you have downloaded them, create a folder for each of those ROMs in one of your server's folders:

```
/path/to/games/folder/server

---- GBA/
    - game1.gba
    - game2.gba


---- NDS/
    - game1.nds
    - game2.nds

etc...
```

**NB:** If you cannot place the ROMs on the server, you can create a folder called `Games/` in the root of the project and place the game folders inside it.


## Emulators 🖥️

The project provides you with the [mGBA emulator](https://mgba.io/) in both Linux and Windows versions. You can freely change the emulator with the one you prefer by placing it inside the `Emulator/GBA/` folder. In that case, be sure that, if the emulator is for Linux then the name must contain 'linux', if it's for Windows the name must contain 'windows'. Moreover, to avoid errors, ensure that the emulator you chose can be run via terminal using the syntax:


```
path_to_emulator_executable path_to_game_file
```

Otherwise, you won't be able to run the game using the project.

You can also install other emulators such as [PCSX2](https://pcsx2.net/) for emulating the PlayStation2 console or [Dolphin](https://it.dolphin-emu.org/download/) for Wii and GameCube emulation. Keep in mind that they must be placed in a dedicated sub-folder of `Emulators/` folder. When you add a new emulator, don't forget to add the game extension in `configs.yml`:

```
configs.yml

other configs
game_file_extensions: 'gba nds new_file_extension'
other configs
```

When the system scans for game files it will only list files with an extension which is present in that list.

### New Update !!!
We also added an NDS emulator [Desmume](http://desmume.org/). In this specific case, we haven't found any portable version for Linux. Nevertheless, in the `linux_nds_emulator.sh` file we added a shortcut to run the `desmume` command using a .sh file. The command must be installer, you can manually install it using:

```
sudo apt-get install desmume -y
```

If the command is not found the .sh script will install it for you. 