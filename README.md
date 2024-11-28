# Vibester

## Environment
Install Anaconda from [their website](https://www.anaconda.com/download). You should end up with a program called Anaconda prompt on your computer.  
In Anaconda prompt, create a new environment for the project:
```
conda create -n vibester python=3.12
```
Install the necessary packages into the environment:
```
pip install -r requirements.txt
```

## Chromaprint
Using the generate feature only works if you have pyacoustid working. Chromaprint is one of the core libraries of pyacoustid that can create small fingerprints of music. Pyacoustid uses this feature to do song metadata lookup.

### Installation
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
The API requires a key to query correctly. This key is found in our .env file
