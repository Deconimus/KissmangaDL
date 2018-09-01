import sys, os, re, argparse, bs4, shutil

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader

from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlopen, Request

from selenium_helper import get_chapters_list_html, get_image_urls


user_agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 " \
				+ "(KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"

DOMAIN = 'http://kissmanga.com'


def get_chapters(manga_url):

	page = get_chapters_list_html(manga_url)
	if not page:
		print('Failed to load chapters')
		sys.exit(0)
	soup = bs4.BeautifulSoup(page, "lxml")
	table = soup.find('table', attrs={"class": "listing"})

	data = []
	for row in table.find_all('tr'):
		cells = row.find_all("td")
		if not cells:
			continue
		a_tag = cells[0].find('a')
		data.append({
			"chapter_name": re.sub('[^\w\s-]', '', a_tag.get_text().strip().replace(':', " -")),
			"link": DOMAIN + a_tag['href'] if not a_tag['href'].startswith(DOMAIN) else a_tag['href']
		})
	return data


def generate_pdf(chapter_name, images_dir, out_file_path):
	
	canvas = Canvas(out_file_path)
	canvas.setTitle(chapter_name)
	
	print("Generating PDF", end="", flush=True)
	
	for file in os.listdir(images_dir):
		if os.path.isdir(file) or not isImage(file): continue
		
		image = ImageReader(images_dir+"/"+file)
		canvas.setPageSize(image.getSize())
		canvas.drawImage(image, x=0, y=0)
		canvas.showPage()
		print(".", end="", flush=True)
		
	print("", flush=True)
		
	canvas.save()
	
	
def isImage(file):
	ext = file[file.rindex(".")+1:].lower().strip()
	return ext == "png" or ext == "jpg" or ext == "jpeg" or ext == "gif" or ext == "bmp"


def download_images(out_file_path, images):
	
	with ThreadPoolExecutor(max_workers=16) as xec:
		
		for i in range(0, len(images)):
			
			url = images[i]
			xec.submit(save_image, out_file_path, url, i, url[url.rindex("."):])
		
		
def save_image(dir, url, index, ext):
	
	req = Request(url)
	req.add_header("User-Agent", user_agent)
	
	with urlopen(req) as resp:
		with open(dir+"/"+str(index+1).zfill(3)+ext, "wb+") as f:
			f.write(resp.read())
	
	print("Saved "+str(index+1).zfill(3)+ext)


def download_chapter(chapter, output_dir, makepdf=False):
	
	if makepdf:
		out_file_path = output_dir+"/"+chapter['chapter_name']+".pdf"
	else:
		out_file_path = output_dir+"/"+chapter['chapter_name']
	
	if os.path.exists(out_file_path):
		print('Already exists: %s' % out_file_path)
		return
	
	images = get_image_urls(url=chapter['link'])
	if not images:
		print("Failed to get chapter image urls")
		return
	
	if makepdf:
		
		tmpdir = ""
		imagedir = out_file_path[:-4]
		
		if not imagedir_complete(imagedir, images):
			
			tmpdir = output_dir+"/tmp"
			if os.path.isdir(tmpdir):
				shutil.rmtree(tmpdir)
			os.makedirs(tmpdir)
			imagedir = tmpdir
		
			download_images(imagedir, images)
			
		generate_pdf(chapter["chapter_name"], imagedir, out_file_path)
		
		if tmpdir:
			shutil.rmtree(tmpdir)
		
	else:
		
		if not os.path.isdir(out_file_path):
			os.makedirs(out_file_path)
			
		download_images(out_file_path, images)


def imagedir_complete(imagedir, images):
	if os.path.isdir(imagedir):
		return False
	ind = 1
	for img in images:
		if not os.path.exists(imagedir+"/"+str(ind).zfill(3)+(img[img.rindex("."):]).lower()):
			return False
		ind += 1
	return True


def main():

	parser = argparse.ArgumentParser(description="Download manga from kissmanga.com in pdf format",
							 		 usage='%(prog)s url [-o output_dir]')
	
	parser.add_argument('url', help='Manga url')
	parser.add_argument("-o", default='output/', help="Output dir path")
	parser.add_argument("-pdf", action="store_true", help="Save chapters as PDF's.")
	
	args = parser.parse_args()
	manga_url = args.url
	output_dir = args.o
	makepdf = args.pdf
	
	if not manga_url.startswith(DOMAIN):
		print("Manga url is not supported.")
		print("Only kissmanga.com is supported.")
		return
	
	if manga_url.endswith('/'):
		manga_url = manga_url[:-1]
	
	output_dir = output_dir + "/" + manga_url.split('/')[-1].lower()
	
	print('Manga url: '+manga_url)
	print('Output dir: '+output_dir)
	
	if not os.path.isdir(output_dir):
		os.makedirs(output_dir)
	
	chapters = get_chapters(manga_url)
	
	for chapter in chapters:
		print("\n\n")
		print(chapter['chapter_name'])
		download_chapter(chapter, output_dir, makepdf)


if __name__ == "__main__":
	
	main()
	