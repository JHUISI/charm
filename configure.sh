#!/bin/sh
#
# charm-crypto configure script
# (adapted from the qemu source)
#
# set temporary file name
if test ! -z "$TMPDIR" ; then
    TMPDIR1="${TMPDIR}"
elif test ! -z "$TEMPDIR" ; then
    TMPDIR1="${TEMPDIR}"
else
    TMPDIR1="/tmp"
fi

TMPC="${TMPDIR1}/charm-conf-${RANDOM}-$$-${RANDOM}.c"
TMPO="${TMPDIR1}/charm-conf-${RANDOM}-$$-${RANDOM}.o"
TMPE="${TMPDIR1}/charm-conf-${RANDOM}-$$-${RANDOM}.exe"

# NB: do not call "exit" in the trap handler; this is buggy with some shells;
# see <1285349658-3122-1-git-send-email-loic.minier@linaro.org>
trap "rm -f $TMPC $TMPO $TMPE" EXIT INT QUIT TERM
rm -f config.log config.ld

compile_object() {
  echo $cc $CHARM_CFLAGS -c -o $TMPO $TMPC >> config.log
  $cc $CHARM_CFLAGS -c -o $TMPO $TMPC >> config.log 2>&1
}

compile_prog() {
  local_cflags="$1"
  local_ldflags="$2"
  echo $cc $CHARM_CFLAGS $local_cflags -o $TMPE $TMPC $LDFLAGS $local_ldflags >> config.log
  $cc $CHARM_CFLAGS $local_cflags -o $TMPE $TMPC $LDFLAGS $local_ldflags >> config.log 2>&1
}

check_library() {
   lib_test="$1"
   tmp_file="$2"
   $cc $LDFLAGS $lib_test 2> $tmp_file
   grep "main" $tmp_file > /dev/null
   result=$?
#   echo "Result => $result"
   return $result
}

# symbolically link $1 to $2.  Portable version of "ln -sf".
symlink() {
  rm -f $2
  ln -s $1 $2
}

# check whether a command is available to this shell (may be either an
# executable or a builtin)
has() {
    type "$1" >/dev/null 2>&1
}

# search for an executable in PATH
path_of() {
    local_command="$1"
    local_ifs="$IFS"
    local_dir=""

    # pathname has a dir component?
    if [ "${local_command#*/}" != "$local_command" ]; then
        if [ -x "$local_command" ] && [ ! -d "$local_command" ]; then
            echo "$local_command"
            return 0
        fi
    fi
    if [ -z "$local_command" ]; then
        return 1
    fi

    IFS=:
    for local_dir in $PATH; do
        if [ -x "$local_dir/$local_command" ] && [ ! -d "$local_dir/$local_command" ]; then
            echo "$local_dir/$local_command"
            IFS="${local_ifs:-$(printf ' \t\n')}"
            return 0
        fi
    done
    # not found
    IFS="${local_ifs:-$(printf ' \t\n')}"
    return 1
}

# default parameters
source_path=`dirname "$0"`
cpu=""
static="no"
cross_prefix=""
host_cc="gcc"
helper_cflags=""
cc_i386=i386-pc-linux-gnu-gcc

# Default value for a variable defining feature "foo".
#  * foo="no"  feature will only be used if --enable-foo arg is given
#  * foo=""    feature will be searched for, and if found, will be used
#              unless --disable-foo is given
#  * foo="yes" this value will only be set by --enable-foo flag.
#              feature will searched for,
#              if not found, configure exits with error
#
# Always add --enable-foo and --disable-foo command line args.
# Distributions want to ensure that several features are compiled in, and it
# is impossible without a --enable-foo that exits if a feature is not found.
docs="no"
sphinx_build="$(which sphinx-build)"
integer_module="yes"
ecc_module="yes"
pairing_module="yes"
pairing_miracl="no"
pairing_relic="no"
pairing_pbc="yes"
disable_benchmark="no"
integer_ssl="no"
integer_gmp="yes"
python_version=""
gprof="no"
debug="no"
mingw32="no"
EXESUF=""
prefix="/usr/local"
mandir="\${prefix}/share/man"
datadir="\${prefix}/share/charm"
docdir="\${prefix}/share/doc/charm"
bindir="\${prefix}/bin"
libdir="\${prefix}/lib"
sysconfdir="\${prefix}/etc"
confsuffix="/charm"
profiler="no"
wget="$(which wget)"
 
