import os
import sys
from stat import S_ISDIR

import yaml
import paramiko

from utils import *

CURRENT_DIR = find_base_dir()
# Load configs
CONFIGS_PATH = os.path.join(CURRENT_DIR, '..','configs.yml')
with open(CONFIGS_PATH, 'r') as f:
    configs = yaml.safe_load(f)

configs = dict(configs)

def download_games() -> None:
    """
    Prompts the user to download game directories or files from a remote server.

    Returns:
    None
    """

    # Ensure the Games folder exists locally
    games_folder = os.path.join(CURRENT_DIR, '..','Games')

    # Setup SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Assuming 'server_ip' includes both the IP address and port number
    server_ip = configs['server_configs']['server_ip']
    server_port = int(configs['server_configs']['server_port'])

    # Connect to the server (you might need to add username and password/SSH key parameters)
    ssh.connect(server_ip, port=server_port, username=configs['server_configs']['server_username'], password=configs['server_configs']['server_password'])

    # Initialize SFTP client here
    sftp = ssh.open_sftp()

    print('\n\nPick the remote game by typing its ID (press enter to quit):')
    id_to_game = list_games(True, ssh, configs["games_folder"])

    while True:

        game_id = input('\n')
        if game_id == '':
            return
        elif game_id.isdigit() and int(game_id) in id_to_game:
            game_id = int(game_id)
            break
        else:
            not_valid_choice(game_id)

    
    game_type, game_file = id_to_game[game_id]
    while True:
        response = input(f'\nDo you want to download {game_file} from {server_ip}:{server_port}? [Y/n]\n').upper()
            
        if response == 'Y' or response == '':

            remote_path = os.path.join(configs['games_folder'] + f'/{game_type}' + f'/{game_file}')
            local_path = os.path.join(games_folder, game_type, game_file)

            # Attempt to get the remote file's modification time
            remote_file_attr = sftp.stat(remote_path)
            remote_mtime = remote_file_attr.st_mtime

            # Check if the local file exists and get its modification time
            local_mtime = 0
            if os.path.exists(local_path):
                local_mtime = os.path.getmtime(local_path)

            while True:
                # Check which file is newer between local and remote ones
                if remote_mtime > local_mtime and local_mtime > 0:
                    response = input(f'You already have {game_file}, it seems that you files are outdated. Do you want to overwrite your local files? [y/N]\n').upper()
                elif remote_mtime < local_mtime and local_mtime > 0:
                    response = input(f'You already have {game_file} and they are more recent than the server\'s one. Do you want to overwrite your local files? [y/N]\n').upper()
                else:
                    response = 'Y'

                if response == 'Y':
                    if not os.path.exists(os.path.dirname(local_path)):
                        os.makedirs(os.path.dirname(local_path))
                        print(f'Created local directory {os.path.dirname(local_path)}')

                    # Use SFTP to download the file
                    sftp.get(remote_path, local_path)
                    print(f'--- Downloaded {os.path.basename(remote_path)} ---')
                    break

                elif response == 'N' or response == '':
                    break

                else:
                    not_valid_choice(response)

            break

        elif response == 'N':
            break

        else:
            not_valid_choice(response)

    ssh.close()

    download_games()