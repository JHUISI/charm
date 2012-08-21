#!/bin/sh

#
# The following script will build a DMG for OS X 10.5+ installations.
# To achieve this, a charmDMG directory will be created, and the
# following will be copied there:
#
#   1) ./build/Charm Crypto.mpkg -> ./charmDMG/Charm Crypto.mpkg
#   2) ../../schemes/            -> ./charmDMG/charm-usr/schemes
#   3) ../../tests/              -> ./charmDMG/charm-usr/tests
#


# Declare some useful variables.
NAME="Charm Crypto"
VERSION=`cat ../../VERSION`
VOLName="${NAME} ${VERSION}"
TMPName="charm-temp.dmg"
SRC="./charmDMG/"
DMGName="Charm Crypto"
APPDIR="/Applications/"

# Obviously if there is no mpkg, than don't build!
test -d "./build/" || {
    echo "Cannot find build directory, please use White Box Packages.app to build the Charm Crypto.pkgproj."

    exit 1;
}

# Maybe there is a better way to do this, for now just ask.
echo "Please type the path of the top level directory of Charm, python 2.x build, e.g. /Users/you/charm-2.7/charm:"
read CHARM27
echo "Please type the path of the top level directory of Charm, python 3.x build, surrounding input in quotes:"
read CHARM32


mkdir -p charmDMG/charm-usr2.7 charmDMG/charm-usr3.2 charmDMG/.background charmDMG/charm-usr2.7/adapters charmDMG/charm-usr3.2/adapters

cp -R "./build/Charm Crypto.mpkg" ./charmDMG/"Charm Crypto.mpkg"


cp -R ${CHARM27}/schemes/ ./charmDMG/charm-usr2.7/schemes
cp -R ${CHARM27}/adapters/ ./charmDMG/charm-usr2.7/adapters
cp -R ${CHARM27}/test/ ./charmDMG/charm-usr2.7/test

cp -R ${CHARM32}/schemes/ ./charmDMG/charm-usr3.2/schemes
cp -R ${CHARM32}/adapters/ ./charmDMG/charm-usr3.2/adapters
cp -R ${CHARM32}/test/ ./charmDMG/charm-usr3.2/test

cp ./packages-src/README-OSX.rtf ./charmDMG/
cp ./packages-src/charm-dmg-background.png ./charmDMG/.background/charm-dmg-background.png

echo "Make nice folder icons. Press enter when you're done." 
read haltomodifyfolder

# Create the image.
echo "Creating the Charm Crypto disk image."
hdiutil create -fs HFS+ -volname "${VOLName}" -srcfolder \
    "${SRC}" -fsargs "-c c=64,a=16,e=16" -format UDRW -size \
    6m "${TMPName}"

# Mount the image.
echo "Mounting the Charm Crypto disk image."
device=$(hdiutil attach -readwrite -noverify -noautoopen \
    "${TMPName}" | egrep '^/dev/' | sed 1q | awk '{print $1}')

# AppleScript automated settings.
# Idea Attribution: 
# http://stackoverflow.com/questions/96882/how-do-i-create-a-nice-looking-dmg-for-mac-os-x-using-command-line-tools
echo '
tell application "Finder"
tell disk "'${VOLName}'"
open
set current view of container window to icon view
set toolbar visible of container window to false
set statusbar visible of container window to false
set the bounds of container window to {250, 100, 685, 430}
set theViewOptions to the icon view options of container window
set arrangement of theViewOptions to not arranged
set icon size of theViewOptions to 82
set background picture of theViewOptions to file ".background:'charm-dmg-background.png'"
make new alias file at container window to POSIX file "'${APPDIR}'" with properties {name:"Applications"}
set position of item "'Charm  Crypto.mpkg'" of container window to {100, 100}
set position of item "Applications" of container window to {685, 120}
set position of item "'charm-usr2.7'" of container window to {50,25}
set position of item "'charm-usr3.2'" of container window to {50,25}
set position of item "'README-OSX.rtf'" of container window to {385,120}
update without registering applications
delay 5
close
open
end tell
end tell
' | osascript

echo "For now, manually adjust the icons where they should be. Press enter when you're done." 
read haltomodify

echo "If you receive an error concerning the inability to unmount, you can optionally finish the process \
by accessing Disk Utility, selecting the charm-temp.dmg and selecting Images->Convert with compression."

# Finalize permissions.
echo "Finalizing permissions."
sudo chmod -Rf go-w "/Volumes/${VOLName}"
sync

# Unmount the image.
echo "Unmounting the Charm Crypto disk image."
hdiutil detach ${device}

# Compress the image.
echo "Compressing the Charm Crypto disk image."
hdiutil convert "${TMPName}" -format UDZO -imagekey zlib-level=9 -o "${DMGName}"

rm -f "${TMPName}"

exit 0