# set -x

# parse CC options first
for opt do
  optarg=`expr "x$opt" : 'x[^=]*=\(.*\)'`
  case "$opt" in
  --cross-prefix=*) cross_prefix="$optarg"
  ;;
  --cc=*) CC="$optarg"
  ;;
  --source-path=*) source_path="$optarg"
  ;;
  --cpu=*) cpu="$optarg"
  ;;
  --extra-cflags=*) CHARM_CFLAGS="$optarg $CHARM_CFLAGS"
  ;;
  --extra-ldflags=*) LDFLAGS="$optarg $LDFLAGS"
  ;;
  --extra-cppflags=*) CPPFLAGS="$optarg $CPPFLAGS"
  ;;
  --python-build-ext=*) PYTHONBUILDEXT="$optarg" 
  esac
done
# OS specific
# Using uname is really, really broken.  Once we have the right set of checks
# we can eliminate it's usage altogether

cc="${cross_prefix}${CC-gcc}"
ar="${cross_prefix}${AR-ar}"
objcopy="${cross_prefix}${OBJCOPY-objcopy}"
ld="${cross_prefix}${LD-ld}"
windres="${cross_prefix}${WINDRES-windres}"
pkg_config="${cross_prefix}${PKG_CONFIG-pkg-config}"
sdl_config="${cross_prefix}${SDL_CONFIG-sdl-config}"

# default flags for all hosts
#CHARM_CFLAGS="-fno-strict-aliasing $CHARM_CFLAGS"
CFLAGS="-g $CFLAGS"
CHARM_CFLAGS="-Wall -Wundef -Wwrite-strings -Wmissing-prototypes $CHARM_CFLAGS"
#CHARM_CFLAGS="-Wstrict-prototypes -Wredundant-decls $CHARM_CFLAGS"
#CHARM_CFLAGS="-D_GNU_SOURCE -D_FILE_OFFSET_BITS=64 -D_LARGEFILE_SOURCE $CHARM_CFLAGS"
#CHARM_CFLAGS="-D_FORTIFY_SOURCE=2 $CHARM_CFLAGS"
CHARM_INCLUDES="-I. -I\$(SRC_PATH)"
# Need to add an --enable-debugging flag.
#LDFLAGS="-g $LDFLAGS"

# make source path absolute
source_path=`cd "$source_path"; pwd`

check_define() {
cat > $TMPC <<EOF
#if !defined($1)
#error Not defined
#endif
int main(void) { return 0; }
EOF
  compile_object
}

if test ! -z "$cpu" ; then
  # command line argument
  :
elif check_define __i386__ ; then
  cpu="i386"
elif check_define __x86_64__ ; then
  cpu="x86_64"
elif check_define __sparc__ ; then
  # We can't check for 64 bit (when gcc is biarch) or V8PLUSA
  # They must be specified using --sparc_cpu
  if check_define __arch64__ ; then
    cpu="sparc64"
  else
    cpu="sparc"
  fi
elif check_define _ARCH_PPC ; then
  if check_define _ARCH_PPC64 ; then
    cpu="ppc64"
  else
    cpu="ppc"
  fi
elif check_define __mips__ ; then
  cpu="mips"
elif check_define __ia64__ ; then
  cpu="ia64"
elif check_define __s390__ ; then
  if check_define __s390x__ ; then
    cpu="s390x"
  else
    cpu="s390"
  fi
else
  cpu=`uname -m`
fi

case "$cpu" in
  alpha|cris|ia64|lm32|m68k|microblaze|ppc|ppc64|sparc64|unicore32|armv6l|armv7l|s390|s390x|arm64|aarch64)
    cpu="$cpu"
  ;;
  i386|i486|i586|i686|i86pc|BePC)
    cpu="i386"
  ;;
  x86_64|amd64)
    cpu="x86_64"
  ;;
  *)
    echo "Unsupported CPU = $cpu"
    exit 1
  ;;
esac

# OS specific
if check_define __linux__ ; then
  targetos="Linux"
elif check_define _WIN32 ; then
  targetos='MINGW32'
elif check_define __OpenBSD__ ; then
  targetos='OpenBSD'
elif check_define __sun__ ; then
  targetos='SunOS'
elif check_define __HAIKU__ ; then
  targetos='Haiku'
