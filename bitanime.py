import requests as req
import ctypes
import os
import time
from anikimiapi import AniKimi
from termcolor import colored
import concurrent.futures
from backend import Download, CustomMessage, get_download_links
from tqdm.contrib.concurrent import thread_map
import linecache
from bs4 import BeautifulSoup
import mpv
from colorama import Fore
import sys
import subprocess

OK = f"{Fore.RESET}[{Fore.GREEN}+{Fore.RESET}] "
ERR = f"{Fore.RESET}[{Fore.RED}-{Fore.RESET}] "
IN = f"{Fore.RESET}[{Fore.LIGHTBLUE_EX}>{Fore.RESET}] "
try:
    ctypes.windll.kernel32.SetConsoleTitleW("BitAnime")
except AttributeError:
    pass

with open('D:\pythonprojects\Anime\menugraphic.txt') as f:
    contents = f.read()

anime = AniKimi(
    gogoanime_token="h65ljs00pl024m41so9gpn89h1",
    auth_token = "eKzu2ajtnSfa2McSQDv4vWXCqaGI46nC%2BFn0iT1ypZ389IAEz4MFAvDU0WW1%2BS1PJJBgFYyjKMHcWj5dUiANyw%3D%3D",
    host = "https://gogoanime.pe/"
)

def bitanime():
    os.system("cls")
    while True:
        print(colored(contents, 'green'))
        print(colored("Welcome!", 'green'))
        while True:
            name = input(f"{IN}Type S for search, H for History, D for Details, P to play downloaded episodes, to download type the anime name. > ")
            if name == 'h':
                readhistory()
            if name == 'p':
                player()
            if name == "s":
                search()
            elif name == "d":
                getdetails()
            else:
                bettertitle = name.replace(" ", "-")
                name = bettertitle.lower()
                title = name.title().strip()
            source = f"https://gogoanime.pe/category/{name}"
            with req.get(source) as res:
                if res.status_code == 200:
                    soup = BeautifulSoup(res.content, "html.parser")
                    all_episodes = soup.find("ul", {"id": "episode_page"})
                    all_episodes = int(all_episodes.get_text().split("-")[-1].strip())
                    break
                else:
                    print(f"{ERR}Error 404: Anime not found. Please try again.")
        while True:
            quality = input(
                f"{IN}Enter episode quality (1.SD/360P|2.SD/480P|3.HD/720P|4.FULLHD/1080P) > "
            )
            if quality == "1" or quality == "":
                episode_quality = "SDP"
                break
            elif quality == "2":
                episode_quality = "SHD"
                break
            elif quality == "3":
                episode_quality = "HDP"
                break
            elif quality == "4":
                episode_quality = "FullHDP"
                break
            else:
                print(f"{ERR}Invalid input. Please try again.")
        print(f"{OK}Title: {Fore.LIGHTCYAN_EX}{title}")
        print(f"{OK}Episode/s: {Fore.LIGHTCYAN_EX}{all_episodes}")
        print(f"{OK}Quality: {Fore.LIGHTCYAN_EX}{episode_quality}")
        print(f"{OK}Link: {Fore.LIGHTCYAN_EX}{source}")
        
        folder = os.path.join(os.getcwd(), title)
        if not os.path.exists(folder):
            os.mkdir(folder)

        if all_episodes != 1:
            while True:
                choice = input(
                    f"{IN}Do you want to download all episode? (y/n) > "
                ).lower()
                if choice in ["y", "n"]:
                    break
                else:
                    print(f"{ERR}Invalid input. Please try again.")

        episode_start = None
        episode_end = None

        if choice == "n":
            while True:
                try:
                    episode_start = int(input(f"{IN}Episode start > "))
                    episode_end = int(input(f"{IN}Episode end > "))
                    if episode_start <= 0 or episode_end <= 0:
                        CustomMessage(
                            f"{ERR}episode_start or episode_end cannot be less than or equal to 0"
                        ).print_error()
                    elif episode_start >= all_episodes or episode_end > all_episodes:
                        CustomMessage(
                            f"{ERR}episode_start or episode_end cannot be more than {all_episodes}"
                        ).print_error()
                    elif episode_end <= episode_start:
                        CustomMessage(
                            f"{ERR}episode_end cannot be less than or equal to episode_start"
                        ).print_error()
                    else:
                        break
                except ValueError:
                    print(f"{ERR}Invalid input. Please try again.")

        if episode_start is not None:
            pass
        else:
            episode_start = 1
        if episode_end is not None:
            pass
        else:
            episode_end = all_episodes

