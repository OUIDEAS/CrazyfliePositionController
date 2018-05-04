# magical init file all over again
#from pyvicon_class import PyVicon
import sys
if sys.platform == 'linux2':
    import DLFCN as dl
    flags = sys.getdlopenflags()
    sys.setdlopenflags(dl.RTLD_NOW|dl.RTLD_GLOBAL)
    from pyvicon_class import PyVicon
    sys.setdlopenflags(flags)
else:
    #import os
    #cwd = os.getcwd()
    #print(cwd)
    from python_vicon.pyvicon_class import PyVicon
