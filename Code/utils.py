import os
import sys
import yaml

def list_games(remote=False, ssh=None, remote_folder=None):
    
    CURRENT_DIR = find_base_dir()
    CONFIGS_PATH = os.path.join(CURRENT_DIR, '..', 'configs.yml')
    with open(CONFIGS_PATH, 'r') as f:
        configs = yaml.safe_load(f)

    configs = dict(configs)

    id_to_game = {}

    known_ext = configs['game_file_extensions']

    if remote:

        if not ssh or not remote_folder:
            print('--- Error while listing remote files, no ssh or no remote_folder given! ---')
            return None

        # Use SSH to list directories in the remote games_folder
        stdin, stdout, stderr = ssh.exec_command(f'ls -p {remote_folder} | grep /')
        available_remote_game_types = stdout.readlines()
        available_remote_game_types = [game_type.replace('\n', '')[:-1] for game_type in available_remote_game_types]  # Clean up newline characters and remove trailing slashes
        available_remote_game_types = sorted(available_remote_game_types)

        id_counter = 0
        for game_type in available_remote_game_types:
            stdin, stdout, stderr = ssh.exec_command(f'ls -p {remote_folder}/{game_type}')
            result = stdout.readlines()
            game_titles = []
            for game_title in result:
                game_title = game_title.replace('\n', '')
                if game_title.endswith('/'):
                    game_titles.append(game_title[:-1])

            for game_title in game_titles:
                stdin, stdout, stderr = ssh.exec_command(f'ls {remote_folder}/{game_type}/{game_title}')
                game_files = stdout.readlines()
                game_files = [game_file.strip() for game_file in game_files]

                game_file_name = next((game_file for game_file in game_files if game_file.split('.')[-1] in known_ext), None)
                if game_file_name:
                    print(f'- {id_counter}: {game_title} ({game_type})')
                    id_to_game[id_counter] = (game_type, game_title, game_file_name)
                    id_counter += 1

        print(f'\n{id_counter} remote games found.')

    else:

        games_folder = os.path.join(CURRENT_DIR, '..', 'Games')
        available_game_types = sorted(os.listdir(games_folder))

        id_counter = 0
        for game_type in available_game_types:
            game_type_path = os.path.join(games_folder, game_type)
            if not os.path.isdir(game_type_path):
                continue

            game_titles = sorted(os.listdir(game_type_path))
            for game_title in game_titles:
                game_title_path = os.path.join(game_type_path, game_title)
                if not os.path.isdir(game_title_path):
                    continue

                game_files = os.listdir(game_title_path)
                game_file_name = next((game_file for game_file in game_files if game_file.split('.')[-1] in known_ext), None)
                if game_file_name:
                    print(f'- {id_counter}: {game_title} ({game_type})')
                    id_to_game[id_counter] = (game_type, game_title, game_file_name)
                    id_counter += 1

        print(f'\n{id_counter} local games found.')

    return id_to_game

def not_valid_choice(choice:str) -> None:
    print(f'\n!!! {choice} is not a valid choice, try again !!!\n')    


def find_base_dir():
    # Check if running as a bundled application
    if getattr(sys, 'frozen', False):
        # If bundled, the executable path is in sys.executable
        base_dir = os.path.dirname(sys.executable)
    else:
        # If running as a regular script, use the script's directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return base_dir