# create history file or something, idk its scuffed
        if os.path.exists(f'{folder}/history.txt'):
            os.remove(f'{folder}/history.txt')

        with open('history.txt', 'x') as f:
            f.write(f'''
This is the history file for the history function. it is recommended to not edit it.
{name}
{episode_start}
{episode_end}
{folder}''')

        download = Download(
            name, episode_quality, folder, all_episodes, episode_start, episode_end
        )

        source = f"https://gogoanime.pe/{name}"
        with req.get(source) as res:
            soup = BeautifulSoup(res.content, "html.parser")
            episode_zero = soup.find("h1", {"class": "entry-title"})  # value: 404

        if choice == "n" or episode_zero is not None:
            source = None

        episode_links = download.get_links(source)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            download_links = list(executor.map(get_download_links, episode_links))
            download_urls = list(executor.map(download.get_download_urls, download_links))
            print(
            f"{OK}Downloading {Fore.LIGHTCYAN_EX}{len(download_urls)}{Fore.RESET} episode/s"
        )
        thread_map(
            download.download_episodes,
            download_urls,
            total=len(download_urls),
        )

        try:
            os.startfile(folder)
        except AttributeError:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, folder])
        print("\n")
        use_again = input(f"{IN}Do you want to use the app again? (y|n) > ").lower()
        if use_again == "y":
            os.system("cls")
        else:
            break

def search():
    print(colored('What anime would you like to see?', 'blue'))
    choice = input()
    results = anime.search_anime(query=choice)
    for i in results:
        print(i.title)
    time.sleep(5)
    bitanime()

def getdetails():
    print(colored("What anime would you like details from?", 'blue'))
    animede = input(f'{IN}Anime name > ')
    animedetitle = animede.replace(" ", "-").lower()
    details = anime.get_details(animeid=f'{animedetitle}')
    print('\n')
    print(colored(f'Title: {details.title}', 'blue'))
    print(colored(f'Year: {details.year}', 'blue'))
    print(colored(f'Seasons: {details.season}', 'blue'))
    print(colored(f'Episodes: {details.episodes}', 'blue'))
    print(colored(f'Summary: {details.summary}', 'blue'))
    time.sleep(10)
    bitanime()

def readhistory(): # why is there an unmatched () like its there so that is why there are a thousand variables
    # also there are global for player() function
    global animelocate
    global lastepint
    global firstepint
    animevar = linecache.getline('history.txt', 3).strip()
    print(colored(f'Anime Downloaded: {animevar}', 'green'))
    firstepisode = linecache.getline('history.txt', 4)
    firstepint = int(firstepisode)
    lastepisode = linecache.getline('history.txt', 5)
    lastepint = int(lastepisode)
    totalepisodes = lastepint - firstepint + 1
    print(colored(f'Episodes downloaded: {totalepisodes}', 'green'))
    animelocate = linecache.getline('history.txt', 6).strip()
    print(colored(f'Anime Location: {animelocate}', 'green'))


def player():
    print(colored(f'{OK} Getting history.txt for player...', 'green'))
    readhistory()
    # create python-MPV video player
    videoplayer = mpv.MPV(input_default_bindings=True)
    videoplayer.fullscreen = True
    currentep = firstepint
    epintint = 99999
    # GUI for player
    while True:
        os.system("cls")
        print(colored(f'{OK} Playing episode {currentep}.\n', 'blue'))
        videoplayer.play(f'{animelocate.strip()}/EP.{currentep}.MP4')
        print(colored(f'{OK} [N] Next Episode', 'green'))
        print(colored(f'{OK} [P] Previous Episode', 'green'))
        print(colored(f'{OK} [E] Exit Player', 'green')) 
        playerchoice = input(f'{IN} Choose an option >> ').lower()
        if playerchoice == 'n':
            currentep = currentep + 1
            print(currentep)
            if currentep < firstepint or currentep > lastepint:
                print(f'{ERR} Wrong episode entered, playing episode {firstepint}')
                currentep = firstepint
                time.sleep(2)
        if playerchoice == 'p':
            currentep = currentep - 1
            if currentep < firstepint or currentep > lastepint:
                print(f'{ERR} Wrong episode entered, playing episode {firstepint}')
                currentep = firstepint                                                                                  # i made a mess here
                time.sleep(2)
        if playerchoice == 'e':
            videoplayer.terminate()
            bitanime()
        else:
            print(f'{ERR} incorrect option.')

    






    

if __name__ == "__main__":
    bitanime()