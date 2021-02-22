#!/bin/bash

# Checking your operating system with enviroment uname
unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)     machine=Linux;;
    Darwin*)    machine=Mac;;
    CYGWIN*)    machine=Windows;;
    MINGW*)     machine=Windows;;
    MSYS*)      machine=Windows;;
    *)          machine="UNKNOWN:${unameOut}"
esac

# Check python condition
python3x="py -3"
if [[ $machine != "Windows" ]]; then
    if command -v python3 &>/dev/null; then
        python3x="python3"
    elif command -v python &>/dev/null; then
        python3x="python"
    else
    	read -p $'Python is NOT installed.\nVisit https://www.python.org/downloads/ for more info.'
    	exit 1;
    fi
fi

# Check aria2c condition
if ! [[ -x "$(command -v aria2c)" ]]; then
	read -p $'aria2c is NOT installed.\nVisit https://github.com/aria2/aria2/releases/latest for more info.'
	exit 1;
fi

echo "Search for your anime:"
read anime
rm $PWD/scraper/__temp__/*.txt # clean up
$python3x $PWD/scraper/twist.py $anime

# Return total lines in all text file combine
total=$(cat $PWD/scraper/__temp__/*.txt | wc -l | xargs)
if [[ "$total" -eq "0" ]]; then
	read -p "Search your anime first!"
	exit 1;
elif [[ "$total" -eq "1" ]]; then
	echo "Only 1 episode."
else
	echo "Total $total episodes."
fi
echo

# Space delimiter
IFS=' '
for file in $PWD/scraper/__temp__/*.txt; do
	while read -r _ep _url; do
		name=$(echo $file | cut -d'/' -f7 | cut -d'.' -f1) # Get the 7th & 1st element of the delimiter array
		url=${_url%$'\r'} # Strip the \r from each line
		echo "Downloading $name"
		aria2c "$url" \
			-o "$name Episode $_ep" \
			--dir "$PWD/scraper/$name" \
			--header="Referer: https://twist.moe/" \
			--header="User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"
	done < "$file"
done
echo
rm $PWD/scraper/__temp__/*.txt # Delete all text file