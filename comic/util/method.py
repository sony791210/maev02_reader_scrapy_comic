
import os


def creatDir(name="test",path=0,page=0):
    if(name=="test"):
        return False
    if not (os.path.exists('comic_info')):
        os.mkdir('comic_info')
    if not (os.path.exists( ('comic_info/%s')%(name) )):
        os.mkdir( ('comic_info/%s')%(name))
    if(path==0):
        return False
    if not (os.path.exists(('comic_info/%s/%s')%(name,path))):
        os.mkdir(('comic_info/%s/%s')%(name,path))
    