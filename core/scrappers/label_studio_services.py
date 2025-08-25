from label_studio_sdk import Client

import os 
from threading import Lock


label_configs = '''
<View>
<Header value="Detect '$folder'" />
<Image name="image" value="$image" rotateControl="true"/>
<RectangleLabels name="label" toName="image">
    <Label value="$folder"/>
</RectangleLabels>
</View>
'''

class LabelStudio:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None: 
                    cls._instance = super(LabelStudio, cls).__new__(cls)
                    cls._instance._init_client()
        return cls._instance
    
    def _init_client(self):
        self.url = os.getenv('LABEL_STUDIO_URL')
        self.api_key = os.getenv('LABEL_STUDIO_KEY')
        self.ls = Client(url=self.url, api_key=self.api_key)
        
    def create_category(self , name : str ) -> int :
        projects = self.ls.get_projects()
        project  = next((p for p in projects if p.title == name), None)
        
        if project:
            return project.id 
        
        project = self.ls.start_project(
            title=f"Object Detection | {name}",
            label_config=label_configs,
            description=f"Detect '{name}' in images using bounding boxes."
        )

        return project.id 
    
    def upload_image():
        ...