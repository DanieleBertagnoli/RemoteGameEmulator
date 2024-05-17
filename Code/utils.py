import os
import sys
import yaml

def list_games(remote=False, ssh=None, remote_folder=None):
    
    CURRENT_DIR = find_base_dir()
    CONFIGS_PATH = os.path.join(CURRENT_DIR, '..','configs.yml')
    with open(CONFIGS_PATH, 'r') as f:
        configs = yaml.safe_load(f)

    configs = dict(configs)

    id_to_game = {}

    known_ext = configs['game_file_extensions']

    if remote:

        if not ssh or not remote_folder:
            print('--- Error while listing remote files, no ssh or no remote_folder given! ---')
            return None

        # Use SSH to list files in the remote games_folder
        stdin, stdout, stderr = ssh.exec_command(f'ls {remote_folder}')
        available_remote_games_types = stdout.readlines()
        available_remote_games_types = [filename.strip() for filename in available_remote_games_types]  # Clean up newline characters
        available_remote_games_types = sorted(available_remote_games_types)

        for i, game_type in enumerate(available_remote_games_types):
            game_titles = stdin, stdout, stderr = ssh.exec_command(f'ls {remote_folder}/{game_type}')
            game_titles = stdout.readlines()
            game_titles = [filename.strip() for filename in game_titles]  # Clean up newline characters
            for game_title in game_titles:
                file_ext = game_title.split('.')[-1]
                if file_ext not in known_ext:
                    continue
                print(f'- {i}: {game_title} ({game_type})')
                id_to_game[i] = (game_type, game_title)
            
            print(f'\n{len(id_to_game)} remote games found.')

    else:
        
        CURRENT_DIR = find_base_dir()
        games_folder = os.path.join(CURRENT_DIR, '..', 'Games')
        available_games = sorted(os.listdir(games_folder))
        for i, game_type in enumerate(available_games):
            for game_title in os.listdir(os.path.join(games_folder, game_type)):
                file_ext = game_title.split('.')[-1]
                if file_ext not in known_ext:
                    continue
                print(f'- {i}: {game_title} ({game_type})')
                id_to_game[i] = (game_type, game_title)

        print(f'\n{len(id_to_game)} local games found.')

    return id_to_game

def not_valid_choice(choice:str) -> None:
    print(f'\n!!! {choice} is not a valide choice, try again !!!\n')    


def find_base_dir():
    # Check if running as a bundled application
    if getattr(sys, 'frozen', False):
        # If bundled, the executable path is in sys.executable
        base_dir = os.path.dirname(sys.executable)
    else:
        # If running as a regular script, use the script's directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return base_dir