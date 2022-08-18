# Try using setuptools first, if it's installed
try:
 from setuptools import setup
except:
 print('Install the setuptools module (pip3 install setuptools)')
 quit()

if __name__ == '__main__':
    setup()
    quit()

