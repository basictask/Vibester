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
After this make sure you have pyacoustid installed in your environment:
```
pip install pyacoustid
```
After the installation you should be able to run fpcalc from the command line. Make sure to restart the terminal client beforehand. Verify this by issuing the following command:
```
fpcalc -version
```
The API requires a key to query correctly. This key is found in our .env file or you can request a new key using the Acoustid website. If you have a new key insert it into the .env file under the name API_KEY_ACOUSTID


## Usage

1. Insert your music into the folder `data/music`. The list of supported file formats can be found in VibesterConfig. 
2. Start the application using the dash application.
3. Go to the generate page. This should be the second from the top button.
4. Wait for the table to load. It will take some time to load as the music that is not yet in the database has to be fingerprinted and analyzed to extract the metadata from it. 
5. When the table is loaded click the generate button to create a new PDF file from the music. 
6. The file should now be under the `data/output` folder. 
7. Stick two pages together back-by back so the QR codes match and cut out the QR codes with scissors.
8. Enjoy the game by clicking the play button in the main menu.