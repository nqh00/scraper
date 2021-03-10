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
if [[ "$machine" == "Linux" ]]; then
	if command -v python3 &>/dev/null; then
		python3x="python3"
	elif command -v python &>/dev/null; then
		python3x="python"
	else
		read -p "Python 3.X is NOT installed. Try to update your repositories."
		exit 2;
	fi
elif [[ "$machine" == "Windows" ]]; then
	if ! [[ -x "$(command -v py -3)" ]]; then
		read -p $'Python 3.X is NOT installed.\nVisit https://www.python.org/downloads/ for more info.'
		exit 2;
	else
		python3x="py -3"
	fi
fi

# Check `aria2c` condition
if ! [[ -x "$(command -v aria2c)" ]]; then
	if [[ "$machine" == "Windows" ]]; then
		read -p $'aria2c is NOT installed.\nVisit https://github.com/aria2/aria2/releases/latest for more info.'
		exit 2;
	fi
	if [[ "$machine" == "Linux" ]]; then
		read -p "Try this command: sudo apt-get install aria2"
		exit 2;
	fi
fi

# Check `ffmpeg` condition
if ! [[ -x "$(command -v ffmpeg)" ]]; then
	if [[ "$machine" == "Windows" ]]; then
		read -p $'ffmpeg is NOT installed.\nVisit https://www.gyan.dev/ffmpeg/builds for more info.'
		exit 2;
	fi
	if [[ "$machine" == "Linux" ]]; then
		read -p "Try this command: sudo apt-get install ffmpeg"
		exit 2;
	fi
fi

# Instantiate file path
promt_statement='Choose your movie type: '
directory="`dirname $0`"
feature_path="$directory/.temp/.feature"
anime_path="$directory/.temp/.anime"

# Create necessary temporary directory
check_directory () {
	if [[ "$machine" == "Linux" ]]; then
		if [[ ! -d "$directory/.temp" ]]; then
			mkdir "$directory/.temp"
		fi
		if [[ ! -d  "$anime_path" ]]; then
			mkdir "$anime_path"
		fi
		if [[ ! -d  "$feature_path" ]]; then
			mkdir "$feature_path" 
		fi
	elif [[ "$machine" == "Windows" ]]; then
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

# Python execution
run_vikv_python () {
	clear
	echo "Search your feature movie:"
	read -e feature
	clear
	stty -echo # Disable input
	if [[ ! -z "$feature" ]]; then # Null input check
		$python3x "$directory/vikv.py" "$feature"; feature_found=$(echo $?) # store sys.exit value to $found
	fi
	echo
	stty echo # Re-enable input
}

# Python execution
run_twist_python () {
	clear
	echo "Search for your anime:"
	read -e anime
	clear
	stty -echo # Disable input
	if [[ ! -z "$anime" ]]; then # Null input check
		$python3x "$directory/twist.py" "$anime"; anime_found=$(echo $?) # store sys.exit() value to $found, found = 1 is no found, found = 2 is Server Error
	fi
	echo
	stty echo # Re-enable input
}

# Download URL with concurrent threading, always continue download
download_feature () {
	aria2c -i "$feature_path/$1.txt" \
		--quiet \
		--file-allocation=none \
		--continue \
		--always-resume \
		--max-tries=3 \
		--max-concurrent-downloads=10
}

# Choose whether download or watch feature movie
watch_download_feature () {
	stty -echo # Disable input
	folder="$(head -n 3 $feature_path/$1.txt | tail -n 1 | cut -c 6-)" # Read file and get the folder path from line 2
	folder=${folder##*/} # Strip the path to get folder name
	if [[ "$2" == "watch" ]]; then
		m3u8="$(head -n 1 $feature_path/$1.txt | cut -c 3-)"
		clear
		ffplay -fs "$m3u8"
	elif [[ ! -f "$folder/$1.mp4" && "$2" == "down" ]]; then
		clear
		echo -e "Downloading $1\nPlease take your time."
		download_feature "$1"
		clear
		merge_ts "$1" "$folder"
		convert_vtt "$1" "$folder"
	else
		read -p "Your movie has downloaded and saved in \"$folder\"."
	fi
	stty echo # Re-enable input
}

# Merge all ts file with ffmpeg
merge_ts () {
	ls -v "$2/"*.ts | xargs -d '\n' cat > "$2/$1.ts"
	ffmpeg -y -i "$2/$1.ts" -vcodec copy -acodec copy "$2/$1.mp4"
	rm "$2/"*.ts "$2/"*.aria2
	clear
}

# Convert vtt to srt subtitle
convert_vtt () {
	for file in $(find "$feature_path" -name "$1*.vtt"); do
		name=${file##*/} # Get the filename and its extension
		name=${name%.vtt} # Strip the extention
		ffmpeg -y -i "$file" "$directory/$2/$name.srt"
		clear
	done
}

# Download URL with headers, auto rety on error, always continue download, no pre-allocated disk size
download_anime () {
	aria2c "$2" \
		-o "$1 Episode $3.mp4" \
		--dir "$directory/$1" \
		--header="Referer: https://twist.moe/" \
		--header="User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36" \
		--download-result=hide \
		--file-allocation=none \
		--continue \
		--always-resume \
		--max-tries=0
}

# Download all anime episodes
download_anime_all () {
	stty -echo # Disable input
	IFS=' ' # Space delimiter
	while read -r _ep _url; do
		url=${_url%$'\r'} # Strip the `\r` from each line
		echo "Downloading $1 Episode $_ep"
		download_anime "$1" "$url" "$_ep"
		clear
	done < "$anime_path/$1.txt"
	stty echo # Re-enable input
}

# Choose whether download or watch single anime episode
watch_download_anime () {
	stty -echo # Disable input
	IFS=' ' # Space delimiter
	while read -r _ep _url; do
		if [[ "$_ep" == "$2" ]]; then
			url=${_url%$'\r'} # Strip the `\r` from each line
		fi
	done < "$anime_path/$1.txt"
	if [[ "$3" == "watch" ]]; then
		ffplay -reconnect 1 -reconnect_at_eof 1 -reconnect_streamed 1 -reconnect_delay_max 2 -fs -i "$url" -headers "Referer: https://twist.moe/"
	elif [[ "$3" == "down" ]]; then
		echo "Downloading $1 Episode $2"
		download_anime "$1" "$url" "$2"
		clear
		read -p "Your episode has downloaded and saved in \"$1\"."
	fi
	stty echo # Re-enable input
}

# Choose whether watch or download feature movie
controller_feature_action () {
	clear
	PS3="Pick your choice: "
	actions=("Watch the movie" "Download the movie" "Download all subtitles" "Back to the menu")
	select action in "${actions[@]}"; do
		case $action in
			"Watch the movie")
				watch_download_feature "$1" "watch"
				break 2
				;;
			"Download the movie")
				watch_download_feature "$1" "down"
				break 2
				;;
			"Download all subtitles")
				convert_vtt "$1"
				break 2
				;;
			"Back to the menu")
				break 2
				;;
			*)
				read -p "Option $REPLY is invalid."
				clear
		esac
	done
}

