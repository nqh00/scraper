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
		read -s -p "Python 3.X is NOT installed. Try to update your repositories."
		exit 2;
	fi
elif [[ "$machine" == "Windows" ]]; then
	if ! [[ -x "$(command -v py -3)" ]]; then
		read -s -p $'Python 3.X is NOT installed.\nVisit https://www.python.org/downloads/ for more info.'
		exit 2;
	else
		python3x="py -3"
	fi
fi

# Check `aria2c` condition
if ! [[ -x "$(command -v aria2c)" ]]; then
	if [[ "$machine" == "Windows" ]]; then
		read -s -p $'aria2c is NOT installed.\nVisit https://github.com/aria2/aria2/releases/latest for more info.'
		exit 2;
	elif [[ "$machine" == "Linux" ]]; then
		read -s -p "Try this command: sudo apt-get install aria2"
		exit 2;
	fi
fi

# Check `ffmpeg` condition
if ! [[ -x "$(command -v ffplay)" ]]; then
	if [[ "$machine" == "Windows" ]]; then
		read -s -p $'ffmpeg is NOT installed.\nVisit https://www.gyan.dev/ffmpeg/builds for more info.'
		exit 2;
	elif [[ "$machine" == "Linux" ]]; then
		read -s -p "Try this command: sudo apt-get install ffmpeg"
		exit 2;
	fi
fi

# Instantiate file path
directory="`dirname $0`"
feature_path="$directory/.temp/.feature"
anime_path="$directory/.temp/.anime"
series_path="$directory/.temp/.series"

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
		if [[ ! -d  "$series_path" ]]; then
			mkdir "$series_path"
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
		if [[ ! -d "$series_path" ]]; then
			mkdir "$series_path"
			attrib +h "$series_path"
		fi
	fi
}

# Python execution
run_vikv_python () {
	clear
	echo "Search your feature movie:"
	read -e feature
	clear
	if [[ ! -z "$feature" ]]; then # Null input check
		stty -echo # Disable input
		$python3x "$directory/vikv.py" "$feature"; feature_found=$(echo $?) # store sys.exit() value to $found, found = 1 is no found, found = 2 is no movie
		if [[ "$feature_found" -eq "1" ]]; then
			read -s -p "Please try another keyword."
		elif [[ "$feature_found" -eq "2" ]]; then
			read -s -p "We will update this movie in the future."
		else
			read -s -p "Your movie library has been updated."
		fi
		stty echo # Re-enable input
	else
		read -s -p $'No keywords detected.\nPress something to search will you?'
	fi
	clear
}

# Python execution
run_twist_python () {
	clear
	echo "Search for your anime:"
	read -e anime
	clear
	if [[ ! -z "$anime" ]]; then # Null input check
		stty -echo # Disable input
		$python3x "$directory/twist.py" "$anime"; anime_found=$(echo $?) # store sys.exit() value to $found, found = 1 is no found, found = 2 is Server Error
		if [[ "$anime_found" -eq "1" ]]; then
			read -s -p "Please try another keyword."
		elif [[ "$anime_found" -eq "2" ]]; then
			read -s -p "Please try again later."
		else
			read -s -p "Your anime library has been updated."
		fi
		stty echo # Re-enable input
	else
		read -s -p $'No keywords detected.\nPress something to search will you?'
	fi
	clear
}

# Python execution
run_drama_python () {
	clear
	echo "Search for your TV series:"
	read -e series
	clear
	if [[ ! -z "$series" ]]; then
		stty -echo # Disable input
		$python3x "$directory/dramacool.py" "$series"; series_found=$(echo $?) # store sys.exit() value to $found, found = 1 is no found
		if [[ "$series_found" -eq "1" ]]; then
			read -p "Please try another keyword."
		else
			read -p "Your TV series library has been updated."
		fi
		stty echo # Re-enable input
	else
		read -p $'No keywords detected.\nPress something to search will you?'
	fi
	clear
}

