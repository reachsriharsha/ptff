
import secrets
import string
import re


def gen_random_string(length=3):
    len = secrets.randbelow(4) + length
    safe_chars = (string.ascii_letters + string.digits).replace('l', '') \
        .replace('1', '').replace('I', '').replace('O', '').replace('0', '')
    rand_gen_str = ''.join(secrets.choice(safe_chars) for _ in range(length))
    return rand_gen_str 

def clense_name(name):
    name = name.lower()
    #replace all special characters with _
    #name = ''.join(e for e in name if e.isalnum() or e == '_')
    name = re.sub(r"[^\w\s]", "", name)
    return name