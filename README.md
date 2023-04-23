# listeners-digest
Turn Wikipedia content to audio files via Amazon Polly

## About
This program will get the summary text (the first main section) from Wikipedia, send it to Amazon Polly for voice synthesis and return an mp3.
It cleans up the text by removing content that does't work well without a visual reference (e.g. bracket which are akin to asides and mathmatical equations) as well as adding pauses.

## How to
For this solution work work you need to have an AWS account (free tier is fine).  You need to install boto3 (see https://pypi.org/project/boto3/)
```python -m pip install boto3```

after boto3 is installed, run ```aws configure``` in the command line to provide an access key and passphrase generated from your AWS IAM settings to be able to connec to AWS Polly and request text synthesis.

The wikipedia API is public and does not require authentication to get page content

The program will attempt to save an .mp3 audio file at the same location as the script and auto-play it on your operating system (Windows, Lunix or Mac)

## Changes to source text for narration
This program makes the following modifications to text for easier listening:
- Identifies 4 digit numbers as dates if they are preceed by any of the following: of, in, before, after, until, since. Otherwise program assumes these are numbers and narrates accordingly.
- Removes bracketed asides, as well as nexted brackets to a depth of 2. This means some clarification may be lost but eases listening.
- Any content that has HTML tag 'displaystyle' as this usually indicates a non-text item such as a math foruma, or expression.

If any lines of source were skipped this will be referenced at the end of the narration. 


