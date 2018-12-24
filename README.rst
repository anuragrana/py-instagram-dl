=====
py_instagram_dl
=====

This python package let you download all the pictures of an instagram user.


Quick start
-----------

- Create a virtual environment. Optional but recommended. You can refer below article.

   https://www.pythoncircle.com/post/404/virtual-environment-in-python-a-pocket-guide/

- Install dependencies::

    pip install beautifulsoup4 bs4 lmxl requests urllib3

- Install the package::

    pip install py_instagram_dl

- Use the package in your code. Example below::

    import py_instagram_dl as pyigdl
    import sys

    try:
        pyigdl.download(sys.argv[1], wait_between_requests=1)
    except Exception as e:
        print(e)


- Please visit below link for more details and source code.

    https://www.pythoncircle.com/post/447/py_instagram_dl-the-python-package-to-download-all-pictures-of-an-instagram-user/


.