# Download URL with concurrent threading, always continue download
download_text_file () {
	stty -echo # Disable input
	aria2c -i "$1.txt" \
		--quiet \
		--file-allocation=none \
		--continue \
		--always-resume \
		--max-tries=3 \
		--max-concurrent-downloads=10
	stty echo # Re-enable input
}

# Choose whether download or watch feature movie
watch_download_feature () {
	folder="$(head -n 3 $feature_path/$1.txt | tail -n 1 | cut -c 6-)" # Read file and get the folder path from line 2
	while true; do
		if [[ "$2" == "watch" ]]; then
			m3u8="$(head -n 1 $feature_path/$1.txt | cut -c 3-)"
			clear
			ffplay -loglevel error -fs "$m3u8"
		elif [[ ! -f "$folder/$1.mp4" && "$2" == "down" ]]; then
			clear
			echo -e "Downloading $1\nPlease take your time."
			download_text_file "$feature_path/$1"
			clear
			merge_ts "$1" "folder"
			convert_vtt "$1" "$folder"
			mv "$feature_path/$1.txt" "$feature_path/$1 - [downloaded].txt"
			read -s -p "Your movie has been downloaded and saved in \"$1\"."
		else
			mv "$feature_path/$1.txt" "$feature_path/$1 - [downloaded].txt"
			read -s -p "Your movie has ALREADY been downloaded and saved in \"$1\"."
		fi
		return
	done
}

# Merge all ts file with ffmpeg
merge_ts () {
	ls -v "$2/"*.ts | xargs -d '\n' cat > "$2/$1.ts"
	ffmpeg -loglevel error -y -i "$2/$1.ts" -vcodec copy -acodec copy "$2/$1.mp4"
	rm "$2/"*.ts "$2/"*.aria2
	clear
}

# Convert vtt to srt subtitle
convert_vtt () {
	_feature="$1"
	for file in $(find "$feature_path" -name "$_feature*.vtt"); do
		name=${file##*/} # Get the filename and its extension
		name=${name%.vtt} # Strip the extention
		ffmpeg -loglevel error -y -i "$file" "$2/$name.srt"
		clear
	done
}

# Download URL with headers, auto rety on error, always continue download, no pre-allocated disk size
download_anime () {
	stty -echo # Disable input
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
	stty echo # Re-enable input
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
	mv "$anime_path/$1.txt" "$anime_path/$1 - [downloaded].txt"
	stty echo # Re-enable input
}

# Choose whether download or watch single anime episode
watch_download_anime () {
	IFS=' ' # Space delimiter
	while read -r _ep _url; do
		if [[ "$_ep" == "$2" ]]; then
			url=${_url%$'\r'} # Strip the `\r` from each line
		fi
	done < "$anime_path/$1.txt"
	while true; do
		if [[ "$3" == "watch" ]]; then
			clear
			ffplay -reconnect 1 -reconnect_at_eof 1 -reconnect_streamed 1 -reconnect_delay_max 2 -loglevel error -fs -i "$url" -headers "Referer: https://twist.moe/"
		elif [[ "$3" == "down" ]]; then
			clear
			echo "Downloading $1 Episode $2"
			download_anime "$1" "$url" "$2"
			clear
			read -s -p "Your episode has been downloaded and saved in \"$1\"."
		fi
		return
	done
}

# Choose whether download or watch single tv series episode
watch_download_series () {
	while true; do
		if [[ "$3" == "watch" ]]; then
			_ep="$2"
			m3u8="$(head -n 1 "$series_path/$1/$_ep.txt" | cut -c 3-)"
			clear
			ffplay -loglevel error -fs "$m3u8"
		elif [[ ! -f "$directory/$1/$2.mp4" && "$3" == "down" ]]; then
			clear
			echo -e "Downloading $1 - $2\nPlease take your time."
			download_text_file "$series_path/$1/$2"
			clear
			merge_ts "$2" "$directory/$1"
			mv "$series_path/$1/$2.txt" "$series_path/$1/$2 - [downloaded].txt"
			read -s -p "Your episode has been downloaded and saved in \"$1\"."
		else
			mv "$series_path/$1/$2.txt" "$series_path/$1/$2 - [downloaded].txt"
			read -s -p "Your episode has ALREADY been downloaded and saved in \"$1\"."
		fi
		return
	done
}

# Control watch or download feature movie
controller_feature_action () {
	clear
	local PS3='Pick your choice: '
	local actions=("Watch the movie" "Download the movie" "Delete the movie" "Download all subtitles" "Back to the movie")
	echo "$1"
	select action in "${actions[@]}"; do
		case $action in
			"Watch the movie")
				watch_download_feature "$1" "watch"
				read -s -p "Press enter to get back to movie."
				clear
				echo "$1"
				;;
			"Download the movie")
				watch_download_feature "$1" "down"
				return
				;;
			"Delete the movie")
				rm "$feature_path/$1.txt"
				return
				;;
			"Download all subtitles")
				convert_vtt "$1"
				return
				;;
			"Back to the movie")
				return
				;;
			*)
				read -s -p "Option $REPLY is invalid."
				clear
				;;
		esac
	done
}

