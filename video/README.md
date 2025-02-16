# Video Segmentation by Steps
1. Downloads video
2. Parses subtitle file, removes artifacts from auto-generated subtitles into json
3. Takes generated instruction.json and combines with subtitles to be parsed by Perplexity LLM for timestamps of different video steps
4. Parses Perplexity LLM's json output
5. Segments video into parts and saves to video\_steps/

## In order:
```
python3 ytdown.py
python3 parsevtt.py
python3 subtitlesparse.py
python3 extractJSONsplits.py
python3 videoseg.py
```
