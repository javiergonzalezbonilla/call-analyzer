# call-analyzer
The project consists of a small web application that allows users to upload a short audio recording file of a sales phone call (WAV or MP3) and then transcribe the audio using a STT (speech-to-text) model and analyze it with an LLM.

# Install

 
## Setup environment


```sh   
make create-environment

conda activate call-analyzer   

make install-dependencies

```

install yarn 
```sh


brew install yarn

cd call-analyzer-web

yarn

```


### Install docker and docker-compose in your machine 

```sh
brew install docker
brew install docker-compose
```



### Run

```sh
make docker-compose-up
```

