import os
import subprocess
import sys
import time

import yaml

from upload_games import upload_games
from download_games import download_games
from utils import *

CURRENT_DIR = find_base_dir()
# Load configs
CONFIGS_PATH = os.path.join(CURRENT_DIR, '..','configs.yml')
with open(CONFIGS_PATH, 'r') as f:
    configs = yaml.safe_load(f)

configs = dict(configs)

import os
import subprocess

def play() -> None:
    """
    Allows the user to select and play a game from the available games folder.
    
    This function prompts the user to select a game by typing its ID. Once a valid ID is entered, 
    the corresponding game is selected and launched using the appropriate emulator. After playing 
    the game, it uploads the game data.

    Parameters:
        None

    Returns:
        None
    """
    # Define the folder where games are stored
    games_folder = os.path.join(CURRENT_DIR, '..', 'Games')
           
    emulators_path = os.path.join(CURRENT_DIR, '..', 'Emulators')
    emulators = os.listdir(emulators_path)

    print('\n\nPick your emulator by typing its ID (press enter to quit):')
    for i, e in enumerate(emulators):
        print(f'- {i}: {e}')

    while True:
        response = input('\n')

        if response == '':
            return
        elif response.isdigit() and int(response)>=0 and int(response) < len(emulators):
            response = int(response)
            selected_emulator = os.path.join(emulators_path, emulators[response])
            break
        else:
            not_valid_choice() 

    emulator = None
    for executable in os.listdir(selected_emulator):
        if configs['current_os'] in executable:
            emulator = os.path.join(selected_emulator, executable)
            break

    
    if not emulator:
        print(f'\nThere are not executables containing the {configs["current_os"]} in the name\n')
        return


    # Display available games to the user
    print('\n\nPick your game by typing its ID (press enter to quit):')
    id_to_game = list_games(False)

    # Keep asking the user for input until a valid game ID is entered
    while True:
        response = input('\n')
            
        if response == '':
            return
        elif response.isdigit() and int(response) >= 0 and int(response) < len(id_to_game):
            response = int(response)

            selected_game = id_to_game[response]
            print(f'\n\n {selected_game[1]} selected for {selected_game[0]} emulator! Let\'s play!\n\n')

            # Construct the path to the selected game file
            selected_game = os.path.join(games_folder, selected_game[0], selected_game[1], selected_game[2])
            break
        else:
            not_valid_choice(response)

    # Launch the selected game using the appropriate emulator
    subprocess.run([emulator, selected_game])
    
    # Update the game file access time

    # Get the new mtime
    new_mtime = time.time()
    # Get current atime
    old_atime = float(os.path.getatime(selected_game))
    # Update the atime while keeping the mtime unchanged

    os.utime(selected_game, (old_atime, new_mtime))

    # Upload the game data after playing
    upload_games()



def configure() -> None:
    """
    Allows the user to configure emulator variables.

    This function presents a menu to the user to configure various emulator variables.
    The user can select a variable and update its value. The updated configuration 
    is saved to the configuration file.

    Parameters:
        None

    Returns:
        None
    """
    print('\nHere you can configure your emulator variables\n')
        
    id_to_config = {}
    string = ''
    i = 0

    # Build a menu of configuration options
    for config in configs:
        if type(configs[config]) == dict:
            for subconfig in configs[config]:
                id_to_config[i] = (config, subconfig)
                string += f'{i}: {config} - {subconfig}\n'
                i += 1
        else:
            id_to_config[i] = config
            string += f'{i}: {config}\n'
            i += 1

    # Prompt the user to select and configure a variable
    while True:
        response = input(f'\nType the associated number to perform the action (press enter to quit):\n{string}\n')

        if response == '':
            break

        elif response.isdigit() and int(response) in id_to_config:
            response = int(response)
            selected_config = id_to_config[response]

            # Determine if the selected configuration is a main configuration or a sub-configuration
            if not type(selected_config) == str:
                main_config = selected_config[0]
                subconfig = selected_config[1]
                old_val = configs[main_config][subconfig] 
            else:
                old_val = configs[selected_config]
            
            # Prompt the user to update the selected configuration
            while True:
                response = input(f'\nCurrent value for {selected_config} = {old_val}, do you want to overwrite it? [y,N]: ').upper()

                if response == 'Y':
                    new_value = input(f'Type the new value for {selected_config}: ')
                    if not type(selected_config) == str:
                        configs[main_config][subconfig] = new_value
                    else:
                        configs[selected_config] = new_value
                    print(f'--- {selected_config} successfully updated ---')
                    break

                elif response == 'N' or response == '':
                    break
                else:
                    not_valid_choice(response)

        else:
            not_valid_choice(response)

    # Save the updated configuration to the configuration file
    with open(CONFIGS_PATH, 'w') as f:
        yaml.dump(configs, f, default_flow_style=False)




import sys

def menu() -> None:
    """
    Displays the main menu of the GameBoyEmulator and allows the user to perform various actions.

    This function displays the main menu of the GameBoyEmulator application. It prompts the user
    to select an action by typing the associated number. The available actions include listing
    available games, playing a game, downloading game files, uploading game files, and configuring variables.

    Parameters:
        None

    Returns:
        None
    """
    print('\n\n\n###    GameBoyEmulator v1  ###\n\n\n')

    server_configs = configs['server_configs']
    
    # Check if server configs are missing and prompt the user to set them up
    for key in server_configs:
        if not server_configs[key]:
            print('\nOps... It seems that some server configs are missing. Let\'s set them up!\n')
            configure()

    # Define actions available in the menu
    actions = {
        0: list_games,
        1: play,
        2: download_games,
        3: upload_games,
        4: configure
    }

    # Main menu loop
    while True:
        response = input('\nType the associated number to perform the action (press enter to quit):\n'
                         '0: List available games (local)\n'
                         '1: Play\n'
                         '2: Download game files from the remote server\n'
                         '3: Upload game files to the remote server\n'
                         '4: Configure variables\n\n')

        # Exit the program if the user presses enter
        if response == '':
            sys.exit()

        # Execute the selected action based on the user's input
        elif response.isdigit() and int(response) in actions:
            response = int(response)
            action = actions[response]
            action()
        else:
            not_valid_choice(response)



if __name__ == '__main__':

    games_folder = os.path.join(CURRENT_DIR, '..', 'Games')
    if not os.path.exists(games_folder):
        os.makedirs(games_folder)

    menu()
