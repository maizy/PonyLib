# _*_ coding: utf-8 _*_

__license__         = "GPL3"
__copyright__       = "Copyright 2010-2011 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = ""


import os
import sys


class Iterator(object):



    roots = None

    def __init__(self, roots = None):
        if roots:
            self.roots = roots


    def __iter__(self):
        return self.next()


    def next(self):
        """
        Generate pair (root_path, relative_file_path)

        Full filepath = os.path.join(root_path, relative_file_path)
        """
        if not self.roots or len(self.roots) == 0:
            raise StopIteration

        for root_path in self.roots:
            root_path = os.path.realpath(root_path)
            path_iter = os.walk(root_path, followlinks=True)

            for (dirpath, dirnames, filenames) in path_iter:
                # ignore dirs start with '.'
                # dirnames can be modified dinamically (but mutable only)
                dirnames[:] = [dir for dir in dirnames if dir[0] != '.']

                assert dirpath == root_path or dirpath.startswith(root_path+'/')
                
                if dirpath != root_path:
                    rel_dirpath = dirpath[len(root_path)+1:]
                else:
                    rel_dirpath = ''

                for file in filenames:
                    if file[0] != '.':
#                        i -= 1
#                        if i < 0:
#                            raise StopIteration

                        yield (root_path, os.path.join(rel_dirpath, file))

            raise StopIteration