#!/bin/sh

#自动创建文件列表
fileprefix=`ls *.cap*|sed s/\.cap[0-9]*$/.cap/|sort|uniq`

filelist=""
for f in $fileprefix
do
	len=`expr \( length "$f" \) + 1`
	filelist=$filelist`ls "$f"*|sort -k 1."$len"n`" "
done

head="SIP\/2\.0 [4-6]"
content1="^Warning:"
content2="^Reason:"

#tcpdump读取所有错误
errorfile=errors.txt
for f in $filelist
do
	#echo "$f"
	lasterrorfile=$errorfile
	errorfile=`echo $f|sed s/\.cap[0-9]*$/-errors.txt/`
	if [ $errorfile != $lasterrorfile ]
	then
		echo -n > $errorfile
	fi
	echo "checking $f" >>$errorfile
	#tcpdump -r "$f" -A udp | awk '/^..:..:../ {
	#	if (flag1 || segment ~ /'"${content1}"'/ || hasreason) {
	#		printf "%s", segment;
	#	}
	#	segment = "";
	#	hasreason = "";
	#	flag1 = 0;
	#}
	#/'"${head}"'/ {
	#	flag1 = 1;
	#}
	#/^Reason/ {
	#	hasreason=!/Normal call clearing/;
	#}
	#{
	#	segment = segment $0 "\n";
	#}' >> $errorfile
	tcpdump -r "$f" -A udp | grep -E "(SIP\/2\.0 [4-6]|^Warning|^Reason)" -B 14 -A 30 > "$f.temp"
	cat "$f.temp" | awk '{
		if ($0 ~ /^..:..:../) {
			if (isOxx || hasWarning || hasReason) {
				printf "%s", segment;
			}
			segment = "";
			isSip = 0;
			isOxx = 0;
			hasWarning = 0;
			hasReason = 0;
		} else {
			if (!isSip && $0 ~ /SIP\/2\.0/) {
				isSip = 1;
				isOxx = /SIP\/2\.0 [4-6]/;
				isRsp = /SIP\/2\.0 [1-6]/;
				isError = isRsp || /CANCEL/ || /BYE/;
			} else if (isError) {
				if ($0 ~ /^Warning/) {
					hasWarning = 1;
				} else if ($0 ~ /^Reason/) {
					hasReason=!/Normal call clearing/;
				}
			}
		}
		segment = segment $0 "\n";
	}
	END {
		if (isOxx || hasWarning || hasReason) {
			printf "%s", segment;
		}
	}' >> $errorfile
	rm "$f.temp"
done

#生成汇总表格
for f in $fileprefix
do
	filename=`echo $f|sed s/\.cap$//`
	errorfile="${filename}-errors.txt"
	sumfile="${filename}-errors-sum.txt"
	userfile="${filename}-errors-user.txt"
	sortfile="${filename}-errors-sort.txt"
	uniqfile="${filename}-errors-user-uniq.txt"
	echo -e "Time\tFrom\tTo\tMethod\tOxx\tWarning\tReason" > $sumfile
	awk '/^..:..:../ {
		if (Time != "") {
			printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\n", Time,From,To,Method,Oxx,Warning,Reason;
		}
		Time = $1;
		Oxx = "-";
		User = "-";
		Method = "-";
		Warning = "-";
		Reason = "-";
	}
	/SIP\/2\.0 [3-6]/ {
		Oxx=substr($0, index($0, "SIP/2.0 ")+8, 3);
	}
	/^From:/ {
		i=index($0, "sip:");
		str=substr($0, i+4);
		i=match(str, "[:;?@]");
		str=substr(str, 1, i-1);
		From=str
	}
	/^To:/ {
		i=index($0, "sip:");
		str=substr($0, i+4);
		i=index(str, "@");
		str=substr(str, 1, i-1);
		To=str
	}
	/^CSeq:/ {
		Method=substr($NF, 1, length($NF)-1)
	}
	/^Warning:/ {
		Warning=substr($0, 1, length($0)-1)
	}
	/^Reason:/ {
		Reason=substr($0, 1, length($0)-1)
	}
	END {
		if (Time != "") {
			printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\n", Time,From,To,Method,Oxx,Warning,Reason;
		}
	}' $errorfile >> "$sumfile"
	
	cat "$sumfile" | sort -k 3 >"$sortfile"
	
	awk '{
		user=$3;
		if (olduser!=user)
		{
			olduser=user;
			print $0;
		}
	}' $sortfile > "$userfile"
	cat $userfile | sort -k 4,9 | uniq -f 4 -c > "$uniqfile"
done