else
  targetos=`uname -s`
fi

: ${make=${MAKE-make}}
: ${install=${INSTALL-install}}

if [ "$targetos" = "MINGW32" ] ; then
  EXESUF=".exe"
  CHARM_CFLAGS="-DWIN32_LEAN_AND_MEAN -DWINVER=0x501 $CHARM_CFLAGS"
  # enable C99/POSIX format strings (needs mingw32-runtime 3.15 or later)
  CHARM_CFLAGS="-D__USE_MINGW_ANSI_STDIO=1 $CHARM_CFLAGS"
  LIBS="-lwinmm -lws2_32 -liberty -liphlpapi $LIBS"
  #If you are building for NSIS executable, set prefix to /c/charm-crypto
  prefix="/mingw"
  mandir="\${prefix}"
  datadir="\${prefix}"
  docdir="\${prefix}"
  bindir="\${prefix}"
  sysconfdir="\${prefix}"
  confsuffix=""
fi

werror=""

for opt do
  optarg=`expr "x$opt" : 'x[^=]*=\(.*\)'`
  case "$opt" in
  --help|-h) show_help=yes
  ;;
  --version|-V) exec cat "$source_path/VERSION"
  ;;
  --prefix=*) prefix="$optarg"
  ;;
  --source-path=*)
  ;;
  --cross-prefix=*)
  ;;
  --cc=*)
  ;;
  --host-cc=*) host_cc="$optarg"
  ;;
  --make=*) make="$optarg"
  ;;
  --install=*) install="$optarg"
  ;;
  --extra-cflags=*)
  ;;
  --extra-ldflags=*)
  ;;
  --extra-cppflags=*)
  ;;
  --python-build-ext=*)
  ;;
  --cpu=*)
  ;;
  --enable-gprof) gprof="yes"
  ;;
  --static)
    static="yes"
    LDFLAGS="-static $LDFLAGS"
  ;;
  --mandir=*) mandir="$optarg"
  ;;
  --bindir=*) bindir="$optarg"
  ;;
  --libdir=*) libdir="$optarg"
  ;;
  --datadir=*) datadir="$optarg"
  ;;
  --docdir=*) docdir="$optarg"
  ;;
  --sysconfdir=*) sysconfdir="$optarg"
  ;;
  --disable-integer) integer_module="no"
  ;;
  --disable-ecc) ecc_module="no"
  ;;
  --disable-pairing) pairing_module="no"
  ;;
  --disable-benchmark) disable_benchmark="yes"
  ;;
  --enable-pairing-miracl=*) 
    echo "Enabling this option assumes you have unzipped the MIRACL library into charm-src/pairingmath/miracl/ and make sure the library is built in that directory."
  	pairing_arg="$optarg" ;
  	pairing_pbc="no";
  	pairing_miracl="yes" ;
  	pairing_relic="no"
  ;;	
  --enable-pairing-pbc)
    pairing_pbc="yes" ;
    pairing_miracl="no";
    pairing_relic="no"
  ;;
  --enable-pairing-relic)
    pairing_relic="yes";
    pairing_pbc="no" ;
    pairing_miracl="no"
  ;;
  --enable-integer-openssl)
    echo "integer module using openssl not supported yet."
    #integer_ssl="yes" ; 
    #integer_gmp="no"
  ;;
  --enable-integer-gmp)
    integer_gmp="yes" ;
    integer_ssl="no"
  ;;
  --enable-integer-relic)
    echo "integer module using RELIC not supported yet."
  ;;
  --enable-debug)
      # Enable debugging options that aren't excessively noisy
      debug="yes"
  ;;
  --enable-darwin) darwin="yes"
  ;;
  --enable-profiler) profiler="yes"
  ;;
  --enable-werror) werror="yes"
  ;;
  --disable-werror) werror="no"
  ;;
  --disable-docs) docs="no"
  ;;
  --enable-docs) docs="yes"
  ;;
  --sphinx-build=*) sphinx_build="$optarg"
  ;;
  --python=*) python_path="$optarg"
  ;;
  --build-win-exe) LDFLAGS="-L/c/charm-crypto/lib $LDFLAGS" CPPFLAGS="-I/c/charm-crypto/include -I/c/charm-crypto/include/openssl/ $CPPFLAGS" prefix="/c/charm-crypto" PYTHONBUILDEXT="-L/c/charm-crypto/lib -I/c/charm-crypto/include/"
  ;;
  --*dir)
  ;;
  *) echo "ERROR: unknown option $opt"; show_help="yes"
  ;;
  esac
