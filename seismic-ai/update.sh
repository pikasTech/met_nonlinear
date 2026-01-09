echo "updating met..."
cd lib/met && git commit -a 
cd -
cd lib/met && git pull
cd -
cd lib/met && git push
cd -
echo "updating this repo..."
echo $PWD
git add assets
git commit -a && git pull && git push
# press any key to exit
read -n 1 -s -r -p "[Press any key to continue]"
