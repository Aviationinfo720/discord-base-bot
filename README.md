# Discord Base code

**READ BEFORE USING**

*--------------------------------------------------------------UPDATE 2.0.1----------------------------------------------------------------------------*

Thankyou for using my bot base code, Under here is all of the pips you have to do:

**discord:**
`pip install discord.py`

**discord.ext (shoudnt have to because it usually comes in with discord but incase):**
`pip install discord-ext`

**typing (brings the Optional module to set wether a input is optional or not):**
`pip install typing`

**asyncio (makes the code smoother):**
`pip install asyncio`

**spotifysearch (finds the song):**
`pip install spotifysearch`

**spotipy (finds the artist):**
`pip install spotipy`

**characterai:**
`pip install characterai`

**PyCharacterAI:**
`pip install git+https://github.com/Xtr4F/PyCharacterAI` <- adding git+[github_respitory_url] allows you to clone the respitory to your computer

*--------------------------------------------------------------UPDATE 2.0.2----------------------------------------------------------------------------*

This was a **big** update and thus alot of libraries were imported, The most importand one and the hardest one being ffmpeg. Heres a whole guidethrough on how to download ffmpeg.

ffmpeg is actually a external library which is not fully uploded in pyPI, so doing `pip install ffmpeg` would work but it just interacts with the ffmpg which you download onto your computer manually.

To make it easier, imagine drinking Coca Cola with a straw. The straw is `pip install ffmpeg`, you are python and the coca cola is the ffmpeg download. If you dont get the coca cola, you woudnt get any soda from the straw. The same acts here. Lets do a rundown to getting ffpmeg installed and fully initialied onto your computer:

**NOTE1: THIS GUIDE ISNT PERFECT, YOU MIGHT BREAK YOUR COMPUTER. I RECOMEND FOR SEARCHING A GUIDE HOW TO DOWNLOAD FFMPEG AND PUT IT TO PATH ON YOUTUBE**
**NOTE2: THIS GUIDE IS ONLY FOCUSED ON WINDOWS COMPUTERS, I RECOMEND FOLLOWING A YOUTUBE VIDEO FOR OTHER PLATFORMS**

**Step 1:** Go to the main ffmpeg website (https://ffmpeg.org)

**Step 2:** Press download -> Get packages & executable files and select the windows icon.

**Step 3:** I recomend downloading from gyan.dev, so select "Windows builds from guyan.dev"

**Step 4:** Scroll down and select "ffmpeg-git-full.7z"

**Step 5:** A file will download, Store it somewhere safe. I recomend "C:/" drive

**Step 6:** Extract the zip file

**Step 7:** Go into the file, and search for the flie named "bin" and copy the file path.

**Step 8:** in your taskbar, search "Edit the system enviorment variables" and press enter

**Step 9:** Press "Advanced" on the top and click "Enviorment Variables" at the bottom

**Step 10:** You will see all of your system enviroment variables.

**Step 11:** On the top list, click "Path" and click "Edit"

**Step 12**: Press "New", and paste the file path.

**Step 13**: Press "Ok" and close everything.

**Step 14 (Optional):** If your code editor dosent constantly updates its resources, close your editor and re-open it. (You have to do it if youre using vs code) 

*aaaaand* its done! You have finally downloaded your ffmpeg and added it to your path. To check wether you have ffmpeg properly installed, open cmd or your powershell and type `ffmpeg -version`. You should see alot of information, but if you get a error, you may have done something wrong. But dont worry, do the guide once again or search on youtube for a better guide.

And yeah I forgot, now you can do `pip install ffmpeg` and it should work!
Aso import `pip install yt_dlp`too