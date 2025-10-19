if pgrep -af 'manage.py run_article_detail_collector > /dev/null
then
	echo "article detail collector running"
else
	echo "article detail collector not running"
	command="/home/admin/Works/mkay/onenlc/api-gateway/venv/bin/python /home/admin/Works/mkay/onenlc/api-gateway/manage.py run_article_detail_collector >> /usr/log/run_article_detail_collector.log 2>&1 &"
	echo $command
	eval $command
fi