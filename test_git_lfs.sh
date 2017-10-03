#!/bin/bash

URL_BASE='http://127.0.0.1:8000/'
curl -s "$URL_BASE" > /dev/null || { echo "ERROR: could not curl $URL_BASE. Make sure Django test server is running."; exit 1; }

function indent() { sed 's/^/    /'; }

set -e

echo "(Re)creating test dirs..."
rm -rf test_temp
mkdir test_temp
cd test_temp
mkdir lfs_storage_dir

echo "Creating bare repository..."
git init --bare bare_repo 2>&1 | indent
cd bare_repo
git lfs install 2>&1 | indent

echo "Cloning empty repo..."
cd ..
git clone bare_repo clone1 2>&1 | indent
cd clone1
date > test1.txt
echo "Configuring LFS..."
git config -f .lfsconfig lfs.url http://localhost:8000/info/lfs 2>&1 | indent
git lfs track '*.bin' | indent
git add .lfsconfig .gitattributes test1.txt 2>&1 | indent

echo "Commiting config & normal files..."
git commit -m "First commit" 2>&1 | indent
echo "Pushing..."
git push 2>&1 | indent

echo "Creating some test files..."
dd if=/dev/urandom bs=1024 count=1024 of=test1.bin 2>&1 | indent
dd if=/dev/zero bs=2048 count=102400 of=test2.bin 2>&1 | indent
echo "Commiting them..."
git add *.bin | indent
git commit -m "Add some bin files" 2>&1 | indent

echo "Commiting known binary content..."
echo "testcontent" > known.bin
git add known.bin 2>&1 | indent
git commit -m "Add known bin" 2>&1 | indent

echo "Pushing..."
git push 2>&1 | indent

echo "Making another clone..."
cd ..
git clone bare_repo clone2 2>&1 | indent
cd clone2

git lfs pull 2>&1 | indent

cd ..
cmp clone1/test1.bin clone2/test1.bin || { echo "Pulled files differ"; exit 1; }
cmp clone2/known.bin lfs_storage_dir/86/03/8603effde36c3c39e50c1ad0b4909ee48318ab760c85a7555bd821b026856bf7 || { echo "Clone and storage differ?"; exit 1; }

echo "Deleting file from storage..."
rm -r lfs_storage_dir/86
[ ! -e lfs_storage_dir/86/03/8603effde36c3c39e50c1ad0b4909ee48318ab760c85a7555bd821b026856bf7 ] || { echo 'Failed to delete file?'; exit 1; }

echo "Pushing it again..."
cd clone2
git lfs push origin master --all 2>&1 | indent
cd ..
cmp clone2/known.bin lfs_storage_dir/86/03/8603effde36c3c39e50c1ad0b4909ee48318ab760c85a7555bd821b026856bf7 || { echo "Clone and storage differ?"; exit 1; }

echo "Corrupting file from storage..."
echo "BAD" > lfs_storage_dir/86/03/8603effde36c3c39e50c1ad0b4909ee48318ab760c85a7555bd821b026856bf7

echo "Pushing it again..."
cd clone2
git lfs push origin master --all 2>&1 | indent
cd ..
cmp clone2/known.bin lfs_storage_dir/86/03/8603effde36c3c39e50c1ad0b4909ee48318ab760c85a7555bd821b026856bf7 || { echo "Clone and storage differ?"; exit 1; }

[ -z "$(ls lfs_storage_dir/tmp/)" ] || { echo "ERROR: temp dir not empty."; exit 1; }

echo ""
echo "Tests passed."
echo ""
