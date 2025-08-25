from abc import ABC , abstractmethod 

class Scrapper(ABC):
    @abstractmethod 
    def get_images_urls(): 
        ...