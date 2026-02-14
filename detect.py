"""
Purpose: monitor added content in a bunch of web pages and store changes in a file
"""

# using native Unix tools: curl, diff, etc.

# What it does:
# - read a list of urls from a file
# - for each url, fetch the content and store it in a file
# - if the content has changed since the last fetch, append the diff to a file
# - make that into an html file
#
# Additionally: rate limit, max 1 check per day

import os

# List of paths:
urls_file = 'urls.txt'
html_folder = 'html'
changes_file = 'changes.xml'
html_pre = "html_pre.xml"
html_post = "html_post.xml"
html_file = 'changes.html'

# touch all the files to make sure they exist
os.system(f'touch {urls_file}')
os.makedirs(html_folder, exist_ok=True)
os.system(f'touch {changes_file}')

# first read the file
with open(urls_file, 'r') as f:
    urls = f.read().splitlines()

for url in urls:
    # create a filename from the url
    filename = os.path.join(html_folder,
        url.replace('https://', '').replace('http://', '').replace('/', '_') + '.html')

    # print(f'Checking {url}...')

    # fetch the content
    os.system(f'curl -s {url} -o {filename+".new"}')

    # check if the file exists
    if os.path.exists(filename):
        # if it exists, compare the new file with the old file
        os.system(f"diff --new-line-format='%L' --old-line-format='' --unchanged-line-format='' {filename} {filename+'.new'} > {filename+'.diff'}")

        # if there is a diff, append it to the changes file
        if os.path.exists(filename+".diff") and os.path.getsize(filename+".diff") > 0:

            with open(filename+".diff", 'r') as diff_file:

                content=diff_file.read()

                # verify content actually has html content, not just
                # property changes or id changes in div metadata and such
                if (
                    "</div>" in content
                    or
                    "<p>" in content
                    or
                    "<h1>" in content
                    or
                    "<h2>" in content
                    or
                    "<h3>" in content
                    or
                    "<h4>" in content
                    or
                    "<h5>" in content
                    or
                    "<h6>" in content
                    or
                    "<a" in content
                    or
                    "<img" in content
                    or
                    "<span" in content
                    or
                    "<li" in content
                    ):


                    print("Found changes in " + url)

                    with open(changes_file, 'a') as f:

                        f.write(f'<h2><a href="{url}">{url}</a></h2>\n')
                        f.write(content)
                        f.write('<hr><br>\n')

        if os.path.exists(filename+".diff"):
            os.remove(filename+".diff")

    # move the new file to the old file
    # print(os.listdir(html_folder))
    # os.system("cat " + filename + ".new")
    # os.remove(filename) if os.path.exists(filename) else None
    os.rename(filename+".new", filename)
    # print(os.listdir(html_folder))


# make that into an html file by concatenation
os.system(f"cat {html_pre} {changes_file} {html_post} > {html_file}")
