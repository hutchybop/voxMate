# voxMate


##### Change to openwakeword
- [ ] Train a custom model '**hey voxmate**'
<br>

##### Console logger prints
- [ ] look at and fix random errors
- [ ] Align logger more to output **horse-racing-game** has
<br>

##### Internet search
- [ ] Research internet searches with AI for up to date information. 
<br>

##### Time functions
- [ ] Add timers
    - [ ] Add to timer
    - [ ] Remove from timer
- [ ] Add alarms
<br>

##### News and whether
- [ ] Add news and whether apis
<br>

##### Radio
- [ ] Add radio
<br><br>

-----

## Completed

##### Settings page
- [x] Submit button
- [x] Test submission 
- [x] Ensure db is updated
- [x] Add error handling and user feedback
- [x] Commit
##### Flash
- [x] Setup flash on the boilerplate
- [x] Test flash
##### T&Cs and Cookie Policy 
- [x] Write app specific T&Cs and cookie policy
- [x] Setup T&C route and page
- [x] Set up cookie policy route and page
- [x] Add alert in boilerplate for user to accept policy/T&Cs
- [x] Add local storage variable for it accepted or not
- [x] Test
- [x] Commit
##### About page / readme.md
- [x] Correct the spacing
- [x] Fix extra space in code blocks
- [x] Correct the flow and make sure it is logical
- [x] Commit
##### Web app page layout
- [x] Change index to about page
##### API page
Do I need this?
They will need their own db anyway. 
- [x] On first run if no api keys play audio warning user to add one using web app
- [x] Add warning on settings page, (maybe all pages) if no API keys set
- [x] Warning for no db? 
- [x] Commit
##### Test settings are properly used in voxMate.py
- [x] Debug porcupine wake word
- [x] Test voxMates runs with no setting config set
- [x] See if web app access works on pi
- [x] Change user setting on web app and test voxMate
    - [x] Debug user settings not taking affect
- [x] Remove Mongodb URI from .env and test warning is played and default values used
- [x] Remove Groq API key from .env and test warning is played and app stops
- [x] Remove porcupine API key from .env and test warning is played and app stops
##### Porcupine .ppn
- [x] Fine a way to keep Porcupine files on server even with git pull
- [x] Add .pp file name to .env
- [x] Test
##### User Settings
- [x] See if there is a away to update settings while voxMate is running (line 409)
- [x] Try io socket?
- [x] Add app state to show waiting for wake word or not
    - [x] Look at reverting code for efficiency - its now slow
- [x]  Add setting to display volume
- [x] Remove ’submit’ field from being updated to db from settings
    - [x] Test 
- [x] Ensure voulme_display take affect while voxMate running
- [x] Ensure noise_reduction take affect while voxMate running
##### Spotify
- [x] Test Spotify controls
    - [x] Playback
    - [x] Get playlist info
- [x] Play music on the rpi using raspotify
- [x] Create login
- [x] Create logout
- [x] Add links
- [x] Add proper profile page
- [x] Test logging in and out
- [x] Wait an hour see if token refreshes - 17:20
##### voxMate.py modularisation
- [x] Debug the new code structure
- [x] Confirm file locations in voxMate_app - use Path
- [x] Confirm config (userConfig file calls) in app and web_appAdd Spotify control to voxMate
- [x] Setup voxmate.longrunner.co.uk
    - [x] Add and setup git repo
    - [x] Create sub domain
    - [x] Setup Nginx
    - [x] Create ssh
    - [x] Correct restart_apps for new app
    - [x] Test deployment
- [x] Add email verification code to register also getting the api key
    - [x] Create verify route
        - [x] Create a form
        - [x] If form valid
- [x] Change voxmate.longrunner names to vomate.api
- [x] Setup Spotify call back using api key
##### Spotify Thread - stopping
- [x] Fix time taken to stop
##### Spotify Thread - add tracks
- [x] For add track only:
    - [x] Save current queue
    - [x] Add track
    - [x] Wait 1 second
    - [x] Re-add queue
        - [x] If no queue:
            - [x] Use thread to add 3 tracks of request track artist
            - [x] Get users top played
            - [x] Add them
- [x] Only add new tracks if a track is requested
- [x] Only add x number of tracks
- [x] Add users most played then stop
##### Fixes and improvements
- [x] Fix context uri error
    - [x] Handle if user specifically asks fro content type
- [x] Setup state to track Spotify play
    - [x] Enable pause and restart after user asks question
- [x] Add an ‘action’ service - deals with all the different actionsAdd volume
- [x] Control app volume
- [x] Always set Spotify volume to full
- [x] Set state for current volume to use with up or down
- [x] Set up down and a value
- [x] Add max and mute
- [x] Set default system volume
- [x] Add to settings in control config
- [x] Add default volume to db
- [x] Add default volume to web app
- [x] Test volume control
