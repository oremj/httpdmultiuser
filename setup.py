from distutils.core import setup


setup(name="httpdmultiuser",
      version="0.1a",
      author='Jeremiah Orem',
      author_email='oremj@mozilla.com',
      package_dir={'httpdmultiuser': 'src/httpdmultiuser'},
      packages=['httpdmultiuser'],
      license='BSD',
      scripts=['src/httpd_multiuser_util'],
      )
