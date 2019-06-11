# place this file in ~/.ipython/profile_default/startup/start.py
# it will be launched by jupyter upon kernel launch

from jpype import startJVM, getDefaultJVMPath
from os.path import dirname, join, abspath

JAVA_OpenXAL=join(dirname(abspath(__file__)),'../build/dist/lib/xal-shared.jar')
JAVA_ClassPath='-Djava.class.path='+JAVA_OpenXAL
JAVA_Flags='-ea'
try:
    startJVM(getDefaultJVMPath(), JAVA_Flags, JAVA_ClassPath)
except:
    pass



