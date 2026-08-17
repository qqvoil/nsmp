import glob
import re

def update_essentials():
    files = glob.glob('/Users/voil/data/nsmp/core/templates/*/plugins/Essentials/config.yml')
    
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Join/Quit Messages
        content = re.sub(r'custom-join-message: "none"', r'custom-join-message: "&#aa00aa&l+ &f{PLAYER}"', content)
        content = re.sub(r'custom-quit-message: "none"', r'custom-quit-message: "&#aa00aa&l- &f{PLAYER}"', content)
        
        # First Join Message
        content = re.sub(r'custom-new-join-message: "none"', r'custom-new-join-message: "&#aa00aa&l+ &fВпервые зашел {PLAYER}"', content)
        
        # Chat format
        content = content.replace("format: '<{DISPLAYNAME}> {MESSAGE}'", "format: '{DISPLAYNAME} &#aa00aa» &f{MESSAGE}'")
        content = content.replace("format: '&7[{GROUP}]&r {DISPLAYNAME}&7:&r {MESSAGE}'", "format: '{DISPLAYNAME} &#aa00aa» &f{MESSAGE}'")

        # Announce format
        content = content.replace("announce-format: '&dWelcome {DISPLAYNAME}&d to the server!'", "announce-format: '&#aa00aa&l+ &fДобро пожаловать, {DISPLAYNAME}!'")
        
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
            
    print("Updated Essentials configs globally.")

update_essentials()
