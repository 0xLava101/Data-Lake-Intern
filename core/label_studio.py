# core/label_studio.py

from label_studio_sdk import Client
import os 
import time 

from core.supabase_sdk_client import SupabaseClient

def upload_to_label_studio():
    label_config_template = '''
<View>
<Header value="Detect '$folder'" />
<Image name="image" value="$image" rotateControl="true"/>
<RectangleLabels name="label" toName="image">
    <Label value="$folder"/>
</RectangleLabels>
</View>
'''

    ls = Client(
        url='https://app.humansignal.com/', 
        api_key=os.getenv('LABEL_STUDIO_KEY')
    )

    supabase = SupabaseClient()
    structed_tree = supabase.get_images_urls_structured()

    BATCH_SIZE = 10
    DELAY_SECONDS = 2

    for category, folders in structed_tree.items():
        project = ls.start_project(
            title=f"Object Detection | {category}",
            label_config=label_config_template,
            description='Detect objects in images using bounding boxes.'
        )
        print(f'✅ Created Project ID: {project.id} | Category: {category}')

        for folder_name, image_urls in folders.items():
            for i in range(0, len(image_urls), BATCH_SIZE):
                batch_urls = image_urls[i:i + BATCH_SIZE]
                tasks = [
                    {
                        "data": {
                            "image": url,
                            "folder": folder_name
                        }
                    } for url in batch_urls
                ]

                try:
                    project.import_tasks(tasks)
                    print(f"✅ Uploaded batch of {len(tasks)} tasks from folder: {folder_name}")
                except Exception as e:
                    print(f"❌ Error uploading batch: {e}")
                
                time.sleep(DELAY_SECONDS) 