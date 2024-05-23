import os
import paramiko
import yaml
from tqdm import tqdm

from utils import *

CURRENT_DIR = find_base_dir()
# Load configs
CONFIGS_PATH = os.path.join(CURRENT_DIR, '..','configs.yml')
with open(CONFIGS_PATH, 'r') as f:
    configs = yaml.safe_load(f)

configs = dict(configs)

def upload_games() -> None:

    # Ensure the Games folder exists locally
    games_folder = os.path.join(CURRENT_DIR, '..', 'Games')
    if not os.path.exists(games_folder):
        os.makedirs(games_folder)

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

    # Display available games to the user
    print('\n\nPick the game you want to upload on the server by typing its ID (press enter to quit):')
    id_to_game = list_games(False)

    while True:

        game_id = input('\n')
        if game_id == '':
            ssh.close()
            return
        elif game_id.isdigit() and int(game_id) in id_to_game:
            game_id = int(game_id)
            break
        else:
            not_valid_choice(game_id)

    game_type, game_file = id_to_game[game_id]

    while True:

        response = input(f'\nDo you want to upload {game_file} to {server_ip}:{server_port}? [y/N]\n').upper()

        if response == 'Y':

            remote_path = configs['games_folder'] + f'/{game_type}' + f'/{game_file}'
            local_path = os.path.join(games_folder, game_type, game_file)

            try:
                # Attempt to get the remote file's modification time
                remote_file_attr = sftp.stat(remote_path)
                remote_mtime = remote_file_attr.st_mtime
            except FileNotFoundError:
                remote_mtime = 0

            # Check if the local file exists and get its modification time
            local_mtime = 0
            if os.path.exists(local_path):
                local_mtime = os.path.getmtime(local_path)

            while True:
                # Check which file is newer between local and remote ones
                if remote_mtime < local_mtime and local_mtime > 0 and remote_mtime > 0:
                    response = input(f'Your {game_file} files are more recent than the server\'s one. Do you want to overwrite the remote files? [y/N]: ').upper()
                elif remote_mtime > local_mtime and local_mtime > 0 and remote_mtime > 0:
                    response = input(f'Your {game_file} files are outdated with respect to the remote ones. Do you want to overwrite the remote files? [y/N]: ').upper()
                else:
                    response = 'Y'

                if response == 'Y':
                    # First, check if the remote directory exists, if not, create it
                    try:
                        sftp.stat(os.path.dirname(remote_path))
                    except FileNotFoundError:
                        sftp.mkdir(os.path.dirname(remote_path))
                        print(f'Created remote directory {os.path.dirname(remote_path)}')

                    # Use SFTP to upload the file with a progress bar
                    with open(local_path, 'rb') as local_file:
                        local_file_size = os.path.getsize(local_path)
                        with tqdm(total=local_file_size, unit='B', unit_scale=True, desc=os.path.basename(local_path)) as pbar:
                            def callback(bytes_transferred, bytes_total):
                                pbar.update(bytes_transferred - pbar.n)

                            sftp.put(local_path, remote_path, callback=callback)

                    print(f'--- Uploaded {os.path.basename(local_path)} to {remote_path} ---')
                    break

                elif response == 'N' or response == '':
                    break

                else:
                    not_valid_choice(response)

            break

        elif response == 'N' or response == '':
            break

        else:
            not_valid_choice(response)

    ssh.close()

    upload_games()
