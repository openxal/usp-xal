cd $HOME/lib/openxal
git fetch origin master
git reset --hard origin/master
rm -rf build
ant all install doc
