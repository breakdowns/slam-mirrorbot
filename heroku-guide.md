<div align="center">
<h1>Deploying slam-mirrorbot on Heroku with Github Workflows.</h3>
</div>

## Pre-requisites

- Give stars and Fork this repo then upload **token.pickle** to your forks, or you can upload your **token.pickle** to your Index and put your **token.pickle** link to **TOKEN_PICKLE_URL** (**NOTE**: If you didn't upload **token.pickle** uploading will not work). How to generate **token.pickle**? [Read here](https://github.com/breakdowns/slam-tg-mirror-bot#getting-google-oauth-api-credential-file)
- Recommended to use 1 App in 1 Heroku accounts
- Don't use bin/fake credits card, because your Heroku account will banned

## Deployment

1. Go to Repository `Settings` -> `Secrets`
2. Set the below Variables in the **Github Repository Secrets** [Environmental Variables](#environment-variables)
3. After adding all the above required variables go to github Actions tab in your repo
4. Select `Manually Deploy to heroku` workflow
5. Then click on Run workflow
6. Done! Your bot will be deployed now.

# Environment Variables

## Required Environment
```
• HEROKU_EMAIL: Your Heroku email.
• HEROKU_API_KEY: Your Heroku API key, get it from https://dashboard.heroku.com/account.
• HEROKU_APP_NAME: Your Heroku app name.
• BOT_TOKEN: The Telegram bot token that you get from https://t.me/BotFather.
• TELEGRAM_API: This is to authenticate to your Telegram account for downloading Telegram files. You can get this from https://my.telegram.org DO NOT put this in quotes.
• TELEGRAM_HASH: This is to authenticate to your Telegram account for downloading Telegram files. You can get this from https://my.telegram.org
• OWNER_ID: The Telegram user ID (not username) of the Owner of the bot
• GDRIVE_FOLDER_ID: This is the folder ID of the Google Drive Folder to which you want to upload all the mirrors.
• DOWNLOAD_DIR: The path to the local folder where the downloads should be downloaded to
• DOWNLOAD_STATUS_UPDATE_INTERVAL: A short interval of time in seconds after which the Mirror progress message is updated. (I recommend to keep it `5` seconds at least)  
• AUTO_DELETE_MESSAGE_DURATION: Interval of time (in seconds), after which the bot deletes it's message (and command message) which is expected to be viewed instantly. (Note: Set to -1 to never automatically delete messages)
• UPSTREAM_REPO: Link for Bot Upstream Repo, if you want default update, fill https://github.com/breakdowns/slam-tg-mirror-bot.
• UPSTREAM_BRANCH: Branch name for Bot Upstream Repo, fill `master`.
```

## Not Required Environment
For other vars you can get from [Here](https://github.com/breakdowns/slam-tg-mirror-bot#setting-up-config-file)
