# ~~sCrApEr~~ 
![forthebadge](http://forthebadge.com/images/badges/made-with-python.svg)

***Supported website:***
|                |       |
|----------------|-------|
|fshare          |**[x]**|
|google drive    |**[ ]**|
|twist.moe       |**[x]**|
|freetutsdownload|**[x]**|

### fshare.**vn**
> ***This application for vip accounts only***
1. First, clone this **repo** with `git`:  
```batch
git clone https://github.com/nqh00/scraper.git
```
2. Then `cd` to `scraper`.
3. Run your code with `python`.

**Requirements**
 - **Python 3.5+**
 - [requests](https://github.com/request/request)
 - [aiohttp](https://github.com/aio-libs/aiohttp)
```batch
pip install -r requirements.txt
```
**Example code**
``` python
from fshare import fshare

URL = 'https://www.fshare.vn/folder/ABCDEFG'

# V.I.P accounts only
fs = fshare(email="Your email", password="Your password")

fs.login()

fs.download(URL)
```
**Result**  
```
http://download001.fshare.vn/dl/.../Your%Movie%2021.mp4
```  
### twist.moe
Decrypt password from `JavaScript CryptoJS.AES` by implementing OpenSSL's [EVP BytesToKey](https://www.openssl.org/docs/crypto/EVP_BytesToKey.html).

**Result**
```
Your%Anime%Title
Episode 1: https://cdn.twist.moe/{}.mp4
Episode 2: https://air-cdn.twist.moe/{}.mp4
```  
Visit either `cdn.twist.moe` or `air-cdn.twist.moe` with a `Referer` header request to access:
```json
"Referer": "https://twist.moe/"
```
### freetutsdownload.**net**
Get all `freetus` available courses with `keyword`:
```python
freetuts('keyword')
```
**Result**
```
Course%Name
onedrive: %Ondrive%link
drive: %Google%Drive%link
```