# Control watch or download anime
controller_anime_action () {
	clear
	local PS3='Pick your choice: '
	local actions=("Watch the episode" "Download the episode" "Back to the episode list")
	echo "$1 - Episode $2"
	select action in "${actions[@]}"; do
		case $action in
			"Watch the episode")
				watch_download_anime "$1" "$2" "watch"
				read -s -p "Press enter to get back to episode."
				clear
				echo "$1 - Episode $2"
				;;
			"Download the episode")
				watch_download_anime "$1" "$2" "down"
				return
				;;
			"Back to the episode list")
				return
				;;
			*)
				read -s -p "Option $REPLY is invalid."
				clear
		esac
	done
}


# Choose whether watch or download TV series
controller_series_action () {
	clear
	local PS3='Pick your choice: '
	local actions=("Watch the episode" "Download the episode" "Delete the episode" "Back to the episode list")
	echo "$1 - $2"
	select action in "${actions[@]}"; do
		case $action in
			"Watch the episode")
				watch_download_series "$1" "$2" "watch"
				read -s -p "Press enter to get back to the episode."
				clear
				echo "$1 - $2"
				;;
			"Download the episode")
				watch_download_series "$1" "$2" "down"
				return
				;;
			"Delete the episode")
				rm "$series_path/$1/$2.txt"
				return
				;;
			"Back to the episode list")
				return
				;;
			*)
				read -s -p "Option $REPLY is invalid."
				clear
		esac
	done
}

# Managing all anime episodes
controller_anime_episodes () {
	clear
	local PS3='Choose your episode: '
	local episodes=("All of episodes")
	while read -r __ep __url; do
		IFS=' ' # Space delimiter
		episodes+=("Episode $__ep")
	done < "$anime_path/$1.txt"
	episodes+=("Delete anime" "Back to the anime")
	echo "$1"
	select _ep in "${episodes[@]}"; do
		for _choice in "${episodes[@]}"; do
			if [[ "$_choice" == "$_ep" ]]; then
				if [[ "$_choice" == "Back to the anime" ]]; then
					return
				elif [[ "$_choice" == "Delete anime" ]]; then
					rm "$anime_path/$1.txt"
					return
				elif [[ "$_choice" == "All of episodes" ]]; then
					download_anime_all "$1"
					return
				else
					controller_anime_action "$1" "$(echo $_choice | cut -d' ' -f2)"
					return
				fi
			fi
		done
	done
}

