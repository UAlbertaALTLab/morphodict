# expected to be called from Pipfile under project root directory

echo "Which version of crkeng.xml did you use (200208/200218/200226 etc.)?"
read -r version_digits

rsync --progress CreeDictionary/db.sqlite3 $SAPIR_USER@sapir.artsrn.ualberta.ca:/opt/cree-intelligent-dictionary/CreeDictionary/db.sqlite3

ssh $SAPIR_USER@sapir.artsrn.ualberta.ca "echo $version_digits >> /opt/cree-intelligent-dictionary/CreeDictionary/res/prod_crkeng_version.txt"
