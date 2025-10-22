if pgrep -af 'manage.py run_article_collector' > /dev/null
then
	echo "article collector running"
else
	echo "article collector not running"
	command="/home/admin/Works/mkay/onenlc/api-gateway/venv/bin/python /home/admin/Works/mkay/onenlc/api-gateway/manage.py run_article_collector >> /usr/log/run_article_collector.log 2>&1 &"
	echo $command
	eval $command
fi