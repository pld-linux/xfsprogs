--- xfsprogs-6.12.0/m4/package_icu.m4.orig	2024-11-21 12:56:04.000000000 +0100
+++ xfsprogs-6.12.0/m4/package_icu.m4	2025-01-14 21:41:08.360037770 +0100
@@ -1,5 +1,5 @@
 AC_DEFUN([AC_HAVE_LIBICU],
-  [ PKG_CHECK_MODULES([libicu], [icu-i18n], [have_libicu=yes], [have_libicu=no])
+  [ PKG_CHECK_MODULES([libicu], [icu-i18n icu-uc], [have_libicu=yes], [have_libicu=no])
     AC_SUBST(have_libicu)
     AC_SUBST(libicu_CFLAGS)
     AC_SUBST(libicu_LIBS)
