# -*- coding: utf-8 -*-
#
# Based on pybookshelf python plugin - http://code.google.com/p/pybookshelf/
# Author: sergei.stolyarov, GPLv2

# Ubuntu packages: python-lxml


import zipfile
from base64 import b64decode
from lxml import etree
import os.path
import copy

class Exception(Exception):
    pass


def _u(s):
    return unicode(s, 'UTF8')

nsmap = {
    'fb': "http://www.gribuser.ru/xml/fictionbook/2.0",
    'xlink': "http://www.w3.org/1999/xlink"
    }

def form_element(ns, element_name):
    """
        Form full qualified XML element name.
    """
    return "{%s}%s" % (nsmap[ns], element_name)

"""For fb version 2.0
"""
class Author20:
    fbns = "{%s}" % nsmap['fb']

    def __init__(self, author_node=None):

        self.firstname = None
        self.middlename = None
        self.lastname = None
        self.nickname = None
        self.homepage = None
        self.email = None

        if author_node is None:
            return

        ns = Author20.fbns

        elements = {
            ns+"first-name": u"",
            ns+"middle-name": u"",
            ns+"last-name": u"",
            ns+"nickname": u""}

        for c in author_node:
            elements[c.tag] = c.text.strip() if c.text is not None else None

        self.firstname = elements[ns+"first-name"]
        self.middlename = elements[ns+"middle-name"]
        self.lastname = elements[ns+"last-name"]
        self.nickname = elements[ns+"nickname"]

    def format(self, formatstr=""):
        if formatstr != "":
            return formatstr % {
                'firstname': self.firstname,
                'middlename': self.middlename,
                'lastname': self.lastname,
                'nickname': self.nickname
                }

        args = []
        for s in (self.lastname, self.firstname, self.middlename):
            if s:
                args.append(s)
        if not self.nickname is None and "" != self.nickname:
            args.append(u"(%s)" % self.nickname)

        return u" ".join(args)

    def element(self):
        """
        Return lxml.etree._Element instance that corresponds given author details
        """
        ns = Author20.fbns

        e = etree.Element(ns+"author", nsmap=nsmap)

        def append_elem(name, value):
            if value is None:
                return
            sube = etree.Element(ns+name, nsmap=nsmap)
            sube.text = value
            e.append(sube)

        # the only allowed situations:
        #   firstname!=None and lastname!=None
        #   or
        #   nickname!=None and firstname==None and middlename==None and lastname==None

        if not (not self.firstname is None and not self.lastname is None):
            if self.nickname is None or not (self.firstname is None and self.middlename is None and self.lastname is None):
                raise Exception, "Incorrect author components!"

        append_elem("first-name", self.firstname)
        append_elem("middle-name", self.middlename)
        append_elem("last-name", self.lastname)
        append_elem("nickname", self.nickname)
        append_elem("home-page", self.homepage)
        append_elem("email", self.email)
        return e

