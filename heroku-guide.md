## Deploying slam-mirrorbot on Heroku with Github Workflows.

## Pre-requisites

- [token.pickle](https://github.com/Slam-Team/slam-mirrorbot#getting-google-oauth-api-credential-file)
- [Heroku](heroku.com) accounts
- Recommended to use 1 App in 1 Heroku account
- Don't use bin/fake credits card, because your Heroku account will get banned.

## Deployment

1. Give a star and Fork this repo then upload **token.pickle** to your forks, or you can upload your **token.pickle** to your Index and put your **token.pickle** link to **TOKEN_PICKLE_URL** (**NOTE**: If you don't upload **token.pickle** uploading will not work).

2. Go to Repository `Settings` -> `Secrets`

	![secrets](https://telegra.ph/file/bb8cb0eced5caad68a41b.jpg)

3. Add the below Required Variables one by one by clicking `New Repository Secret` everytime.

	* `HEROKU_EMAIL` Heroku Account Email Id in which the above app will be deployed
	* `HEROKU_API_KEY` Your Heroku API key, get it from https://dashboard.heroku.com/account
	* `HEROKU_APP_NAME` Your Heroku app name, Name Must be unique
	* `CONFIG_FILE_URL` Fill [This](https://raw.githubusercontent.com/Slam-Team/slam-mirrorbot/master/config_sample.env) in any text editor, and remove the second line. Go to https://gist.github.com and paste your config data from the previous step. Rename the file to config.env and upload it. Click on Raw, copy the link and that's your CONFIG_FILE_URL. Refer to below images for clarity. 

	![steps 1 to 3](https://telegra.ph/file/1d8fec16516a87ba9d1ac.jpg)

	![step 4](https://telegra.ph/file/1491f99836cd694ea1195.jpg)

	![step 5](https://telegra.ph/file/416a550f7ded579b63272.jpg)

4. After adding all the above Required Variables go to Github Actions tab in your repo

5. Select `Manually Deploy to Heroku` workflow as shown below:

	![Example Manually Deploy to Heroku](https://telegra.ph/file/38ffda0165d9671f1d5dc.jpg)

6. Then click on Run workflow

	![Run workflow](https://telegra.ph/file/c5b4c2e02f585cb59fe5c.jpg)

7. _Done!_ your bot will be deployed now.

## NOTE
- Don't change/edit variables from Heroku if you want to change/edit do it from `config.env`

## Credits
- [arghyac35](https://github.com/arghyac35) for Tutorial