# Choose whether watch or download anime episode
controller_anime_action () {
	clear
	PS3="Pick your choice: "
	actions=("Watch the episode" "Download the episode" "Back to the menu")
	select action in "${actions[@]}"; do
		case $action in
			"Watch the episode")
				watch_download_anime "$1" "$2" "watch"
				break 2
				;;
			"Download the episode")
				watch_download_anime "$1" "$2" "down"
				break 2
				;;
			"Back to the menu")
				break 2
				;;
			*)
				read -p "Option $REPLY is invalid."
				clear
		esac
	done
}

# Managing all feature movie
controller_feature () {
	list=("Search for feature movie")
	for file in "$feature_path/"*.txt; do
		name=${file##*/} # Get the filename and its extension
		name=${name%.txt} # Strip the extention
		if [[ "$name" != "*" ]]; then # '*' means there is no txt file
			list+=("$name")
		fi
	done

	clear
	PS3='Choose your movie: '
	list+=("Back to the menu")
	select _feature in "${list[@]}"; do
		for _choice in "${list[@]}"; do
			if [[ "$_choice" == "$_feature" ]]; then
				if [[ "$_choice" == "Back to the menu" ]]; then
					break 2
				elif [[ "$_choice" == "Search for feature movie" ]]; then
					run_vikv_python
					if [[ -z "$feature" ]]; then
						break 2
					elif [[ "$feature_found" -eq "1" ]]; then
						read -p "Please try another keyword."
					elif [[ "$feature_found" -eq "2" ]]; then
						read -p "We will update this movie in the future."
					else
						read -p "Your movie library has been updated."
					fi
					break 2
				else
					controller_feature_action "$_feature"
					break 2
				fi
			fi
		done
	done
	clear
	PS3="$promt_statement"
}

# Managing all anime episodes
controller_anime_episodes () {
	clear
	PS3="Choose your episode:"
	episodes=("All of episodes")
	while read -r __ep __url; do
		IFS=' ' # Space delimiter
		episodes+=("Episode $__ep")
	done < "$anime_path/$1.txt"
	episodes+=("Back to the menu")
	PS3="Choose your episode: "
	select _ep in "${episodes[@]}"; do
		for _choice in "${episodes[@]}"; do
			if [[ "$_choice" == "$_ep" ]]; then
				if [[ "$_choice" == "Back to the menu" ]]; then
					break 2
				elif [[ "$_choice" == "All of episodes" ]]; then
					download_anime_all "$1"
					read -p "Your anime has downloaded and saved in \"$1\"."
					break 2
				else
					controller_anime_action "$1" "$(echo $_choice | cut -d' ' -f2)"
					break 2
				fi
			fi
		done
	done
}

# Managing all anime
controller_anime () {
	list=("Search for anime")
	for file in "$anime_path/"*.txt; do
		name=${file##*/} # Get the filename and its extension
		name=${name%.txt} # Strip the extention
		if [[ "$name" != "*" ]]; then # '*' means there is no txt file
			list+=("$name")
		fi
	done

	clear
	PS3='Choose your anime: '
	list+=("Back to the menu")
	select _anime in "${list[@]}"; do
		for _choice in "${list[@]}"; do
			if [[ "$_choice" == "$_anime" ]]; then
				if [[ "$_choice" == "Back to the menu" ]]; then
					break 2
				elif [[ "$_choice" == "Search for anime" ]]; then
					run_twist_python
					if [[ -z "$anime" ]]; then
						break 2
					elif [[ "$anime_found" -eq "1" ]]; then
						read -p "Please try another keyword."
					elif [[ "$anime_found" -eq "2" ]]; then
						read -p "Please try again later."
					else
						read -p "Your anime library has been updated."
					fi
					break 2
				else
					controller_anime_episodes "$_anime"
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
			clear
			exit
			;;
		*)
			read -p "Option $REPLY is invalid."
			clear
	esac
done
