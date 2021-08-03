# About
* What is this repo?
> This is a slightly modified fork which includes some extra features & memes added to my liking.
* How's this different from the main repo?
> Since the `list` module in the main repo doesn't have recursive search support, I integrated **SearchX-bot**'s search module into this. You can now search for files/folders in more than one drive.  

> **Note**: I did **not** integrate the main repo's **Shortener** feature to the search module, since I personally don't like shortened links in my search results.
* What're those extra features?
> * I've made some tiny improvements to the search module, such as:  
>   * Time taken to fetch the results
>   * Number of results found  
> * Added support to the `/mirror` command to automatically fetch & download an URL when replied to a certain message. Magnet, Torrent, Mega & Direct links are supported.

# How to deploy?

* Clone this repository & navigate to it's directory.
* Open `drive_folder` using your desired text editor & add the drive names & drive IDs separated by a space to the cloned folder.
* If your drive name includes a **space**, replace it with an **underscore** as shown in the format below.

Format:

```
drive_name drive_id
```

Example:

```
sample_drive 0ASbFU2s497sDUk1PVA
```
* Visit the repo(s) below for further instructions.

# Credits

Projects used in the making:

* [slam-aria-mirror-bot](https://github.com/breakdowns/slam-aria-mirror-bot)
* [SearchX-bot](https://github.com/SVR666/SearchX-bot)

BTW, here's a cute picture of [Hishiro](https://i.imgur.com/QPkgVg6.png).