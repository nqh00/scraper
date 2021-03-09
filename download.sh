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
		exit 2;
	fi
elif [[ $machine == "Windows" ]]; then
	if ! [[ -x "$(command -v py -3)" ]]; then
		read -p $'Python 3.X is NOT installed.\nVisit https://www.python.org/downloads/ for more info.'
		exit 2;
	else
		python3x="py -3"
	fi
fi

# Check `aria2c` condition
if ! [[ -x "$(command -v aria2c)" ]]; then
	if [[ $machine == "Windows" ]]; then
		read -p $'aria2c is NOT installed.\nVisit https://github.com/aria2/aria2/releases/latest for more info.'
		exit 2;
	fi
	if [[ $machine == "Linux" ]]; then
		read -p "Try this command: sudo apt-get install aria2"
		exit 2;
	fi
fi

# Check `ffmpeg` condition
if ! [[ -x "$(command -v ffmpeg)" ]]; then
	if [[ $machine == "Windows" ]]; then
		read -p $'ffmpeg is NOT installed.\nVisit https://www.gyan.dev/ffmpeg/builds for more info.'
		exit 2;
	fi
	if [[ $machine == "Linux" ]]; then
		read -p "Try this command: sudo apt-get install ffmpeg"
		exit 2;
	fi
fi

# Set file path
promt_statement='Choose your movie type: '
directory="`dirname $0`"
if [[ $machine == "Linux" ]]; then
	feature_path="$directory/.temp/.feature"
	anime_path="$directory/.temp/.anime"
elif [[ $machine == "Windows" ]]; then
	feature_path="$directory\.temp\.feature"
	anime_path="$directory\.temp\.anime"
else
	read -p "Linux & Windows support only."
	exit 2;
fi

# Create necessary temporary directory
check_directory () {
	if [[ $machine == "Linux" ]]; then
		if [[ ! -d "$directory/.temp" ]]; then
			mkdir "$directory/.temp"
		fi
		if [[ ! -d  "$anime_path" ]]; then
			mkdir "$anime_path"
		fi
		if [[ ! -d  "$feature_path" ]]; then
			mkdir "$feature_path" 
		fi
	elif [[ $machine == "Windows" ]]; then
		if [[ ! -d "$directory\.temp" ]]; then
			mkdir "$directory\.temp"
			attrib +h "$directory\.temp"
		fi
		if [[ ! -d "$anime_path" ]]; then
			mkdir "$anime_path"
			attrib +h "$anime_path"
		fi
		if [[ ! -d "$feature_path" ]]; then
			mkdir "$feature_path"
			attrib +h "$feature_path"
		fi
	fi
}

# python execution
run_vikv_python () {
	clear
	echo "Search your feature movie:"
	read -e feature && [[ "$feature" != "" ]] || exit 1
	echo
	stty -echo # Disable input
	$python3x "$directory/vikv.py" "$feature"; feature_found=$(echo $?) # store sys.exit value to $found
	stty echo # Re-enable input
}

run_twist_python () {
	clear
	echo "Search for your anime:"
	read -e anime && [[ "$anime" != "" ]] || exit 1
	echo
	stty -echo # Disable input
	$python3x "$directory/twist.py" "$anime"; anime_found=$(echo $?) # store sys.exit() value to $found, found = 1 is no found, found = 2 is Server Error
	stty echo # Re-enable input
}

#Download URL with concurrent threading, always continue download
download_feature() {
	stty -echo # Disable input
	echo "Downloading $1"
	folder="$(head -n 2 $feature_path/$1.txt | tail -n 1 | cut -c 6-)" # Read file and get the folder path from line 2
	
	if [[ ! -f "$folder/$1.mp4" ]]; then
		aria2c -i "$feature_path/$1.txt" \
			--quiet \
			--file-allocation=none \
			--continue \
			--always-resume \
			--max-tries=3 \
			--max-concurrent-downloads=10
		clear
		merge_ts "$1" "$folder"
	fi
	stty echo # Re-enable input
}