done


#
# If cpu ~= sparc and  sparc_cpu hasn't been defined, plug in the right
# CHARM_CFLAGS/LDFLAGS (assume sparc_v8plus for 32-bit and sparc_v9 for 64-bit)
#
host_guest_base="no"
case "$cpu" in
    i386)
           CHARM_CFLAGS="-m32 $CHARM_CFLAGS"
           LDFLAGS="-m32 $LDFLAGS"
           cc_i386='$(CC) -m32'
           helper_cflags="-fomit-frame-pointer"
           host_guest_base="yes"
           ;;
    x86_64)
           CHARM_CFLAGS="-m64 $CHARM_CFLAGS"
           LDFLAGS="-m64 $LDFLAGS"
           cc_i386='$(CC) -m32'
           host_guest_base="yes"
           ;;
esac

[ -z "$guest_base" ] && guest_base="$host_guest_base"

if test x"$show_help" = x"yes" ; then
cat << EOF

Usage: configure [options]
Options: [defaults in brackets after descriptions]

EOF
echo "Standard options:"
echo "  --help                   print this message"
echo "  --prefix=PREFIX          install in PREFIX [$prefix]"
echo ""
echo "Advanced options:"
echo "  --source-path=PATH       path of source code [$source_path]"
echo "  --cross-prefix=PREFIX    use PREFIX for compile tools [$cross_prefix]"
echo "  --cc=CC                  use C compiler CC [$cc]"
echo "  --host-cc=CC             use C compiler CC [$host_cc] for code run at build time"
echo "  --extra-cflags=CFLAGS    append extra C compiler flags CHARM_CFLAGS"
echo "  --extra-ldflags=LDFLAGS  append extra linker flags LDFLAGS"
echo "  --extra-cppflags=CPPFLAG append extra c pre-processor flags CPPFLAGS"
echo "  --make=MAKE              use specified make [$make]"
echo "  --python=PATH            use specified path to python 3, if not standard"
echo "  --python-build-ext=OPTS  append extra python build_ext options OPTS"
echo "  --install=INSTALL        use specified install [$install]"
echo "  --static                 enable static build [$static]"
echo "  --mandir=PATH            install man pages in PATH"
echo "  --datadir=PATH           install firmware in PATH"
echo "  --docdir=PATH            install documentation in PATH"
echo "  --bindir=PATH            install binaries in PATH"
echo "  --sysconfdir=PATH        install config in PATH/CHARM"
echo "  --enable-debug           enable common debug build options"
echo "  --disable-integer        disable INTEGER base module"
echo "  --disable-ecc            disable ECC base module"
echo "  --disable-pairing        disable PAIRING base module"
echo "  --enable-pairing-miracl= enable MIRACL lib for pairing module. Options: 'mnt', 'bn', 'ss'"
echo "  --enable-pairing-pbc     enable PBC lib for pairing module (DEFAULT)"
echo "  --enable-pairing-relic   enable RELIC lib for pairing module"
echo "  --enable-integer-openssl enable openssl for integer module"
echo "  --enable-integer-gmp     enable GMP lib for integer module (DEFAULT)"
echo "  --disable-benchmark      disable BENCHMARK base module (DEFAULT is no)"
echo "  --disable-werror         disable compilation abort on warning"
echo "  --enable-cocoa           enable COCOA (Mac OS X only)"
echo "  --enable-docs            enable documentation build"
echo "  --disable-docs           disable documentation build"
echo "  --sphinx-build=PATH      overide the default sphinx-build which is \`which sphinx-build\`"       
echo ""
echo "NOTE: The object files are built at the place where configure is launched"
exit 1
fi

# Python version handling logic. We prefer the argument path given by --python 
# If not specified, we check if python is python 3. 
# Baring that, we try python3, python3.8, python3.7, etc 

python3_found="no"
is_python_version(){
cat > $TMPC << EOF
import sys

if float(sys.version[:3]) >= 3.0:
    exit(0)
else:
   exit(-1)
EOF

if  [ -n "${1}"  ]; then
    $1 $TMPC
    result=$?
    if [ "$result" -eq "0" ] ; then 
        return  
    fi
fi
return 1
}

