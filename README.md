[![Slam](https://telegra.ph/file/db03910496f06094f1f7a.jpg)](https://youtu.be/Pk_TthHfLeE)

# Slam Mirror Bot
This is a telegram bot writen in python for mirroring files on the internet to our beloved Google Drive.

## Getting Google OAuth API credential file

- Visit the [Google Cloud Console](https://console.developers.google.com/apis/credentials)
- Go to the OAuth Consent tab, fill it, and save.
- Go to the Credentials tab and click Create Credentials -> OAuth Client ID
- Choose Desktop and Create.
- Use the download button to download your credentials.
- Clone this repo:
```
git clone https://github.com/breakdowns/slam-mirrorbot mirrorbot/
cd mirrorbot
```
- Move that file to the root of mirrorbot, and rename it to credentials.json
- Visit [Google API page](https://console.developers.google.com/apis/library)
- Search for Drive and enable it if it is disabled
- Finally, run the script to generate token file (token.pickle) for Google Drive:
```
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
python3 generate_drive_token.py
```

## Deployment

Fork this repo, than upload credentials.json and token.pickle to your forks

<p><a href="https://heroku.com/deploy"> <img src="https://www.herokucdn.com/deploy/button.svg" alt="Deploy to Heroku" /></a></p>

## Features supported:
- Mirroring direct download links to Google Drive
- Mirroring Mega.nz links to google drive (In development stage)
- Copy files/folder from someone's drive to your drive
- Download/upload progress
- Download/upload speeds and ETAs
- Docker support
- Uploading To Team Drives.
- Index Link support
- Service account support
- Mirror all youtube-dl supported links
- Mirror telegram files
- Delete files from drive
- Add stickers to your pack
- Nyaa.si and Sukebei Torrent search
- Shell and Executor
- Shortener support
- Custom Buttons
- Speedtest with picture results
- Extract these filetypes and uploads to google drive
> ZIP, RAR, TAR, 7z, ISO, WIM, CAB, GZIP, BZIP2, 
> APM, ARJ, CHM, CPIO, CramFS, DEB, DMG, FAT, 
> HFS, LZH, LZMA, LZMA2, MBR, MSI, MSLZ, NSIS, 
> NTFS, RPM, SquashFS, UDF, VHD, XAR, Z.

## Using service accounts for uploading to avoid user rate limit
For Service Account to work, you must set USE_SERVICE_ACCOUNTS="True" in config file or environment variables
Many thanks to [AutoRClone](https://github.com/xyou365/AutoRclone) for the scripts
**NOTE:** Using service accounts is only recommended while uploading to a team drive.

## Generate [service accounts](https://cloud.google.com/iam/docs/service-accounts)

Let us create only the service accounts that we need. 
**Warning:** abuse of this feature is not the aim of this project and we do **NOT** recommend that you make a lot of projects, just one project and 100 sa allow you plenty of use, its also possible that over abuse might get your projects banned by google. 

```
Note: 1 service account can copy around 750gb a day, 1 project can make 100 service accounts so that's 75tb a day, for most users this should easily suffice. 
```

`python3 gen_sa_accounts.py --quick-setup 1 --new-only`

A folder named accounts will be created which will contain keys for the service accounts

NOTE: If you have created SAs in past from this script, you can also just re download the keys by running:
```
python3 gen_sa_accounts.py --download-keys project_id
```

## Add all the service accounts to the Team Drive
- Run:
```
python3 add_to_team_drive.py -d SharedTeamDriveSrcID
```

## Youtube-dl authentication using .netrc file
For using your premium accounts in youtube-dl, edit the [.netrc](https://github.com/breakdowns/slam-mirrorbot/blob/master/.netrc) file according to following format:
```
machine host login username password my_youtube_password
```
where host is the name of extractor (eg. youtube, twitch). Multiple accounts of different hosts can be added each separated by a new line

## Credits

Thanks to:
- [Izzy12](https://github.com/lzzy12/) for original repo
- [Dank-del](https://github.com/Dank-del/) for base repo
- [magneto261290](https://github.com/magneto261290/) for some features
- [SVR666](https://github.com/SVR666/) for some fixes
- [iamLiquidX](https://github.com/iamLiquidX/) for Speedtest module
- [4amparaboy](https://github.com/4amparaboy/) for some help

and many more people who aren't mentioned here, but may be found in [Contributors](https://github.com/breakdowns/slam-mirrorbot/graphs/contributors).
