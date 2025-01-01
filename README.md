# Vibester

## Setup

### Environment
Install Anaconda from [their website](https://www.anaconda.com/download). You should end up with a program called Anaconda prompt on your computer.  
In Anaconda prompt, create a new environment for the project:
```
conda create -n vibester python=3.12
```
Install the necessary packages into the environment:
```
pip install -r requirements.txt
```

### Chromaprint
Using the generate feature only works if you have pyacoustid working. Chromaprint is one of the core libraries of pyacoustid that can create small fingerprints of music. Pyacoustid uses this feature to do song metadata lookup.

#### Installation
You can install chromaprint through  [their website](https://acoustid.org/chromaprint) or using Chocolatey:
```
choco install chromaprint
```
After the installation you should be able to run fpcalc from the command line. Make sure to restart the terminal client beforehand. Verify this by issuing the following command:
```
fpcalc -version
```
The API requires a key to query correctly. This key is found in our `.env` file or you can request a new key using the Acoustid website.

### APIs

The app uses services that are able to recognize a song and download its metadata. Due to the error rate in some API providers multiple endpoints are being queried each time a song has to be recognized:  

- Acoustid: [https://acoustid.org/](https://acoustid.org/)  
- Deezer: no registration or API key required  
- Spotify: Create a new app on the [Spotify developer dashboard](https://developer.spotify.com/dashboard) and save 
the Client ID and Client Secret into the .env file.  

The correct key names can be found under the `.env.template` file. Insert them there as strings.

### OpenSSL

Secure tunneling is used as browsers only enable webcamera usage though HTTPS. You will have to generate a secure certificate for the Dash application to provide client browsers with. 

1. Install OpenSSL
2. Generate a key.pem and cert.pem using the command

```
openssl req -x509 -new -key key.pem -out cert.pem -days 365
```
Place the `key.pem` and `cert.pem` files in the `data/cert` directory. 

## Generation of cards

You can use this app to generate the QR codes with the year, similar to the game Hitster, using this app.

1. The first resort for finding the artist, title, and year of a song is the IDV3 tags of a song. If it is tagged, it will be taken as ground truth. You can use tools like AudioRanger to tag music files.

2. If the music is not tagged, the music will be fingerprinted using Chromaprint, and the corresponding metadata will be queried from the following APIs:
   - MusicBrainz
   - Spotify
   - Deezer  
   Keep in mind these APIs might not return the correct release year of the song but rather when the song's album was first released. Empirical data shows this can mean a difference of +10 years in some cases. It is necessary to check all the years if you are not sure or are using the app with lesser-known songs. You can edit the table in the generate page manually.

3. In case there is no match found for the musical fingerprint in any of the APIs, the song's artist and title will be inferred from the filename, provided the filename format is `artist - title.mp3` or similar. The delimiter is the `-` character surrounded by spaces.


## Usage

1. Insert your music into the folder `data/music`. The list of supported file formats can be found in VibesterConfig. 
2. Start the application using the dash application.
3. Go to the generate page. This should be the second from the top button.
4. Wait for the table to load. It will take some time to load as the music that is not yet in the database has to be fingerprinted and analyzed to extract the metadata from it. 
5. When the table is loaded click the generate button to create a new PDF file from the music. 
6. The file should now be under the `data/output` folder. 
7. Stick two pages together back-by back so the QR codes match and cut out the QR codes with scissors.
8. Enjoy the game by clicking the play button in the main menu.

## Original rules

Please refer to [The original game maker's site](https://hitstergame.com/en-us/) for the rules of the game and how to play.