if [ -n "$python_path" ]; then 
        if (is_python_version $python_path); then
            python3_found="yes"
        else
            echo "$python_path is not python 3.x. This version of charm requires"
            echo "python 3.x. Please specify a valid python3 location with"
            echo "--python=/path/to/python3, leave off the command to have this script"
            echo "try finding it on its own, or install charm for python2.7"
            exit 1
        fi 
else
        for pyversion in python python3 python3.8 python3.7 python3.6 python3.5 python3.4 python3.3 python3.2 python3.1 
        do 
            if (is_python_version `which $pyversion`); then
                python3_found="yes"
                python_path=`which $pyversion`
                break
            fi
        done
        if test "$python3_found" = "no"; then 
            echo "No python 3 version found. This version of Charm requires python version 3.x. Specify python3 location with --python=/path/to/python3"
            echo "Otherwise, use the python 2.7+ version"
            exit 1
        fi
fi

if [ "$targetos" != "MINGW32" ] ; then
    py_config="$(which python3-config)"
    if ! test -e "$py_config"
    then
        echo "$py_config not found.  This version of Charm requires the python development environment (probably in python3-dev package)."
        exit 1
    fi
    PY_CFLAGS=`$py_config --cflags`
    PY_LDFLAGS=`$py_config --ldflags`
fi

# check that the C compiler works.
cat > $TMPC <<EOF
int main(void) {}
EOF

if compile_object ; then
  : C compiler works ok
else
    echo "ERROR: \"$cc\" either does not exist or does not work"
    exit 1
fi

# set flags here
gcc_flags="-Wold-style-declaration -Wold-style-definition -Wtype-limits"
gcc_flags="-Wformat-security -Wformat-y2k -Winit-self -Wignored-qualifiers $gcc_flags"
gcc_flags="-Wmissing-include-dirs -Wempty-body -Wnested-externs $gcc_flags"
gcc_flags="-fstack-protector-all -Wendif-labels $gcc_flags"
cat > $TMPC << EOF
int main(void) { return 0; }
EOF
for flag in $gcc_flags; do
    if compile_prog "-Werror $CHARM_CFLAGS" "-Werror $flag" ; then
	CHARM_CFLAGS="$CHARM_CFLAGS $flag"
    fi
done

if test -z "$target_list" ; then
    target_list="$default_target_list"
else
    target_list=`echo "$target_list" | sed -e 's/,/ /g'`
fi

feature_not_found() {
  feature=$1

  echo "ERROR"
  echo "ERROR: User requested feature $feature"
  echo "ERROR: configure was not able to find it"
  echo "ERROR"
  exit 1;
}

if test -z "$cross_prefix" ; then

# ---
# big/little endian test
cat > $TMPC << EOF
#include <inttypes.h>
int main(int argc, char ** argv){
        volatile uint32_t i=0x01234567;
        return (*((uint8_t*)(&i))) == 0x67;
}
EOF

if compile_prog "" "" ; then
$TMPE && bigendian="yes"
else
echo big/little test failed
fi

else

# if cross compiling, cannot launch a program, so make a static guess
case "$cpu" in
  armv4b|hppa|m68k|mips|mips64|ppc|ppc64|s390|s390x|sparc|sparc64)
    bigendian=yes
  ;;
esac

fi

# host long bits test, actually a pointer size test
cat > $TMPC << EOF
int sizeof_pointer_is_8[sizeof(void *) == 8 ? 1 : -1];
EOF
if compile_object; then
hostlongbits=64
else
hostlongbits=32
fi

##########################################
# zlib check

#cat > $TMPC << EOF
##include <zlib.h>
#int main(void) { zlibVersion(); return 0; }
#EOF
#if compile_prog "" "-lz" ; then
#    :
#else
#    echo
#    echo "Error: zlib check failed"
#    echo "Make sure to have the zlib libs and headers installed."
#    echo
#    exit 1
#fi

##########################################
# pkg-config probe

#if ! has $pkg_config; then
#  echo warning: proceeding without "$pkg_config" >&2
#  pkg_config=/bin/false
#fi

##########################################
# check if the compiler defines offsetof

need_offsetof=yes
cat > $TMPC << EOF
#include <stddef.h>
int main(void) { struct s { int f; }; return offsetof(struct s, f); }
EOF
if compile_prog "" "" ; then
    need_offsetof=no
