/* jpeginfo.h
 *
 * Copyright (c) Timo Kokkonen, 1997.
 *
 * $Id: jpeginfo.h,v 1.4 2002/12/10 09:58:34 tjko Exp $
 */


#define MIN(a,b) (a<b?a:b)


/* misc.c */

int  is_dir(FILE *fp);
long filesize(FILE *fp);
void delete_file(char *name, int verbose_mode, int quiet_mode);
char *fgetstr(char *s,int n,FILE *stream);
char *md2str(unsigned char *digest, char *s);


/* eof :-) */
