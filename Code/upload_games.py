import os
import paramiko
import yaml
from tqdm import tqdm

from utils import *

CURRENT_DIR = find_base_dir()

# Load configs
CONFIGS_PATH = os.path.join(CURRENT_DIR, '..', 'configs.yml')
with open(CONFIGS_PATH, 'r') as f:
    configs = yaml.safe_load(f)

configs = dict(configs)

def ensure_remote_dir_exists(sftp, remote_directory):
    """
    Ensure that the remote directory exists, create it if it does not.
    """
    dirs = remote_directory.split('/')
    current_dir = ''
    for dir in dirs:
        if dir:
            current_dir = f'{current_dir}/{dir}'
            try:
                sftp.stat(current_dir)
            except FileNotFoundError:
                sftp.mkdir(current_dir)

def upload_folder(sftp, local_folder, remote_folder):
    """
    Upload a local folder to a remote folder via SFTP.
    """
    if not os.path.exists(local_folder):
        print(f'Local folder {local_folder} does not exist.')
        return

    ensure_remote_dir_exists(sftp, remote_folder)
    print(f'Created remote directory {remote_folder}')

    for item in os.listdir(local_folder):
        local_item_path = os.path.join(local_folder, item)
        remote_item_path = os.path.join(remote_folder, item)

        if os.path.isdir(local_item_path):
            upload_folder(sftp, local_item_path, remote_item_path)
        else:
            with open(local_item_path, 'rb') as local_file:
                local_file_size = os.path.getsize(local_item_path)
                with tqdm(total=local_file_size, unit='B', unit_scale=True, desc=item) as pbar:
                    def callback(bytes_transferred, bytes_total):
                        pbar.update(bytes_transferred - pbar.n)

                    sftp.put(local_item_path, remote_item_path, callback=callback)
            print(f'--- Uploaded {local_item_path} to {remote_item_path} ---')

def upload_games() -> None:
    """
    Prompts the user to upload game directories to a remote server.

    Returns:
    None
    """

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
    print('\n\nPick the game you want to upload to the server by typing its ID (press enter to quit):')
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

    game_type, game_name, _ = id_to_game[game_id]

    while True:
        response = input(f'\nDo you want to upload {game_name} to {server_ip}:{server_port}? [y/N]\n').upper()

        if response == 'Y':
            remote_path = os.path.join(configs['games_folder'], game_type, game_name)
            local_path = os.path.join(games_folder, game_type, game_name)

            # Attempt to get the remote file's access time
            try:
                remote_file_attr = sftp.stat(remote_path)
                remote_atime = float(remote_file_attr.st_atime)
            except FileNotFoundError:
                remote_atime = 0

            # Check if the local file exists and get its access time
            local_atime = 0
            if os.path.exists(local_path):
                local_atime = float(os.path.getatime(local_path))

            while True:
                # Check which file is more recently accessed between local and remote ones
                if remote_atime <= local_atime and local_atime > 0 and remote_atime > 0:
                    response = input(f'Your {game_name} files have been accessed more recently than the server\'s one. Do you want to overwrite the remote files? [y/N]: ').upper()
                elif remote_atime > local_atime and local_atime > 0 and remote_atime > 0:
                    response = input(f'Your {game_name} files have been accessed less recently than the remote ones. Do you want to overwrite the remote files? [y/N]: ').upper()
                else:
                    response = 'Y'

                if response == 'Y':
                    upload_folder(sftp, local_path, remote_path)
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