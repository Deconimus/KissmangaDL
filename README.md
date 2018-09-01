## KissmangaDL
Download manga from kissmanga and optionally save chapters as PDF files.

### How to use:
```python
python kissmangadl.py "http://kissmanga.com/Manga/One-Piece" -o some/output/directory -pdf
```

#### Options:

`-o` sets the output directory. Default is `output/` inside kissmangadl's directory. <br>
`-pdf` optional flag to save chapters as PDF files.

### Requirements:
* Python3
* PIP

### Installing dependencies:
```
pip install -r requirements.txt
```
[How to use PIP](https://www.makeuseof.com/tag/install-pip-for-python/)

### History:

This is a fork from [pratikhit07's kissmanga-pdf-downloader](https://github.com/pratikhit07/kissmanga-pdf-downloader). <br>
The code was ported to Python 3. Changes and/or improvements are listed below:

#### Changes:
* Added support for Windows
* Improved speed by concurrently downloading images
* Saving chapters as PDF's is now optional
* By default the script saves chapters as directories containing the pages as image files
