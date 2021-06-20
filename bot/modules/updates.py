# Implement By https://github.com/jusidama18
# Based on this https://github.com/DevsExpo/FridayUserbot/blob/master/plugins/updater.py

import sys
import subprocess
import heroku3

from datetime import datetime
from os import environ, execle, path, remove

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError

from pyrogram import filters

from bot import app, OWNER_ID, UPSTREAM_REPO, UPSTREAM_BRANCH
from bot.helper import runcmd, get_text, HEROKU_URL
from bot.helper.telegram_helper.bot_commands import BotCommands

REPO_ = UPSTREAM_REPO
BRANCH_ = UPSTREAM_BRANCH

# Update Command

@app.on_message(filters.command(BotCommands.UpdateCommand) & filters.user(OWNER_ID))
async def update_it(client, message):
    msg_ = await message.reply_text("`Updating Please Wait!`")
    try:
        repo = Repo()
    except GitCommandError:
        return await msg_.edit(
            "**Invalid Git Command. Please Report This Bug To [Support Group](https://t.me/SlamMirrorSupport)**"
        )
    except InvalidGitRepositoryError:
        repo = Repo.init()
        if "upstream" in repo.remotes:
            origin = repo.remote("upstream")
        else:
            origin = repo.create_remote("upstream", REPO_)
        origin.fetch()
        repo.create_head(UPSTREAM_BRANCH, origin.refs.master)
        repo.heads.master.set_tracking_branch(origin.refs.master)
        repo.heads.master.checkout(True)
    if repo.active_branch.name != UPSTREAM_BRANCH:
        return await msg_.edit(
            f"`Seems Like You Are Using Custom Branch - {repo.active_branch.name}! Please Switch To {UPSTREAM_BRANCH} To Make This Updater Function!`"
        )
    try:
        repo.create_remote("upstream", REPO_)
    except BaseException:
        pass
    ups_rem = repo.remote("upstream")
    ups_rem.fetch(UPSTREAM_BRANCH)
    if not HEROKU_URL:
        try:
            ups_rem.pull(UPSTREAM_BRANCH)
        except GitCommandError:
            repo.git.reset("--hard", "FETCH_HEAD")
        await runcmd("pip3 install --no-cache-dir -r requirements.txt")
        await msg_.edit("`Updated Sucessfully! Give Me Some Time To Restart!`")
        with open("./aria.sh", 'rb') as file:
            script = file.read()
        subprocess.call("./aria.sh", shell=True)
        args = [sys.executable, "-m", "bot"]
        execle(sys.executable, *args, environ)
        exit()
        return
    else:
        await msg_.edit("`Heroku Detected! Pushing, Please wait!`")
        ups_rem.fetch(UPSTREAM_BRANCH)
        repo.git.reset("--hard", "FETCH_HEAD")
        if "heroku" in repo.remotes:
            remote = repo.remote("heroku")
            remote.set_url(HEROKU_URL)
        else:
            remote = repo.create_remote("heroku", HEROKU_URL)
        try:
            remote.push(refspec="HEAD:refs/heads/master", force=True)
        except BaseException as error:
            await msg_.edit(f"**Updater Error** \nTraceBack : `{error}`")
            return repo.__del__()
        await msg_.edit(f"`Updated Sucessfully! \n\nCheck your config with` `/{BotCommands.ConfigMenuCommand}`")
