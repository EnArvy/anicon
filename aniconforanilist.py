from warnings import filterwarnings
from PIL import Image, ImageOps
import requests
from requests import get
import re
import os
import json

print('''Run this in your anime folder
For help and info, check out
https://github.com/EnArvy/anicon
''')


filterwarnings("ignore")
folderlist = next(os.walk('.'))[1]
folderpath = os.path.dirname(os.path.realpath(__file__))
if folderlist is None or len(folderlist) == 0:
    # In case the file is placed inside an inner most directory which contains only files and no other folders, this list will be empty.
    # Thus adding the current directory path as an element of the list.
    folderlist = [str(os.getcwd())]
automode = True if input('Use AutoMode? Y/N : ').upper() == 'Y' else False

def getname(name: str) -> str:

    lastwords = ['bd', 's0', '480p', '720p', '1080p']
    wordstoremove = ['bluray', 'x265', 'x264', 'hevc', 'hi10p', 'avc', '10bit', 'dual', 'audio', 'eng', 'english', 'subbed', ' sub ', 'dubbed', 'dub']

    name = name.lower().replace('_', ' ').replace('.', ' ')
    
    for word in wordstoremove:
        name = name.replace(word, '')
    
    name = re.sub(r"(?<=\[)(.*?)(?=\])", '', name)
    name = re.sub(r"(?<=\()(.*?)(?=\))", '', name)
    name = name.replace('()', '').replace('[]', '')

    for word in lastwords:
        rexstr = "(?<=" + word + ")(?s)(.*$)"
        name = re.sub(rexstr, '', name).replace(word, '')

    return(name.strip())

def getartwork(name: str) -> tuple:

    url="https://graphql.anilist.co"

    query = '''
            query($name:String)      {
                Page{
                    media(search:$name,format_not_in:[MANGA,ONE_SHOT,NOVEL,MUSIC]) {
                        id
                        type
                        title {
                            romaji
                            english
                        }
                        coverImage {
                            extraLarge
                        }
                    }
                }
            }
        '''
    variables = {
        'name':name
    }
    print(name)
    results = requests.post(url,json={'query':query,'variables':variables})
    jsonobj = json.loads(results.content)
    if automode:
        return(jsonobj['data']['Page']['media'][0]['coverImage']['extraLarge'],jsonobj['data']['Page']['media'][0]['type'])
    else:  
        counter = 1  
        for id in jsonobj['data']['Page']['media']:
            print(str(counter)+' - '+id['title']['romaji'])
            counter = counter + 1
        ch = input('\n>')
        if ch == '':
            ch = 1
        return(jsonobj['data']['Page']['media'][int(ch)-1]['coverImage']['extraLarge'] , jsonobj['data']['Page']['media'][int(ch)-1]['type'])
 

def createicon(folder: str, link: str):

    art = get(link)
    open(jpgfile, 'wb').write(art.content)

    img = Image.open(jpgfile)
    img = ImageOps.expand(img, (69, 0, 69, 0), fill=0)
    img = ImageOps.fit(img, (500,500)).convert("RGBA")
    
    datas = img.getdata()
    newData = []
    for item in datas:
        if item[0] == 0 and item[1] == 0 and item[2] == 0:
            newData.append((0, 0, 0, 0))
        else:
            newData.append(item)

    img.putdata(newData)
    os.remove(jpgfile)
    img.save(icofile)
    img.close()
    return(icofile)
    

for folder in folderlist:
    name = getname(folder)

    # Extracting the name of the folder without the path and then performing search for the same. This will be the name of the anime
    # episode, thus instead of performing a search for the directory path, now performing a search for the directory name.
    name = name.rpartition('\\')[2].strip()

    iconname = name.replace(' ', '_')
    jpgfile = folder + '\\' + iconname + '.jpg'
    icofile = folder + '\\' + iconname + '.ico'
    
    if os.path.isfile(icofile):
        print('An icon is already present. Delete the older icon and `desktop.ini` file before applying a new icon')
        continue
    try:
        link, Type = getartwork(name)
        icon = createicon(folder, link)
    except:
        print('Ran into an error. Blame the dev :(')
        continue

    f = open(folder + "\\desktop.ini","w+")
    
    icopath = folderpath + '\\' + icofile
    f.write("[.ShellClassInfo]\nConfirmFileOp=0\n")
    f.write("IconResource={},0".format(icopath.strip("\\")))
    f.write("\nIconFile={}\nIconIndex=0".format(icofile.replace(folder, "").strip("\\")))
    f.write("\n[ViewState]\nMode=\nVid=\nFolderType=Videos")
    
    if Type is not None and len(Type) > 0:
        # If the result has a type, then using this as the infotip for the desktop icon.
        f.write("\nInfoTip={}".format(Type))

    # Closing the output stream. All the text will be written into `desktop.ini` file only when the output is being closed.
    f.close()

    # Not marking the `desktop.ini` file as a system file. This will make sure that the file can be seen if display hidden items is enabled.
    os.system('attrib +r +s \"{}\\{}\"'.format(os.getcwd(), folder))
    os.system('attrib +h \"{}\\desktop.ini\"'.format(folder))
    os.system('attrib +h \"{}\"'.format(icon))