fi

##########################################
# check if the compiler understands attribute warn_unused_result
#
# This could be smarter, but gcc -Werror does not error out even when warning
# about attribute warn_unused_result

gcc_attribute_warn_unused_result=no
cat > $TMPC << EOF
#if defined(__GNUC__) && (__GNUC__ < 4) && defined(__GNUC_MINOR__) && (__GNUC__ < 4)
#error gcc 3.3 or older
#endif
int main(void) { return 0;}
EOF
if compile_prog "" ""; then
    gcc_attribute_warn_unused_result=yes
fi


##########################################
# checks for -lm, -lpbc, -lgmp, -lcrypto libraries
libm_found="no"
if check_library "-lm" $TMPC == 0 ; then
   #echo "libm found!"
   libm_found="yes"
fi

# check for -lgmp
libgmp_found="no"
if check_library "-lgmp" $TMPC == 0 ; then
   #echo "libgmp found!"
   libgmp_found="yes"
fi

# check for -lpbc
libpbc_found="no"
if check_library "-lpbc" $TMPC == 0 ; then
   #echo "libpbc found!"
   libpbc_found="yes"
fi

# check for -lcrypto
libcrypto_found="no"
if check_library "-lcrypto" $TMPC == 0 ; then
   #echo "libcrypto found!"
   libcrypto_found="yes"
fi
##########################################


##########################################
# End of CC checks
# After here, no more $cc or $ld runs

if test "$debug" = "no" ; then
  CFLAGS="-O2 $CFLAGS"
fi

# Consult white-list to determine whether to enable werror
# by default.  Only enable by default for git builds
z_version=`cut -f3 -d. "$source_path/VERSION"`

if test -z "$werror" ; then
    if test "$z_version" = "50" -a \
        "$linux" = "yes" ; then
        werror="yes"
    else
        werror="no"
    fi
fi

if test "$werror" = "yes" ; then
    CHARM_CFLAGS="-Werror $CHARM_CFLAGS"
fi

confdir=$sysconfdir$confsuffix

echo "Install prefix    $prefix"
echo "data directory    `eval echo $datadir`"
echo "binary directory  `eval echo $bindir`"
echo "library directory `eval echo $libdir`"
echo "config directory  `eval echo $sysconfdir`"
echo "Source path       $source_path"
#echo "C compiler        $CC"
#echo "Host C compiler   $HOST_CC"
echo "CFLAGS            $CFLAGS"
echo "CHARM_CFLAGS       $CHARM_CFLAGS"
echo "LDFLAGS           $LDFLAGS"
echo "make              $make"
echo "python            $python_path"
echo "python-config     $py_config"
echo "build_ext options build_ext $PYTHONBUILDEXT"
echo "install           $install"
echo "host CPU          $cpu"
echo "wget              $wget"
echo "gprof enabled     $gprof"
echo "profiler          $profiler"
echo "static build      $static"
echo "-Werror enabled   $werror"
echo "integer module    $integer_module"
echo "ecc module        $ecc_module"
echo "pairing module    $pairing_module"
echo "disable benchmark $disable_benchmark"
echo "libm found        $libm_found"
echo "libgmp found      $libgmp_found"
echo "libpbc found      $libpbc_found"
echo "libcrypto found   $libcrypto_found"
#if test "$darwin" = "yes" ; then
#    echo "Cocoa support     $cocoa"
#fi
echo "Documentation     $docs"
if test "$docs" = "yes" ; then
    echo "sphinx path       $sphinx_build"
fi

[ ! -z "$uname_release" ] && \
echo "uname -r          $uname_release"

config_mk="config.mk"

echo "# Automatically generated by configure - do not modify" > $config_mk
printf "# Configured with:" >> $config_mk
printf " '%s'" "$0" "$@" >> $config_mk
echo >> $config_mk

echo all: >> $config_mk
echo "prefix=$prefix" >> $config_mk
echo "bindir=$bindir" >> $config_mk
echo "libdir=$libdir" >> $config_mk
echo "mandir=$mandir" >> $config_mk
echo "datadir=$datadir" >> $config_mk
echo "sysconfdir=$sysconfdir" >> $config_mk
echo "docdir=$docdir" >> $config_mk
echo "confdir=$confdir" >> $config_mk

