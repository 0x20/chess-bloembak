# chess-bloembak
Chess implementation for the 32x32 led screen of bloembak

# Installation

- install poetry
- `poetry shell`
- `poetry install`

# Compiling stockfish on the pi

```
sudo apt-get install build-essential
wget https://github.com/official-stockfish/Stockfish/archive/sf_15.zip
unzip sf_15.zip
cd Stockfish-sf_15/src
make build ARCH=armv7
```

# Running

Running on bloembak-compatible hardware

`./chess-bloembak.py`

Running on a mac with a homebrew installed stockfish, showing the ascii board

`./chess-bloembak.py -e /opt/homebrew/bin/stockfish --ascii`
