# Contract Summarizer
A neat way of getting highlights of pdf documents.



![](https://github.com/SimplyVlad/contract-summarizer/blob/main/visuals/demo.gif)


### Setup
Make sure you add an OpenAI key either in ```streamlit/Dockerfile``` as
```
ENV OI_KEY <your key>
```
or in the default value of the ```OI_KEY``` environment variable in ```streamlit/contract_summarizer.py```

### A very quick demo

With [Docker](https://www.docker.com) installed, run

```lang=bash
docker-compose up
```
Default login credentials: <br>
usr: jsmith <br>
pwd: jsmith <br>

It has been tested with emplyoment contracts in both English and German, but it could work with others as well.

### Configuration
Add more usernames in streamlit/config.yaml and generate the respective hashes using the hasher script - ```utils/hasher.py```

### TODOs:
1. Add more languages
2. Create a version without default keys
3. Add language model selection
