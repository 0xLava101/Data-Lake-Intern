from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.traceback import install
from concurrent.futures import ThreadPoolExecutor, as_completed

import core.scrapper as scrapper 
from core.supabase_service import SupaBaseService
import core.scrap_duckduck_go as duckduck

import json 
import time 
import os 
import sys

install(extra_lines=1)

console = Console()

logo = """ 
[orange_red1]╔╦╗┌─┐┌┬┐┌─┐  ╦  ┌─┐┬┌─┌─┐  ╔═╗┌─┐┬─┐┌─┐┌─┐┌─┐┌─┐┬─┐[/]   
[red3] ║║├─┤ │ ├─┤  ║  ├─┤├┴┐├┤   ╚═╗│  ├┬┘├─┤├─┘├─┘├┤ ├┬┘[/]   
[bright_red]═╩╝┴ ┴ ┴ ┴ ┴  ╩═╝┴ ┴┴ ┴└─┘  ╚═╝└─┘┴└─┴ ┴┴  ┴  └─┘┴└─[/]

Coded By : [b]Omar Moataz[/] & [b]Ahmed Gharib[/]
Just [b]POC[/]
\n\n\n
"""

def read_objects_to_scrape(file):
    with open(file) as f: 
        data = json.load(f)
    return data

def process():
    data = read_objects_to_scrape('./scrapping_objects.json')
    os.system("cls" if os.name == 'nt' else 'clear')
    console.print(logo, justify='center')

    for key, value in data.items():
        console.print(f"\n[[bright_red]CATEGORY[/]] Start Working On '[b]{key}[/]' Category : \n")
        key = key.replace('&', '-')
        
        for keyword in value: 
            console.print(f"\n[[orange_red1]KEYWORD[/]] Working On Keyword '[b]{keyword}[/]' : \n")
            keyword = keyword.replace('/', '-')

            scrapping_operataion(key, keyword, 10)
            time.sleep(3)


def scrapping_operataion(category, keyword, limit):
    images = duckduck.duckduck_search(keyword, limit)
    supbase = SupaBaseService()
    
    success_uploaded = 0

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.0f}% ",
        TimeRemainingColumn(),
        console=console,
    ) as progress:

        task = progress.add_task(f"[cyan]Uploading {keyword} images...", total=len(images))

        def process_image(image_url):
            image_buffer = scrapper.download_image_in_memory(image_url)
            if image_buffer:
                result = supbase.upload_image(image_buffer, f'{category}/{keyword}')
                return result is True
            return False

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(process_image, url) for url in images]

            for future in as_completed(futures):
                try:
                    if future.result():
                        success_uploaded += 1
                except Exception as e:
                    print(f"❌ Thread error: {e}")
                progress.advance(task)

    console.print(f"[green]✅ Uploaded {success_uploaded} image(s) for keyword: [b]{keyword}[/][/]")


# Entry point

if __name__ == '__main__' :
    mode = sys.argv[1]

    if mode == 'scrap':
        try:
            process()
        except KeyboardInterrupt:
            console.print("\n[b red]Program Exiting ..[/]\n")
            exit(0)
    
    elif mode == 'label': 
        from core.label_studio import upload_to_label_studio
        upload_to_label_studio()
    
    else : 
        console.print("[[red]-[/]] Invaild Option")
        exit(1)