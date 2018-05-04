
from distutils.core import setup, Extension
 
module1 = Extension('pyvicon', 
                sources=['pyvicon_class.cpp'], 
                libraries=['ViconDataStreamSDK_CPP'],
				library_dirs=['.','C:\Program Files\Vicon\DataStream SDK\Win64\CPP'])

setup (name = 'PyVicon',
        version = '1.0',
        description = 'Python bindings to the ViconDataStream SDK',
        ext_modules = [module1])