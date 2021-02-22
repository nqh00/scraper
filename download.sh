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

# Check `python` condition
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

# Check `aria2c` condition
if ! [[ -x "$(command -v aria2c)" ]]; then
	read -p $'aria2c is NOT installed.\nVisit https://github.com/aria2/aria2/releases/latest for more info.'
	exit 1;
fi

# Create temporary directory and temporary text file
path="$(cd "$(dirname "$1")"; pwd -P)/$(basename "$1")"
if [ ! -d  $path/__temp__ ]; then
	mkdir $path/__temp__
	touch $path/__temp__/temp.txt
	attrib +h $path/__temp__
	attrib +h $path/__temp__/temp.txt
elif [[ ! -d $path/__temp__/temp.txt ]]; then
	touch $path/__temp__/temp.txt # this file for not raising `cat` exception: no file in directory
	attrib +h $path/__temp__/temp.txt
fi

# python execution
run_python() {
	echo "Search for your anime:"
	read anime && [[ "$anime" != "" ]] || exit 1
	echo
	$python3x "$path/twist.py" "$anime"
}

# Check downloading state
state_check() {
	read -p "Do you want to keep downloading [yes] or renew [no]: " confirm && [[ "$confirm" == [yY] \
																	 	|| "$confirm" == [yY][eE][sS] \
																	 	|| "$confirm" == [nN] \
																	 	|| "$confirm" == [nN][oO] ]] \
														|| exit 1 # Receive only 4 input yes, no, y, n case insensitive
}

# Download all available URL
download() {
	# Space delimiter
	IFS=' '
	for file in $path/__temp__/*.txt; do
		while read -r _ep _url; do
			name=$(echo $file | cut -d'/' -f7 | cut -d'.' -f1) # Get the 7th & 1st element of the delimiter array
			url=${_url%$'\r'} # Strip the `\r` from each line
			echo "Downloading $name"
			aria2c "$url" \
				-o "$name Episode $_ep" \
				--dir "$path/$name" \
				--header="Referer: https://twist.moe/" \
				--header="User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"
		done < "$file"
	done
	read -p "Press enter to continue."
}

# Return total lines in all text file combine
total=$(cat $path/__temp__/*.txt | wc -l | xargs)
if [[ "$total" -eq "0" ]]; then
	run_python
elif [[ "$total" -eq "1" ]]; then
	echo "There are only 1 URL in queue waiting for download."
	state_check
else
	echo "There are total $total episodes in queue waiting for download."
	state_check
fi
echo

if [[ "$confirm" == [yY] || "$confirm" == [yY][eE][sS] ]]; then
	download
elif [[ "$confirm" == [nN] || "$confirm" == [nN][oO] ]]; then
	rm $path/__temp__/*.txt # Clean up
	run_python
	echo
	new_total=$(cat $path/__temp__/*.txt | wc -l | xargs)
	if [[ "$new_total" -eq "1" ]]; then
		echo "There are only 1 URL in queue waiting for download."
		download
	else
		echo "There are total $new_total episodes in queue waiting for download."
		download
	fi
else
	read -p "Press enter to exit."
	exit 1;
fi
