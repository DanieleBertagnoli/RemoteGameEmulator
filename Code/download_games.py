import os
import yaml
import paramiko
from tqdm import tqdm
from utils import *
from stat import S_ISDIR

CURRENT_DIR = find_base_dir()

# Load configs
CONFIGS_PATH = os.path.join(CURRENT_DIR, '..', 'configs.yml')
with open(CONFIGS_PATH, 'r') as f:
    configs = yaml.safe_load(f)

configs = dict(configs)

def download_folder(sftp, remote_folder, local_folder):
    if not os.path.exists(local_folder):
        os.makedirs(local_folder)
        print(f'Created local directory {local_folder}')

    for item in sftp.listdir_attr(remote_folder):
        remote_item_path = os.path.join(remote_folder, item.filename)
        local_item_path = os.path.join(local_folder, item.filename)

        if S_ISDIR(item.st_mode):
            download_folder(sftp, remote_item_path, local_item_path)
        else:
            remote_file_size = item.st_size
            with sftp.file(remote_item_path, 'rb') as remote_file:
                with open(local_item_path, 'wb') as local_file:
                    with tqdm(total=remote_file_size, unit='B', unit_scale=True, desc=item.filename) as pbar:
                        while True:
                            data = remote_file.read(32768)
                            if not data:
                                break
                            local_file.write(data)
                            pbar.update(len(data))
            print(f'--- Downloaded {item.filename} ---')

def download_games() -> None:
    """
    Prompts the user to download game directories or files from a remote server.

    Returns:
    None
    """

    # Ensure the Games folder exists locally
    games_folder = os.path.join(CURRENT_DIR, '..', 'Games')

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

    game_type, game_name, _ = id_to_game[game_id]
    while True:
        response = input(f'\nDo you want to download {game_name} from {server_ip}:{server_port}? [Y/n]\n').upper()

        if response == 'Y' or response == '':
            remote_path = os.path.join(configs['games_folder'], game_type, game_name)
            local_path = os.path.join(games_folder, game_type, game_name)

            # Attempt to get the remote file's access time
            try:
                remote_file_attr = sftp.stat(remote_path)
                remote_atime = float(remote_file_attr.st_atime)
            except FileNotFoundError:
                print(f'Error: Remote file {remote_path} not found.')
                continue

            # Check if the local file exists and get its access time
            local_atime = 0
            if os.path.exists(local_path):
                local_atime = float(os.path.getatime(local_path))

            while True:
                # Check which file is more recently accessed between local and remote ones
                if remote_atime > local_atime and local_atime > 0:
                    response = input(f'You already have {game_name}, it seems that your files have been accessed less recently. Do you want to overwrite your local files? [y/N]\n').upper()
                elif remote_atime <= local_atime and local_atime > 0:
                    response = input(f'You already have {game_name} and they have been accessed more recently than the server\'s one. Do you want to overwrite your local files? [y/N]\n').upper()
                else:
                    response = 'Y'

                if response == 'Y':
                    download_folder(sftp, remote_path, local_path)
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
