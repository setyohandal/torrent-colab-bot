# torrent-colab-bot
This project involves creating a Telegram bot that allows users to download torrents using Google Colab. By leveraging the computational power and cloud storage capabilities of Google Colab, the bot provides a convenient and efficient way to manage torrent downloads directly from a Telegram chat interface.

# Tutorial
**Setting your telegram bot**
- Open the Telegram app and search for the BotFather (@BotFather).
- Start a chat with the BotFather and use the command /mybots to list your bots.
- Select the bot for which you need a new token.
- Use the /token command to generate a new token. The BotFather will provide a new token in the chat.
- Open the config.cfg file located in your computer directory.
- Locate the section where the Telegram bot token is stored.
- Replace **YOUR TOKEN HERE** with the new token provided by the BotFather.

**Set your Google Colab Notebook and download torrent from telegram**
- Upload all files from repository to your drive.
- Open "Torrent_GDriveuploader.ipynb" which will then be directed to Google Colab.
- Run all runtime.
- To download torrent file, paste magnet link on telegram bot chat.
- Use the command "/list" to see the list active torrents and "/cancel" to cancel downloading torrents.
