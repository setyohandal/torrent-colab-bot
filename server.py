import re
import libtorrent as lt
import time
import datetime
import threading
from bot import telegram_chatbot

# Initialize libtorrent session with settings
settings = {
    'listen_interfaces': '0.0.0.0:6881',
}
ses = lt.session(settings)

# Parameters for the torrent
params = {
    'save_path': '/content/drive/My Drive/Torrent/',
    'storage_mode': lt.storage_mode_t.storage_mode_sparse
}

# Initialize the Telegram bot
bot = telegram_chatbot("config.cfg")
pattern = re.compile(r'magnet:\?xt=urn:btih:[a-zA-Z0-9]*')

# Dictionary to keep track of active torrent handles
active_torrents = {}

def download_torrent(magnet_link, from_):
    atp = lt.add_torrent_params()
    atp.save_path = params['save_path']
    atp.storage_mode = params['storage_mode']
    atp.url = magnet_link
    handle = ses.add_torrent(atp)
    ses.start_dht()

    begin = time.time()
    print(datetime.datetime.now())
    print('Downloading Metadata...')
    
    while not handle.has_metadata():
        time.sleep(1)
    
    print('Got Metadata, Starting Torrent Download...')
    print("Starting", handle.name())
    startreply = f'Download started for {handle.name()}'
    bot.send_message(startreply, from_)
    
    # Store the handle using the torrent's info hash as the key
    active_torrents[str(handle.info_hash())] = handle

    # Keep track of last progress sent to avoid spamming
    last_progress = 0
    
    while handle.status().state != lt.torrent_status.seeding:
        s = handle.status()
        state_str = ['queued', 'checking', 'downloading metadata', 'downloading', 'finished', 'seeding', 'allocating']
        progress = s.progress * 100
        progress_bar = f"[{'=' * int(progress / 5)}{' ' * (20 - int(progress / 5))}] {progress:.2f}%"

        # Send progress update if there's a significant change (more than 5%)
        if progress - last_progress >= 5:
            bot.send_message(f'{progress_bar} complete (down: {s.download_rate / 1000:.1f} kB/s up: {s.upload_rate / 1000:.1f} kB/s peers: {s.num_peers}) {state_str[s.state]}', from_)
            last_progress = progress
        
        print(f'{progress:.2f}% complete (down: {s.download_rate / 1000:.1f} kB/s up: {s.upload_rate / 1000:.1f} kB/s peers: {s.num_peers}) {state_str[s.state]}')
        time.sleep(5)

    end = time.time()
    print(f'{handle.name()} COMPLETE')
    print(f'Elapsed Time: {int((end - begin) // 60)} min : {int((end - begin) % 60)} sec')
    print(datetime.datetime.now())
    
    reply = 'Download Finished. You can find the downloaded file at https://drive.google.com/drive/folders/**YOUR FOLDER URL**'
    bot.send_message(reply, from_)

def make_reply(msg, from_):
    if re.match(pattern, msg):
        threading.Thread(target=download_torrent, args=(msg, from_)).start()
        return "Torrent download started in the background."
    elif msg.startswith('/list'):
        return list_active_torrents()
    elif msg.startswith('/cancel'):
        if len(msg.split(' ', 1)) < 2:
            return "Please provide the torrent name or hash to cancel."
        torrent_name_or_hash = msg.split(' ', 1)[1]
        return cancel_torrent(torrent_name_or_hash)
    else:
        return "Invalid magnet link or command"

def list_active_torrents():
    if not active_torrents:
        return "No active torrents."
    
    reply = "Active torrents:\n"
    for info_hash, handle in active_torrents.items():
        reply += f"{handle.name()} (hash: {info_hash})\n"
    return reply

def cancel_torrent(torrent_name_or_hash):
    print(f"Attempting to cancel torrent: {torrent_name_or_hash}")
    for info_hash, handle in active_torrents.items():
        print(f"Checking torrent: {handle.name()} with hash: {info_hash}")
        if handle.name() == torrent_name_or_hash or info_hash == torrent_name_or_hash:
            ses.remove_torrent(handle, option=lt.options_t.delete_files)
            del active_torrents[info_hash]
            print(f"Torrent {handle.name()} has been canceled and removed.")
            return f'Torrent {handle.name()} has been canceled and removed.'
    return f'No active torrent found with name or hash: {torrent_name_or_hash}'

def handle_updates():
    update_id = None
    while True:
        updates = bot.get_updates(offset=update_id)
        updates = updates.get("result", [])
        if updates:
            for item in updates:
                update_id = item["update_id"]
                message = item["message"].get("text")
                from_ = item["message"]["from"]["id"]
                if message:
                    reply = make_reply(message, from_)
                    if reply:
                        bot.send_message(reply, from_)

if __name__ == '__main__':
    handle_updates()
