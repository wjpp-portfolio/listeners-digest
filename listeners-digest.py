import requests
import boto3
import sys
import subprocess
import re
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing

POLLY_SSML_PROTECTED_SYMBOLS = {'&':'&amp;',
                                '\"':'&quot;',
                                '\'':'&apos;',
                                '<':'&lt;',
                                '>':'&gt;'
                                }



class URLToAudio:
    '''This class takes a Wikipedia article URL and returns an audio file of the summary section from that URL'''
    def __init__(self,passed_URL):
        self.polly_text_format = 'ssml' #'ssml' or 'text'
        self.voice_engine = 'neural' #'standard' or 'neural'
        self.narration_voice = 'Brian'
        self.output_file_type = 'mp3'

        if 'en.wikipedia.org' in passed_URL:     
            self.page_title = passed_URL.split('/')[-1]      

        elif passed_URL == '':
            pass
            
        else:
            self.page_title = 'test audio file'
            self.extracted_text = passed_URL

    def get_wikipedia_content(self):
        '''uses Wikipedia API to retreive page summary section'''
        API_url = 'https://en.wikipedia.org/w/api.php'
        params = {
                'format': 'json',
                'action': 'query',
                'prop': 'extracts',
                'exlimit': '1',
                'exsectionformat': 'plain', #plain | wiki | raw
                'explaintext': 'true',
                'exintro': 'true',
                'titles': self.page_title
            }

        url_response = requests.get(url = API_url, params = params)
        #Add in page exists validation
        
        if url_response.status_code == 200:
            body_data = url_response.json()
            page_code = list(body_data['query']['pages'])[0] #page_code used 
            extracted_text = body_data['query']['pages'][page_code]['extract']
           
            if len(extracted_text) == 0 or extracted_text == '':
                print('No text returned')
                return False

            return extracted_text
        else:
            print('Error returning content')
            return False

    def mark_up_text_for_synthesis(self):
        ''''''
        skipped_count = 0
        list_of_paragraphs = []

        self.extracted_text = re.sub(r'([\[|\]])', '', self.extracted_text) #removes square brackets 
        self.extracted_text = re.sub(r'(\((?:[^\(]*?\)))', '', self.extracted_text) #removes brackets 
        self.extracted_text = re.sub(r'(\((?:[^\(]*?\)))', '', self.extracted_text) #and nested brackets 
        
        self.extracted_text = re.sub(r'(?<=[a-z]|[0-9])\.(?=[A-Z])', '.\n', self.extracted_text) #adds a new paragraph after full stops immediately followed by a non-digit character. This can happen where a wikipedia reference in the source hides a paragraph marker
        
        for paragraph in self.extracted_text.split('\n'):
            if len(paragraph) == 0:
                continue

            if '{\displaystyle' in paragraph:
                skipped_count += 1
                continue
            
            paragraph = paragraph.strip()

            for symbol in POLLY_SSML_PROTECTED_SYMBOLS:
                if symbol in paragraph:
                    paragraph = paragraph.replace(symbol, POLLY_SSML_PROTECTED_SYMBOLS.get(symbol))

            paragraph = re.sub(r'(?<=[in|the|of|before|after|until|since|from|and|-]\s)[1|2]\d{3}(?=[\s|\.|-|,|;|!])', regex_dates, paragraph) 
            paragraph = '<speak><p>' + paragraph + '</p></speak>'
            list_of_paragraphs.append(paragraph)
            
        if skipped_count > 0:
            list_of_paragraphs.append('<speak>' + str(skipped_count) + ' non-narratable sentences were removed for easier listening.</speak>')
            
        list_of_paragraphs.append('<speak>End of narration.</speak>')
        
        return list_of_paragraphs

    def request_speech_synthesis(self):
        ''''''
        content_to_submit = self.mark_up_text_for_synthesis()
        
        aws_session = boto3.Session(profile_name='default')
        aws_polly_client = aws_session.client('polly')

        concatinated_audio_stream = bytearray()
        try:
            for request in content_to_submit:
                response = aws_polly_client.synthesize_speech(Engine = self.voice_engine,
                                                 Text = request,
                                                 OutputFormat = self.output_file_type,
                                                 VoiceId = self.narration_voice,
                                                 TextType = self.polly_text_format
                                                 )

                if 'AudioStream' in response:
                    with closing(response['AudioStream']) as stream:
                        concatinated_audio_stream.extend(stream.read())
                else:
                    print('Could not stream audio')

        except (BotoCoreError, ClientError) as error:
            # The service returned an error, exit gracefully
            raise error

        self.__write_steam_to_file(concatinated_audio_stream)
        
    def __write_steam_to_file(self,stream):
        ''''''
        try:
        # Open a file for writing the output as a binary stream
            with open(self.page_title + '.' + self.output_file_type, 'wb') as file:
                file.write(stream)
        except IOError as error:
            # Could not write to file, exit gracefully
            print(error)
            sys.exit(-1)
            
    def play_audio(self):
        ''''''
        if sys.platform == 'win32':
            os.startfile(self.page_title + '.' + self.output_file_type)
        else:
            # The following works on macOS and Linux. (Darwin = mac, xdg-open = linux).
            opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
            subprocess.call([opener, self.page_title + '.' + self.output_file_type])


def regex_dates(match):
    return '<say-as interpret-as="date" format="y">' + match[0] + '</say-as>'
                    
if __name__ == '__main__':
    url = 'https://en.wikipedia.org/wiki/Attack_on_Pearl_Harbor'

    converter = URLToAudio(url)
    converter.extracted_text = converter.get_wikipedia_content()
    converter.request_speech_synthesis()
    a = converter.mark_up_text_for_synthesis()
    for i in a:
        print(i)
    converter.play_audio()
 
