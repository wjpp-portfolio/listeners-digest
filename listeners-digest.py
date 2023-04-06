import requests
class URLToAudio:
    """This class takes a Wikipedia article URL and returns an audio file of the summary section from that URL"""
    def __init__(self,passedURL):
        self.page_title = passedURL.split('/')[-1]        
        self.get_wikipedia_content()
        
    def __parse_request_string(self):
        """processes passed string and ensures format is suitable to submit to Wikipedia API"""
        pass
    
    def get_wikipedia_content(self):
        """"""
        API_url = "https://en.wikipedia.org/w/api.php"
        params = {
                "format": "json",
                "action": "query",
                "prop": "extracts",
                "exlimit": "1",
                'exsectionformat': 'plain',
                'explaintext': 'true',
                'exintro': 'true',
                'titles': self.page_title
            }

        url_response = requests.get(url = API_url, params = params)

        if url_response.status_code == 200:
            body_data = url_response.json()

            page_code = list(body_data["query"]["pages"])[0] #page_code used 

            extracted_text = body_data["query"]["pages"][page_code]["extract"]
            self.wikipedia_content = extracted_text
    

    def __isolate_summary_content(self):
        """"""
        pass

    def request_speech_synthesis(self):
        """"""
        __markup_text_for_synthesis()
        

    def __markup_text_for_synthesis(self):
        """"""
        pass

    def play_audio(self):
        """"""
        pass

if __name__ == '__main__':
    url = "https://en.wikipedia.org/wiki/Fukushima_nuclear_disaster"

    converter = URLToAudio(url)
    print(converter.wikipedia_content)