case "$cpu" in
  i386|x86_64|alpha|cris|hppa|ia64|lm32|m68k|microblaze|mips|mips64|ppc|ppc64|s390|s390x|sparc|sparc64|unicore32)
    ARCH=$cpu
  ;;
  armv4b|armv4l|armv6l|armv7l)
    ARCH=arm
  ;;
esac
echo "ARCH=$ARCH" >> $config_mk
if test "$debug" = "yes" ; then
  echo "CONFIG_DEBUG_EXEC=y" >> $config_mk
fi

if test "$darwin" = "yes" ; then
  echo "CONFIG_DARWIN=y" >> $config_mk
fi

if test "$static" = "yes" ; then
  echo "CONFIG_STATIC=y" >> $config_mk
fi
if test $profiler = "yes" ; then
  echo "CONFIG_PROFILER=y" >> $config_mk
fi

CHARM_version=`head "$source_path/VERSION"`
echo "VERSION=$CHARM_version" >>$config_mk
echo "PKGVERSION=$pkgversion" >>$config_mk
echo "SRC_PATH=$source_path" >> $config_mk
echo "TARGET_DIRS=$target_list" >> $config_mk
if [ "$docs" = "yes" ] ; then
  echo "BUILD_DOCS=yes" >> $config_mk
fi

echo "CONFIG_UNAME_RELEASE=\"$uname_release\"" >> $config_mk

echo "TOOLS=$tools" >> $config_mk
echo "MAKE=$make" >> $config_mk
echo "INSTALL=$install" >> $config_mk
echo "INSTALL_DIR=$install -d -m0755 -p" >> $config_mk
echo "INSTALL_DATA=$install -m0644 -p" >> $config_mk
echo "INSTALL_PROG=$install -m0755 -p" >> $config_mk

if test "$darwin" = "yes" ; then
   mac_ver=`sw_vers | grep "ProductVersion:" | cut -d. -f2`
   if test "$mac_ver" = "7"; then 
      echo "CC=clang" >> $config_mk
      echo "CPP=clang++" >> $config_mk
      echo "CXX=clang++" >> $config_mk 
      echo "HOST_CC=clang" >> $config_mk
   else
      echo "CC=$cc" >> $config_mk
      echo "HOST_CC=$host_cc" >> $config_mk
   fi
else
echo "CC=gcc" >> $config_mk
echo "CPP=gcc -E" >> $config_mk
echo "HOST_CC=gcc" >> $config_mk
fi
echo "AR=$ar" >> $config_mk
echo "LD=$ld" >> $config_mk
echo "LIBTOOL=$libtool" >> $config_mk
echo "CFLAGS=$CFLAGS" >> $config_mk
echo "CHARM_CFLAGS=$CHARM_CFLAGS" >> $config_mk
echo "CHARM_INCLUDES=$CHARM_INCLUDES" >> $config_mk

echo "HELPER_CFLAGS=$helper_cflags" >> $config_mk
echo "LDFLAGS=$LDFLAGS" >> $config_mk
echo "CPPFLAGS=$CPPFLAGS" >> $config_mk
echo "ARLIBS_BEGIN=$arlibs_begin" >> $config_mk
echo "ARLIBS_END=$arlibs_end" >> $config_mk
echo "LIBS+=$LIBS" >> $config_mk
echo "LIBS_TOOLS+=$libs_tools" >> $config_mk

echo "PY_CFLAGS=$PY_CFLAGS" >> $config_mk
echo "PY_LDFLAGS=$PY_LDFLAGS" >> $config_mk

# generate list of library paths for linker script
cflags=""
includes=""
ldflags=""

if test "$gprof" = "yes" ; then
  echo "TARGET_GPROF=yes" >> $config_target_mak
  if test "$target_linux_user" = "yes" ; then
    cflags="-p $cflags"
    ldflags="-p $ldflags"
  fi
  if test "$target_softmmu" = "yes" ; then
    ldflags="-p $ldflags"
    echo "GPROF_CFLAGS=-p" >> $config_target_mak
  fi
fi

if test "$docs" = "yes" ; then
  if test "$sphinx_build" = ""; then 
    echo "ERROR: sphinx-build not found"
    exit -1 
  fi
fi
if test "$python3_found" = "no" ; then
   echo "ERROR: python 3 not found."
   exit -1
else
   echo "PYTHON=$python_path" >> $config_mk
fi

