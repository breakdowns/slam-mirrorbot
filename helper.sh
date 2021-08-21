#! /bin/bash

# Made with ❤ by @SpeedIndeed - Telegram

printf "This is an interactive script that will help you in deploying Slam- Mirrorbot. What do you want to do?
1) Deploying first time
2) Redeploying but already have credentials.json, token.pickle and SA folder (optional)
3) Just commiting changes to existing repo"
while true; do
	read -p "Select one of the following: " choice
	case $choice in
            "1")
                echo "Firstly we will login to heroku"
				echo
				for (( ; ; ))
				do
					echo "Enter your Heroku credentials: "
					heroku login -i
					status=$?
					if test $status -eq 0; then
						echo "Signed in successfully"
					break
					fi
					echo "Invalid credentials, try again"
				done
				for (( ; ; ))
				do
					read -p "Enter unique appname for your bot: " bname
					heroku create $bname
					status=$?
					if test $status -eq 0; then
						echo "App created successfully"
					break
					fi
					echo "Appname is already taken, choose another one"
				done
				heroku git:remote -a $bname
				heroku stack:set container -a $bname
				pip3 install -r requirements-cli.txt
				pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
				echo
				echo "Now we will create credentials.json"
				echo "For that, follow TUTORIAL 1 given in this post: https://telegra.ph/Deploying-your-own-Slam-Mirrorbot-08-18#TUTORIAL-1"
				for (( ; ; ))
				do
					read -p "After adding credentials.json, Press y" cred
					if [ $cred = y -o $cred = Y ] ; then
						echo "Now we will create token.pickle. Follow the instructions given."
						python -m pip install google-auth-oauthlib
						python3 generate_drive_token.py
						echo
						echo "Service Accounts (SA) help you bypass daily 750GB limit when you want to upload to Shared Drive/Team Drive (TD). Keeping this in mind, select one of the following: "
						echo "1) You don't have SA but want to use them?"
						echo "2) You already have SA and want to use them?"
						echo "3) You don't want to add SA "
						read -p "Enter your choice: " sa
						if [ $sa = 1 ] ; then
							python -m pip install progress
							python3 gen_sa_accounts.py --quick-setup 1 --new-only
							echo
						fi
						if [ $sa = 2 ] ; then
							echo "Choose the project id which contains SA"
							python3 gen_sa_accounts.py --list-projects
							read -p "Project id: " pid
							python3 gen_sa_accounts.py --download-keys $pid
							echo
						fi
						if [ $sa = 1 -o $sa = 2 ] ; then
							echo "As you can see, a folder named 'accounts' has been created and contains 100 SA. Now, how do you want to add these SA to your TD?"
							echo "1) Directly add them to the TD"
							echo "2) Make a Google Group and add all SA to it"
							while true ; do
								read -p "Enter your choice: " way
								case $way in
									"1")
										echo "Enter your Team Drive id"
										echo "(HINT- If your TD link is like 'https://drive.google.com/drive/folders/0ACYsMW75QbTSUk9PVA' then your TD id = 0ACYsMW75QbTSUk9PVA"
										read -p "TD id: " id
										python3 add_to_team_drive.py -d $id
										echo "Now you can goto your TD and see that 100 SA have been added"
										echo "Don't forget to set USE_SERVICE_ACCOUNTS to 'True'"
										break
									;;
									"2")
										cd accounts
										grep -oPh '"client_email": "\K[^"]+' *.json > emails.txt
										cd -
										echo "For that, follow TUTORIAL 2 given in this post: https://telegra.ph/Deploying-your-own-Slam-Mirrorbot-08-18#TUTORIAL-2"
										break
									;;
									*)
										echo "Invalid choice"
									;;
								esac
							done
						break
						fi
						if [ $sa = 3 ] ; then
							echo "No problem, lets proceed further"
							echo
						break
						fi
						for (( ; ; ))
						do
							read -p "After filling all required vars in config.env, press y : " conf
							if [ $conf = y -o $conf = Y ] ; then
								echo "So lets proceed further"
								echo
								echo "Now we will push this repo to heroku, for that"
								read -p "Enter the mail which you used for heroku account: " mail
								read -p "Enter your name: " name
								git add -f .
								git config --global user.email "$mail"
								git config --global user.name "$name"
								git commit -m "First Deployment"
								git push heroku master --force
								heroku ps:scale web=0 -a $bname
								heroku ps:scale web=1 -a $bname
							break
							else 
								echo "Then do it first!"
							fi
						done
					break
					else
						"Then add it first!"
					fi
				done
			;;
            "2")
				for (( ; ; ))
				do
					read -p "After adding credentials.json, token.pickle, SA folder (optional) and all necessary vars in config.env, press y): " req
					if [ $req = y -o $req = Y ] ; then
						for (( ; ; ))
						do
							read -p "Enter unique appname for your bot: " bname
							heroku create $bname
							status=$?
							if test $status -eq 0; then
								echo "App created successfully"
							break
							fi
						echo "Appname is already taken, choose another one"
						done
					read -p "Enter the mail which you used for heroku account: " mail
					read -p "Enter your name: " name
					heroku create $bname
					heroku git:remote -a $bname
					heroku stack:set container -a $bname
					git add -f .
					git config --global user.email "$mail"
					git config --global user.name "$name"
					git commit -m "First Deployment"
					git push heroku master --force
					heroku ps:scale web=0 -a $bname
					heroku ps:scale web=1 -a $bname
				break
					else
						echo "Then do add it first!"
					fi
				done
			break
            ;;
            "3")
                read -p "Type your heroku appname: " bname
                read -p "Enter commit description in one line: " c_des
                git add -f .
                git commit -m "$c_des"
                git push heroku master --force
                heroku ps:scale web=0 -a $bname
                heroku ps:scale web=1 -a $bname
			break
            ;;
            *)
                echo "Invalid Choice"
            ;;
	esac
done
echo "Task completed successfully"