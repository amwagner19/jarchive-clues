#!/bin/bash
set -e

ORIGINAL_MD5=$(md5 jarchive.db)
scrapy runspider jarchive/spider.py -L INFO
UPDATED_MD5=$(md5 jarchive.db)

if [[ "$ORIGINAL_MD5" == "$UPDATED_MD5" ]]; then
  echo -e "Database unchanged \n\ta) $ORIGINAL_MD5\n\tb) $UPDATED_MD5"
else
  echo -e "Database updated \n\ta) $ORIGINAL_MD5\n\tb)$UPDATED_MD5"
  # git add jarchive.db
  # git commit -m 'feat: db update $(date)'
  # git push
fi