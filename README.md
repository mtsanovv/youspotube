# youspotube
Keep in sync all your Spotify playlists with your YouTube playlists.

![build](https://img.shields.io/github/actions/workflow/status/mtsanovv/youspotube/checks.yml?branch=master)
![latest download](https://img.shields.io/github/v/release/mtsanovv/youspotube?style=flat)

## Before reading on...
This was a side project that I created in order to keep my own playlists in sync and therefore I might not have covered all Spotify/YouTube playlist features due to my limited usage of those. If you need something extra, create a PR or let me know.

## Setting up the first run
1. Create your own [Spotify](https://www.codeproject.com/Tips/5276627/HowTo-Setup-a-Spotify-API-App-in-the-Spotify-Devel) and [YouTube](https://wpythub.com/documentation/getting-started/set-youtube-oauth-client-id-client-secret/) OAuth applications (development mode for each is fine) and obtain their client IDs & secrets.
    - When setting up the Spotify application, you only need to set http://localhost:4466 as callback URL so that youspotube can fetch back its authorization tokens.
    - When setting up the YouTube application, set it as a Desktop application so that you don't have to enter any URLs. Generally, you don't have to enter any specific information (besides a couple names and descriptions), just make sure that your Google account's email to the list of users that have access to the application, otherwise later, when you have to authenticate via your browser, you won't have access.
2. Copy config.yml.dist to the directory where you'll be running the python command that launches the app (or the youspotube binary, respectively) and rename it to config.yml.
    - In the config, change the `origin` parameter in it to `youtube` or `spotify`, depending on which site you would like to sync from. *You can also change that later if you wish to sync the other way around.*
    - Set the client IDs and secrets to the ones obtained in step 1. This setting is meant to be set-it-and-forget-it.
    - Setup the `playlists` you would like to synchronize (make sure you have read & write access to them in YouTube/Spotify as well). Provide their YouTube playlist IDs and Spotify playlist IDs. Here is a sample configuration layout for the `playlists` parameter:
        ```
        playlists:
            Various:
                youtube: youtube_various_playlist_id
                spotify: spotify_various_playlist_id
            Pop:
                youtube: youtube_pop_playlist_id
                spotify: spotify_pop_playlist_id
        ```
    - *Optional:* Tie song IDs with `tied_songs` between YouTube and Spotify in case you have preferred matches for a given title. This setting is rather useful after you run the sync for the first time and you would like to have specific Spotify track ID and YouTube video ID to be used instead of whatever the search engine of the site you're synchronizing to (opposite of `origin`) recommended. Sample configuration for `tied_songs`:
        ```
        tied_songs:
            Taylor Swift - I Knew You Were Trouble:
                youtube: TqAollrUJdA
                spotify: 6FB3v4YcR57y4tXFcdxI1E
            Mr Kitty - After Dark:
                youtube: Cl5Vkd4N03Q
                spotify: 0zCgWGmDF0aih5qexATyBn
        ```

## Running youspotube

Open up a Terminal, navigate to a released binary of youspotube that you have downloaded for your platform and run it.

Alternatively, if you know what you're doing, you can run it with python3 from the directory you've cloned this repository in. First, make sure you have all the requirements installed:

```
$ pip3 install -r requirements.txt
```

and then run it:

```
# python3 ./src/ysptb.py
```

**Note:** When running youspotube for the first time (or you don't have the `.spotify_cache` and `.youtube_cache` files), make sure that you'll run them on a machine with a functional browser that you will use to log on to the accounts that have access to your YouTube and Spotify applications from step 1 of 'Setting up the first run.'

## Running youspotube on a server

As mentioned previously, you need to obtain the `.spotify_cache` and `.youtube_cache` files during your first run. In case you have GUI access to your server and it has a browser that you can use to authenticate with Google and YouTube, that's fine. In case you don't, you'll need to run youspotube on a machine with a functional browser and after you authenticate, you can cancel the youspotube run, copy the two cache files and put them on your server. This way, youspotube will be able to use the generated tokens and you'll basically never have to re-authenticate with Google/YouTube again, just like you wouldn't on a regular machine.

**Note:** Make sure to remove/move/rename the two cache files on the machine you used to generate them (essentially, keep them with their original names only where you'll use them) in order to avoid authentication token changes.

## For your development purposes

In case you want to develop something for youspotube, you might find some of the following commands useful (most of them are executed automatically as checks when pushing to dev or creating a PR to master):

- Linting with flake8 (you might need to install the extra python module `flake8`) for syntax errors/undefined names:
    ```
    $ python3 -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    ```
- Linting with flake8 (you might need to install the extra python module `flake8`) for code standards:
    ```
    $ python3 -m flake8 . --max-complexity=10 --max-line-length=127
    ```
- Running unit tests with coverage (you might need to install the extra python module `coverage`) and generating coverage HTML report to see what remains untested (the report is located in `htmlcov/index.html` after that):
    ```
    $ python3 -m coverage run --source=./src -m unittest -v ; python3 -m coverage html
    ```
- Creating an executable (you might need to install the extra python module `PyInstaller`) for your OS & CPU architecture:
    ```
    $ python3 -m PyInstaller -F --name ysptb --paths ./src ./src/ysptb.py
    ```


## Important remarks
- Bidirectional synchronization is not available due to the fact that it becomes extremely messy when it comes to YouTube's search algorithm producing results for Spotify's search algorithm and vice-versa. **It is recommended to maintain manually your playlists on one specific platform that you find yourself most comfortable using and setting it as `origin`.** For example, I listen to music when I'm on my laptop on YouTube, I update my playlists on YouTube and whenever I use my cellular data on my phone I use Spotify to listen to music, so I have set `origin: youtube` in the configuration file and I will have my Spotify playlists synchronized with everything I add to my YouTube playlists.
- During synchronization, no playlist items will be deleted from playlists. This is due to the fact that the YouTube API quota cost for deleting of videos in playlists is too high (in fact, the same as adding an item to a playlist). Although Spotify is fine with deleting as much items as you want, I wanted to keep this behavior consistent with the YouTube synchronizations. In case you have removed a specific track/video from a playlist, you'll need to remove it from the other platform manually, unfortunately.
- The total amount of songs that can be added to YouTube playlists per day with one client ID/client secret (at the time of writing) is around 185. The YouTube quota limit per day is 10K units, and one song addition to playlist costs 50 units. The YouTube API starts throwing quotaExceeded when you're close to reaching 9.5K units, though. One more reason to use `origin: youtube` - there's currently no such limitations on Spotify!
- If you're using `origin: spotify`, it is important to know that the YouTube quota count resets sometime around 00:00 Central Time, so you can use the two synchronizations shortly before and shortly after in order to be able to synchronize more songs. Of course, if you get your quota extended by YouTube, you won't really need this.

*M. Tsanov, 2022*
