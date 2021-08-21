## Deploying slam-mirrorbot on Heroku with Github Workflows.

## Pre-requisites

- [Heroku](heroku.com) accounts
- Recommended to use 1 App in 1 Heroku accounts
- Don't use bin/fake credits card, because your Heroku account will banned

## Deployment

1. Give stars and Fork this repo then upload **token.pickle** to your forks, or you can upload your **token.pickle** to your Index and put your **token.pickle** link to **TOKEN_PICKLE_URL** (**NOTE**: If you didn't upload **token.pickle** uploading will not work). How to generate **token.pickle**? [Read here](https://github.com/Slam-Team/slam-mirrorbot#getting-google-oauth-api-credential-file)

2. Go to Repository `Settings` -> `Secrets`

	![secrets](https://telegra.ph/file/bb8cb0eced5caad68a41b.jpg)

3. Add the below Required Variables one by one by clicking `New Repository Secret` everytime.

	```
	HEROKU_EMAIL
	HEROKU_API_KEY
	HEROKU_APP_NAME
	CONFIG_FILE_URL
	```
- To get CONFIG_FILE_URL, check the steps here:

    ![steps 1 to 3](https://telegra.ph/file/1d8fec16516a87ba9d1ac.jpg)

    ![step 4](https://telegra.ph/file/1491f99836cd694ea1195.jpg)

    ![step 5](https://telegra.ph/file/416a550f7ded579b63272.jpg)

4. After adding all the above Required Variables go to Github Actions tab in your repo

5. Select `Manually Deploy to heroku` workflow as shown below:

	![Example Manually Deploy to Heroku](https://telegra.ph/file/38ffda0165d9671f1d5dc.jpg)

6. Then click on Run workflow

	![Run workflow](https://telegra.ph/file/c5b4c2e02f585cb59fe5c.jpg)

7. _Done!_ your bot will be deployed now.

## NOTE
- Don't change/edit variables from Heroku if you want to change/edit do it from Github Secrets
- If you want to set optional variables, go to your Heroku app settings and add the variables

## Credits
- [arghyac35](https://github.com/arghyac35) for Tutorial