# Download URL with headers, auto rety on error, always continue download, no pre-allocated disk size
download_anime() {
	stty -echo # Disable input
	IFS=' ' # Space delimiter
	while read -r _ep _url; do
		url=${_url%$'\r'} # Strip the `\r` from each line
		echo "Downloading $1 Episode $_ep"
		aria2c "$url" \
			-o "$1 Episode $_ep.mp4" \
			--dir "$directory/$1" \
			--header="Referer: https://twist.moe/" \
			--header="User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36" \
			--download-result=hide \
			--file-allocation=none \
			--continue \
			--always-resume \
			--max-tries=0
		clear
	done < "$anime_path/$1.txt"
	stty echo # Re-enable input
}

# Merge all ts file with ffmpeg
merge_ts () {
	ls -v "$2/"*.ts | xargs -d '\n' cat > "$2\\$1.ts"
	ffmpeg -y -i "$2\\$1.ts" -vcodec copy -acodec copy "$2\\$1.mp4"
	rm "$2/"*.ts
}

# Managing all transport stream file
controller_feature () {
	LIST=("Search for feature movie")
	for file in "$feature_path/"*.txt; do
		name=${file##*/} # Get the filename and its extension
		name=${name%.txt} # Strip the extention
		if [[ $name != "*" ]]; then # '*' means there is no txt file
			LIST+=("$name")
		fi
	done

	clear
	PS3='Choose your movie: '
	LIST+=("Exit")
	select _feature in "${LIST[@]}"; do
		for _choice in "${LIST[@]}"; do
			if [[ $_choice == $_feature ]]; then
				if [[ $_choice == "Exit" ]]; then
					break 2
				elif [[ $_choice == "Search for feature movie" ]]; then
					run_vikv_python
					if [[ $feature_found -eq "1" ]]; then
						read -p "Please try another keyword."
					elif [[ $feature_found -eq "2" ]]; then
						read -p "We will update this movie in the future."
					else
						read -p "Your movie library has been updated."
					fi
					break 2
				else
					download_feature "$_feature"
					read -p "Your movie has downloaded and saved in $folder."
					break 2
				fi
			fi
		done
	done
	clear
	PS3="$promt_statement"
}

# Managing all anime episode
controller_anime () {
	LIST=("Search for anime")
	for file in "$anime_path/"*.txt; do
		name=${file##*/} # Get the filename and its extension
		name=${name%.txt} # Strip the extention
		if [[ $name != "*" ]]; then # '*' means there is no txt file
			LIST+=("$name")
		fi
	done

	clear
	PS3='Choose your anime: '
	LIST+=("Exit")
	select _anime in "${LIST[@]}"; do
		for _choice in "${LIST[@]}"; do
			if [[ $_choice == $_anime ]]; then
				if [[ $_choice == "Exit" ]]; then
					break 3
				elif [[ $_choice == "Search for anime" ]]; then
					run_twist_python
					if [[ $anime_found -eq "1" ]]; then
						read -p "Please try another keyword."
					elif [[ $anime_found -eq "2" ]]; then
						read -p "Please try again later."
					else
						read -p "Your anime library has been updated."
					fi
					break 2
				else
					download_anime "$_anime"
					read -p "Your anime has downloaded and saved in \"$_anime\"."
					break 2
				fi
			fi
		done
	done
	clear
	PS3="$promt_statement"
}

# Using Prompt statement
PS3="$promt_statement"
movies=("Feature movie" "Anime" "Exit")
check_directory
select movie in "${movies[@]}"; do
	case $movie in
		"Feature movie")
			controller_feature
			;;
		"Anime")
			controller_anime
			;;
		"Exit")
			exit
			;;
		*)
			read -p "Option $REPLY is invalid."
			clear
	esac
done