# Managing all TV series episodes
controller_series_episodes () {
	clear
	local PS3='Choose your episode: '
	local episodes=()
	for file in "$series_path/$1/"*.txt; do
		name=${file##*/} # Get the text file name
		name=${name%.txt} # Strip the extention
		if [[ "$name" != "*" ]]; then # '*' means there is no txt file
			episodes+=("$name")
		fi
	done
	episodes+=("Delete the show" "Back to the series")
	echo "$1"
	select _ep in "${episodes[@]}"; do
		for _choice in "${episodes[@]}"; do
			if [[ "$_choice" == "$_ep" ]]; then
				if [[ "$_choice" == "Back to the series" ]]; then
					return
				elif [[ "$_choice" == "Delete the show" ]]; then
					rm "$series_path/$1/"*.txt
					rm -d "$series_path/$1"
					return
				else
					controller_series_action "$1" "$_choice"
					return
				fi
			fi
		done
	done
}

# Managing all feature movie
controller_feature () {
	clear
	local PS3='Choose your movie: '
	local list=("Search for feature movie")
	for file in "$feature_path/"*.txt; do
		name=${file##*/} # Get the filename and its extension
		name=${name%.txt} # Strip the extention
		if [[ "$name" != "*" ]]; then # '*' means there is no txt file
			list+=("$name")
		fi
	done

	list+=("Back to the menu")
	select _feature in "${list[@]}"; do
		for _choice in "${list[@]}"; do
			if [[ "$_choice" == "$_feature" ]]; then
				if [[ "$_choice" == "Search for feature movie" ]]; then
					run_vikv_python
					return
				elif [[ "$_choice" == "Back to the menu" ]]; then
					return
				else
					controller_feature_action "$_feature"
					read -s -p $'\nSorry you have to press enter once more :(\nThis is a feature!'
					clear
				fi
			fi
		done
	done
}

# Managing all anime
controller_anime () {
	clear
	local PS3='Choose your anime: '
	local list=("Search for anime")
	for file in "$anime_path/"*.txt; do
		name=${file##*/} # Get the filename and its extension
		name=${name%.txt} # Strip the extention
		if [[ "$name" != "*" ]]; then # '*' means there is no txt file
			list+=("$name")
		fi
	done

	list+=("Back to the menu")
	select _anime in "${list[@]}"; do
		for _choice in "${list[@]}"; do
			if [[ "$_choice" == "$_anime" ]]; then
				if [[ "$_choice" == "Back to the menu" ]]; then
					return
				elif [[ "$_choice" == "Search for anime" ]]; then
					run_twist_python
					return
				else
					controller_anime_episodes "$_anime"
					read -s -p $'\nSorry you have to press enter once more :(\nThis is a feature!'
					clear
				fi
			fi
		done
	done
}

# Managing all TV series
controller_series () {
	clear
	local PS3='Choose your TV series: '
	local list=("Search for TV series")
	for folder in "$series_path/"*; do
		name=${folder##*/} # Get the folder name
		if [[ "$name" != "*" ]]; then # '*' means there is no folder
			list+=("$name")
		fi
	done

	list+=("Back to the menu")
	select _series in "${list[@]}"; do
		for _choice in "${list[@]}"; do
			if [[ "$_choice" == "$_series" ]]; then
				if [[ "$_choice" == "Back to the menu" ]]; then
					return
				elif [[ "$_choice" == "Search for TV series" ]]; then
					run_drama_python
					return
				else
					controller_series_episodes "$_series"
					read -s -p $'\nSorry you have to press enter once more :(\nThis is a feature!'
					clear
				fi
			fi
		done
	done
}

# Using Prompt statement
clear
PS3='Choose your movie type: '
movies=("Feature movie" "Anime" "TV series" "Exit")
check_directory
while true; do
	select mov in "${movies[@]}"; do
		case $REPLY in
			1)
				controller_feature
				clear
				break
				;;
			2)
				controller_anime
				clear
				break
				;;
			3)
				controller_series
				clear
				break
				;;
			4)
				clear
				exit
				;;
			*)
				read -s -p "$REPLY is an invalid option."
				clear
				;;
		esac
	done
done
