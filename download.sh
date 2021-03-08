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
if [[ $machine == "Linux" ]]; then
	if command -v python3 &>/dev/null; then
		python3x="python3"
	elif command -v python &>/dev/null; then
		python3x="python"
	else
		read -p "Python 3.X is NOT installed. Try to update your repositories."
		exit 1;
	fi
elif [[ $machine == "Windows" ]]; then
	if ! [[ -x "$(command -v py -3)" ]]; then
		read -p $'Python 3.X is NOT installed.\nVisit https://www.python.org/downloads/ for more info.'
		exit 1;
	else
		python3x="py -3"
	fi
fi

# Check `aria2c` condition
if ! [[ -x "$(command -v aria2c)" ]]; then
	if [[ $machine == "Windows" ]]; then
		read -p $'aria2c is NOT installed.\nVisit https://github.com/aria2/aria2/releases/latest for more info.'
		exit 1;
	fi
	if [[ $machine == "Linux" ]]; then
		read -p "Try this command: sudo apt-get install ffmpeg"
		exit 1;
	fi
fi

# Check `ffmpeg` condition
if ! [[ -x "$(command -v ffmpeg)" ]]; then
	if [[ $machine == "Windows" ]]; then
		read -p $'ffmpeg is NOT installed.\nVisit https://www.gyan.dev/ffmpeg/builds for more info.'
		exit 1;
	fi
	if [[ $machine == "Linux" ]]; then
		read -p "Try this command: sudo apt-get install aria2"
		exit 1;
	fi
fi

# Set file path
directory="`dirname $0`"
if [[ $machine == "Linux" ]]; then
	path="$directory/.temp/.anime"
elif [[ $machine == "Windows" ]]; then
	path="$directory\.temp\.anime"
else
	read -p "Linux & Windows support only."
	exit 1;
fi

# Create temporary directory and temporary text file
check_directory () {
	if [[ $machine == "Linux" ]]; then
		if [[ ! -d "$directory/.temp" ]]; then
			mkdir "$directory/.temp"
		fi
		if [[ ! -d  "$path" ]]; then
			mkdir "$path"
		fi
		if [[ ! -d  "$path/.txt" ]]; then
			touch "$path/.txt" # this file is for not raising `cat` exception: no file directory 
		fi
	elif [[ $machine == "Windows" ]]; then
		if [[ ! -d "$directory\.temp" ]]; then
			mkdir "$directory\.temp"
			attrib +h "$directory\.temp"
		fi
		if [ ! -d "$path" ]; then
			mkdir "$path"
			attrib +h "$path"
		fi
		if [[ ! -d "$path\temp.txt" ]]; then
			touch "$path\temp.txt" # this file is for not raising `cat` exception: no file in directory
			attrib +h "$path\temp.txt"
		fi
	fi
}

# Check total url in all text file
check_total_url () {
	if [[ "$1" -eq "0" ]]; then
		run_python
		if [[ "$found" -eq "1" ]]; then
			echo
			read -p "Press enter to exit and try another keyword."
			exit 1;
		fi
		confirm="yes"
	elif [[ "$1" -eq "1" ]]; then
		echo "There are only 1 URL in queue waiting for download."
		check_state
	else
		echo "There are total $1 episodes in queue waiting for download."
		check_state
	fi
}

# Check downloading state
check_state () {
	read -p "Do you want to keep downloading [yes] or renew [no]: " confirm && [[ "$confirm" == [yY] \
																		|| "$confirm" == [yY][eE][sS] \
																		|| "$confirm" == [nN] \
																		|| "$confirm" == [nN][oO] ]] \
														|| exit 1 # Receive only 4 input yes, no, y, n case insensitive
}

# python execution
run_python () {
	clear
	echo "Search for your anime:"
	read -e anime && [[ "$anime" != "" ]] || exit 1
	echo
	stty -echo # Disable input
	$python3x "$directory/twist.py" "$anime"; found=$(echo $?) # store sys.exit() value to $found, found = 1 is no found
	stty echo # Re-enable input
	echo
}

# Download all available URL
download () {
	# Space delimiter
	IFS=' '
	stty -echo
	for file in "$path/"*.txt; do
		while read -r _ep _url; do
			name=${file##*/} # Get the filename and its extension
			name=${name%.txt} # Remove the extention
			url=${_url%$'\r'} # Strip the `\r` from each line
			echo "Downloading $name Episode $_ep"
			aria2c "$url" \
				-o "$name Episode $_ep.mp4" \
				--dir "$directory/$name" \
				--header="Referer: https://twist.moe/" \
				--header="User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36" \
				--download-result=hide \
				--file-allocation=none \
				--continue \
				--always-resume \
				--max-tries=0 \
				--max-concurrent-downloads=10
			clear
		done < "$file"
	done
	stty echo
	read -p "Download has finished, press enter to exit."
	rm "$path/"*.txt # Clean up
	exit 1;
}

check_directory

check_total_url "$(cat "$path/"*.txt | wc -l | xargs)"

if [[ "$confirm" == [yY] || "$confirm" == [yY][eE][sS] ]]; then
	download
else
	rm "$path/"*.txt # Clean up
	check_directory
	check_total_url "$(cat "$path/"*.txt | wc -l | xargs)"
	download
fi