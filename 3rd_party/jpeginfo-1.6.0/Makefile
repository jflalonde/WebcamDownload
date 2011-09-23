# Generated automatically from Makefile.in by configure.
#########################################################################
# $Id: Makefile.in,v 1.8 2002/12/07 22:13:21 tjko Exp $ 
# 
# Makefile for jpeginfo 
#
Version = 1.6.0
PKGNAME = jpeginfo

SHELL = /bin/sh

DEFS = -DHAVE_CONFIG_H

srcdir = .

prefix = /Users/jflalonde/Documents/research/code/c++/3rd_party/jpeginfo-1.6.0
exec_prefix = ${prefix}

# Where to install the executables.
bindir = $(exec_prefix)/bin

# Where to put libraries
libdir = $(prefix)/lib

# Where to put the Info files
infodir = $(prefix)/share/info

# Where to put the manual pages.
mandir = $(prefix)/share/man



CC        = gcc 
XCPPFLAGS = 
CFLAGS    = -g -O2 $(XCPPFLAGS) $(DEFS)
LDFLAGS   = 
LIBS      = -ljpeg 
STRIP     = strip


INSTALL = /usr/bin/install -c
INSTALL_DATA = ${INSTALL} -m 644
INSTALL_PROGRAM = ${INSTALL}



# should be no reason to modify lines below this
#########################################################################

DIRNAME = $(shell basename `pwd`) 
DISTNAME  = $(PKGNAME)-$(Version)

OBJS = $(PKGNAME).o misc.o  md5.o 

$(PKGNAME):	$(OBJS) 
	$(CC) $(CFLAGS) -o $(PKGNAME) $(OBJS) $(LDFLAGS) $(LIBS) 

all:	$(PKGNAME) 

strip:
	for i in $(PKGNAME) ; do [ -x $$i ] && $(STRIP) $$i ; done

clean:
	rm -f *~ *.o core a.out make.log \#*\# $(PKGNAME) $(OBJS)

clean_all: clean
	rm -f Makefile config.h config.log config.cache config.status

dist:	clean_all
	(cd .. ; tar cvzf $(DISTNAME).tar.gz $(DIRNAME))

backup:	dist


install: all install.dirs install.man
	$(INSTALL) -m 755 $(PKGNAME) $(INSTALL_ROOT)/$(bindir)/$(PKGNAME)

printable.man:
	groff -Tps -mandoc ./$(PKGNAME).1 >$(PKGNAME).ps
	groff -Tascii -mandoc ./$(PKGNAME).1 | tee $(PKGNAME).prn | sed 's/.//g' >$(PKGNAME).txt

install.man:
	$(INSTALL) -m 644 $(PKGNAME).1 $(INSTALL_ROOT)/$(mandir)/man1/$(PKGNAME).1

install.dirs:
	$(INSTALL) -d -m 755 $(INSTALL_ROOT)/$(bindir)
	$(INSTALL) -d -m 755 $(INSTALL_ROOT)/$(mandir)/man1

# a tradition !
love:	
	@echo "Not War - Eh?"
# eof

