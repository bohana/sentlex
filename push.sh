rm /halshare/python/hub/sentlex/dist/*.gz
python /halshare/python/hub/sentlex/setup.py sdist
ver=`cat setup.py |grep version|cut -d'=' -f2|sed s/\'//g|sed s/,//`
easy_install -v file:/halshare/python/hub/sentlex/dist/SentLex-$ver.tar.gz
