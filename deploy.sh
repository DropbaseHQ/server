if [[ $1 == 'l' ]]
then
    $SERIVE_NAME = 'lsp'
else
    $SERIVE_NAME = 'server'
fi

docker build -t dropbase/$SERIVE_NAME -f Dockerfile-$SERIVE_NAME .
docker push dropbase/$SERIVE_NAME