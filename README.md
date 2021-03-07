# ~~sCrApEr~~ 
![forthebadge](http://forthebadge.com/images/badges/made-with-python.svg)

***Supported website:***
| |                |       | |
|-|----------------|-------|-|
| |fshare          | **x** | |
| |google drive    |       | |
| |vikv            | **x** | |
| |twist.moe       | **x** | |
| |freetutsdownload| **x** | |
| |                |       | |

**Getting started**
1. First, clone this **repo** with `git`:  
```batch
git clone https://github.com/nqh00/scraper.git
```
2. Then `cd` to `scraper`.
3. Install all required dependencies with `pip`:
```batch
pip install -r requirements.txt
```
**Requirements**
 - [**CygWin**](https://cygwin.com/setup-x86_64.exe) or [Git Bash](https://github.com/git-for-windows/git/releases/latest)
 - [**Python**](https://www.python.org/ftp/python/3.9.0/python-3.9.0-amd64.exe)
 - [aria2c](https://github.com/aria2/aria2/releases/latest)
 - [ffmpeg](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z)
 - [requests](https://github.com/request/request)
 - [aiohttp](https://github.com/aio-libs/aiohttp)
### fshare.**vn**
> *This application for vip accounts only*
> 
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
### vikv.**net**
Encode `hdv-user` using `btoa` & `reverse` then send request to `vikv` backend.
Download all `.ts` file & merge them back with `ffmpeg`.
### twist.moe
Decrypt password from `JavaScript CryptoJS.AES` by implementing OpenSSL's [EVP BytesToKey](https://www.openssl.org/docs/crypto/EVP_BytesToKey.html).
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