# write the CHARM specific options to the config file
echo "INT_MOD=$integer_module" >> $config_mk
echo "ECC_MOD=$ecc_module" >> $config_mk
echo "PAIR_MOD=$pairing_module" >> $config_mk

if test "$pairing_pbc" = "yes" ; then
    echo "USE_PBC=$pairing_pbc" >> $config_mk
    echo "USE_GMP=$pairing_pbc" >> $config_mk
    echo "USE_MIRACL=no" >> $config_mk
    echo "USE_RELIC=no" >> $config_mk
elif test "$pairing_miracl" = "yes" ; then
    echo "USE_MIRACL=$pairing_miracl" >> $config_mk
    echo "USE_PBC=no" >> $config_mk
    echo "USE_RELIC=no" >> $config_mk
elif test "$pairing_relic" = "yes" ; then
    echo "USE_RELIC=$pairing_relic" >> $config_mk
    echo "USE_PBC=no" >> $config_mk
    echo "USE_MIRACL=no" >> $config_mk
fi

if test "$pairing_miracl" = "yes" ; then
    if test "$pairing_arg" = "mnt" ; then
        echo "MIRACL_MNT=yes" >> $config_mk
        echo "MIRACL_BN=no" >> $config_mk
        echo "MIRACL_SS=no" >> $config_mk
    elif test "$pairing_arg" = "bn" ; then
        echo "MIRACL_MNT=no" >> $config_mk
        echo "MIRACL_BN=yes" >> $config_mk
        echo "MIRACL_SS=no" >> $config_mk
    elif test "$pairing_arg" = "ss" ; then
        echo "MIRACL_MNT=no" >> $config_mk
        echo "MIRACL_BN=no" >> $config_mk
        echo "MIRACL_SS=yes" >> $config_mk
    fi
fi

if test "$disable_benchmark" = "yes" ; then
    echo "DISABLE_BENCHMARK=yes" >> $config_mk
else
    echo "DISABLE_BENCHMARK=no" >> $config_mk
fi

if test "$wget" = "" ; then
    if [ "$targetos" = "MINGW32" ] ; then
        printf "wget not found!\n\n.Will now run Internet Explorer to download wget for windows.\n\n Please be sure to add the GNU32 bin directory to your path! Right-click Computer, Properties, Advanced System Settings, Advanced, Environment Variables, Path."
        /c/Program\ Files/Internet\ Explorer/iexplore.exe http://downloads.sourceforge.net/gnuwin32/wget-1.11.4-1-setup.exe
        rm $config_mk
        exit -1
    else
        echo "wget not found. Please install first, its required if installing dependencies."
        rm $config_mk
        exit -1
    fi
fi

if [ "$targetos" = "MINGW32" ] ; then
	echo "PYTHONFLAGS=--compile=mingw32" >> $config_mk
	echo "OSFLAGS=--disable-static --enable-shared $OSFLAGS" >> $config_mk
fi

# For python installers on OS X.
test_path=`echo $python_path | awk 'BEGIN {FS="."}{print $1}'`
if [ "$test_path" = "/Library/Frameworks/Python" ] ; then
    PYTHONBUILDEXT="-L/usr/local/lib -I/usr/local/include $PYTHONBUILDEXT"
fi

if [ "$PYTHONBUILDEXT" != "" ] ; then
    echo "PYTHONBUILDEXT=build_ext $PYTHONBUILDEXT" >> $config_mk
fi

if test "$libm_found" = "no" ; then
   echo "ERROR: libm not found. Please install first, then re-run configure."
   rm $config_mk
   exit -1
fi 

if [ "$targetos" = "MINGW32" ] ; then
	# Windows allowing spaces in directories is a no-no.
	echo "wget=\"$wget\"" >> $config_mk
else
	echo "wget=$wget" >> $config_mk
fi
echo "HAVE_LIBM=$libm_found" >> $config_mk
echo "HAVE_LIBGMP=$libgmp_found" >> $config_mk
echo "HAVE_LIBPBC=$libpbc_found" >> $config_mk
echo "HAVE_LIBCRYPTO=$libcrypto_found" >> $config_mk
echo "PYPARSING=$pyparse_found" >> $config_mk
if test "$docs" = "yes" ; then
    echo "SPHINX=$sphinx_build" >> $config_mk
fi

# needed for keeping track of crypto libs installed
cp config.dist.py charm/config.py
exit 0