class Document:

    def __init__(self, text=None, filename=None):
        self.__doc = None
        self.__authors_list = None
        self.__title = None
        self.__genres = None
        self.__annotation = None
        self.__annotation_doc = None
        self.__title_covers = None
        self.__images = None
        self.__sequences = None
        self.new_title = None

        try:
            if text:
                self.__doc = etree.ElementTree(etree.fromstring(text))
            elif text=="":
                raise Exception, "Invalid content: text is empty"
            else:
                f = open(filename)
                parser = etree.XMLParser(recover=True) #recover bad chars
                self.__doc = etree.parse(f, parser)
                f.close()

        except etree.XMLSyntaxError, error:
            raise Exception, error

        # check that document is really FictionBook2 file
        root = self.__doc.getroot()
        if not root or not root.tag == "{http://www.gribuser.ru/xml/fictionbook/2.0}FictionBook":
            raise Exception, "Not FictionBook2 document"

    def __str__(self):
        document_encoding = self.__doc.docinfo.encoding
        return etree.tostring(self.__doc, encoding=document_encoding, xml_declaration=True)

    def write (self, file):
        """
        Save document to the file
        """

    def __xpath(self, expr):
        return self.__doc.xpath(expr, namespaces=nsmap)

    def authors(self):
        """
        Return list of book authors, unique list
        """
        if not self.__authors_list:
            self.__authors_list = []
            authors_hash = []
            nodeset = self.__xpath("/fb:FictionBook/fb:description/fb:title-info/fb:author")
            for node in nodeset:
                a = Author20(node)
                af = a.format()
                if not af in authors_hash:
                    authors_hash.append(a.format())
                    self.__authors_list.append(a)

        return self.__authors_list

    def set_authors(self, authors_list):
        """
        Set new authors list
        """
        # update xml tree
        nodeset = self.__xpath("/fb:FictionBook/fb:description/fb:title-info/fb:author")
        first = nodeset[0]

        for a in authors_list:
            first.addprevious(a.element())

        for node in nodeset:
            # remember first element
            if first is None:
                first = node
                continue
            # delete others
            node.getparent().remove(node)

        self.__authors_list = copy.deepcopy(authors_list)

    def genres(self):
        if self.__genres is None:
            self.__genres = []
            nodeset = self.__xpath("/fb:FictionBook/fb:description/fb:title-info/fb:genre")
            genres_hash = []

            for node in nodeset:
                genre = node.text
                if genre is None:
                    continue

                try:
                    genre_match = int(node.get("match"))
                    # genre_match must be integer in range(1, 99)
                    if genre_match < 1 or genre_match > 99:
                        genre_match = None
                except ValueError:
                    genre_match = None
                except TypeError:
                    genre_match = None

                if not genre in genres_hash:
                    self.__genres.append((genre, genre_match))
                    genres_hash.append(genre)

        return self.__genres

    def title(self):
        if not self.__title:
            nodeset = self.__xpath("/fb:FictionBook/fb:description/fb:title-info/fb:book-title")

            if not len(nodeset):
                raise Exception, "Book must have `book-title' element!"
            self.__title =  nodeset[0].text

        return self.__title

    def set_title(self, new_title):
        nodeset = self.__xpath("/fb:FictionBook/fb:description/fb:title-info/fb:book-title")
        if not len(nodeset):
            raise Exception, "Book must have `book-title' element!"
        nodeset[0].text = new_title
        self.__title = new_title

    def annotation_doc(self):
        """
            Return annotation of the book as etree object
        """
        if not self.__annotation_doc:
            self.__annotation = None
            nodeset = self.__xpath("/fb:FictionBook/fb:description/fb:title-info/fb:annotation")
            if len(nodeset):
                self.__annotation_doc = etree.ElementTree(nodeset[0])

        return self.__annotation_doc

    def annotation(self):
        """
            Return annotation of the book, in XML. You should manually parse it before showing.
        """
        if not self.__annotation:
            doc = self.annotation_doc()
            if doc:
                self.__annotation = etree.tostring(doc, encoding="UTF-8")

        return self.__annotation

    def annotation_text(self):
        """
            Return annotation as simple text (with \n)
        """
        #TODO
        ann = self.annotation()
        if not ann:
            return ''

        return ann

    def covers(self, cache_dir, prefix="file_"):
        """
            Return list of all covers from "title-info" element. Covers from "src-title-info"
            should be extracted by the other function.

            Returned list contains full paths to extracted covers.
        """
        if not self.__title_covers:
            self.__title_covers = []

            # try to extract covers and to fill a list
            nodeset = self.__xpath("/fb:FictionBook/fb:description/fb:title-info/fb:coverpage/fb:image")

            num = 0

            for node in nodeset:
                href = node.get(form_element("xlink", "href"))
                num += 1

                # extract cover
                covers_nodes = self.__xpath('//fb:binary[@id="%s"]' % href[1:]) # remove first symbol - #
                for cn in covers_nodes:
                    img = b64decode(cn.text)
                    # save text into the file
                    outfile = os.path.join(cache_dir, "%s%d" % (prefix, num) )
                    out = open(outfile, "w")
                    out.write(img)
                    out.close()
                    self.__title_covers.append(outfile)
                    break

        return self.__title_covers

    def sequences(self):
        """
            Return list of sequences, i.e. series
        """
        if self.__sequences is None:
            self.__sequences = []

            seq_nodes = self.__xpath("/fb:FictionBook/fb:description/fb:title-info/fb:sequence")
            for node in seq_nodes:
                s = {}
                s["name"] = node.get("name")
                s["number"] = node.get("number")
                self.__sequences.append(s)

        return self.__sequences

    def html(self, xslt):
        """
            Transform fb2 to html
            Argument: xslt - path to xslt-file
            Return: html as string
        """
        f = open(xslt)
        xslt_doc = etree.parse(f)
        f.close()

        # FIXME: possible unicode issues?
        transform = etree.XSLT(xslt_doc)
        result = transform(self.__doc)
        return str(result)

    def images(self):
        if not self.__images:
            self.__images = []
            images_nodes = self.__xpath('//fb:binary')
            for node in images_nodes:
                #print node, node.get('id'), node.get('content-type')
                img = b64decode(node.text)
                self.__images.append((img, node.get('id'),
                    node.get('content-type')))

        return self.__images

def parse(text, validate=False):
    """
        Parse text and return Document object
    """
    return Document(text=text)

def parse_file(filename, validate=False):
    """
        Parse file (.fb2 or .fb2.zip) and return Document object. Loose parsing.
    """
    doc = None
    if filename.lower().endswith(".fb2"):
        doc = Document(filename=filename)
    else:
        # treat file as zip-file
        try:
            zz = zipfile.ZipFile(filename, 'r', zipfile.ZIP_STORED, True)
        except zipfile.BadZipfile, e:
            # file is not a zip-file so pass it as is
            doc = Document(filename=filename)
        except IOError, e:
            # read error
            raise Exception, "ZIP IOError: %s" % e
        else:
            listing = zz.namelist()
            if not len(listing):
                raise Exception, "Provided ZIP-file is empty"

            # take first file from archive
            first = listing[0]
            if not first.lower().endswith(".fb2"):
                raise Exception, "Provided ZIP-archive doesn't contain FB2-file"

            content = zz.read(listing[0])
            zz.close()
            doc = Document(text=content)

    return doc