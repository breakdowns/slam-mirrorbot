## Deploying slam-mirrorbot on Heroku with Github Workflows.

## Pre-requisites

- [Token Pickle](https://github.com/SlamDevs/slam-mirrorbot#getting-google-oauth-api-credential-file)
- [Heroku](heroku.com) accounts. **NOTE**: Recommended to use 1 App in 1 Heroku account and Don't use bin/fake credits card, because your Heroku account will get banned.

## Deployment

1. Give a star and Fork this repo then upload **token.pickle** to your forks, or you can upload your **token.pickle** to your Index and put your **token.pickle** link to `TOKEN_PICKLE_URL` (**NOTE**: If you don't upload **token.pickle** uploading will not work).

2. Go to Repository `Settings` -> `Secrets`

	![secrets](https://telegra.ph/file/bb8cb0eced5caad68a41b.jpg)

3. Add the below Required Variables one by one by clicking `New Repository Secret` everytime.

	* `HEROKU_EMAIL` Heroku Account Email Id in which the above app will be deployed
	* `HEROKU_API_KEY` Your Heroku API key, get it from https://dashboard.heroku.com/account
	* `HEROKU_APP_NAME` Your Heroku app name, Name Must be unique
	* `CONFIG_FILE_URL` Fill [This](https://raw.githubusercontent.com/Slam-Team/slam-mirrorbot/master/config_sample.env) in any text editor. Remove the `_____REMOVE_THIS_LINE_____=True` line and fill the variables. For details about config you can see [Here](https://github.com/SlamDevs/slam-mirrorbot#setting-up-config-file). Go to https://gist.github.com and paste your config data. Rename the file to `config.env` then create secret gist. Click on Raw, copy the link. This will be your `CONFIG_FILE_URL`. Refer to below images for clarity. 

	![steps 1 to 3](https://telegra.ph/file/1d8fec16516a87ba9d1ac.jpg)

	![step 4](https://telegra.ph/file/1491f99836cd694ea1195.jpg)

	![step 5](https://telegra.ph/file/416a550f7ded579b63272.jpg)

	* **NOTE**: Remove commit id from raw link to be able to change variables without updating the `CONFIG_FILE_URL` in secrets. should be in this form: https://gist.githubusercontent.com/username/gist-id/raw/config.env
	* Before: https://gist.githubusercontent.com/anasty17/8cce4a4b4e7f4ea47e948b2d058e52ac/raw/19ba5ab5eb43016422193319f28bc3c7dfb60f25/config.env
	* After: https://gist.githubusercontent.com/anasty17/8cce4a4b4e7f4ea47e948b2d058e52ac/raw/config.env
	* You only need to restart your bot after editing `config.env` gist secret.

4. After adding all the above Required Variables go to Github Actions tab in your repo

5. Select `Manually Deploy to Heroku` workflow as shown below:

	![Example Manually Deploy to Heroku](https://telegra.ph/file/38ffda0165d9671f1d5dc.jpg)

6. Then click on Run workflow

	![Run workflow](https://telegra.ph/file/c5b4c2e02f585cb59fe5c.jpg)

7. **Done!** your bot will be deployed now.

## NOTE
- Don't change/edit variables from Heroku if you want to change/edit do it in `config.env` from your gist.

## Credits
- [`arghyac35`](https://github.com/arghyac35) for Tutorial
- [`AkhileshNS`](https://github.com/AkhileshNS) for Github Workflow method to deploy Heroku app
