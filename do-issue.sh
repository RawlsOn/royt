#!/bin/bash

## . ./do-issue.sh 10 이렇게 실행해야 cd 가 먹음

if [ $# -eq 0 ]; then
	echo "Error: Worktree 이름을 명시해주세요!"
	return 1
fi

ARGUMENT=$1
WORKTREE_PATH="../issue-$ARGUMENT"

# Create the worktree, and if successful, change directory
if git worktree add "$WORKTREE_PATH"; then
	echo "Worktree 생성 성공: $WORKTREE_PATH"
	cd "$WORKTREE_PATH" || return 1 # Use exit for standalone scripts
	echo "디렉터리 변경 완료 : $(pwd)"

	# Extract the number from the argument
	# This assumes the number is the last part after the last hyphen
	# Example: "feature-branch-123" will extract "123"
	ISSUE_NUMBER=$(echo "$ARGUMENT" | awk -F'-' '{print $NF}')

	# Check if ISSUE_NUMBER is a valid number (optional, but good practice)
	if [[ "$ISSUE_NUMBER" =~ ^[0-9]+$ ]]; then
		echo "Running claude command for issue: #$ISSUE_NUMBER"
		# echo "/resolve-issue $ISSUE_NUMBER"
		command="claude --verbose \"/resolve-issue $ISSUE_NUMBER\""
		# command="claude"
		echo $command
		eval $command
	else
		echo "Warning: Could not extract a valid issue number from '$ARGUMENT'. Skipping claude command."
	fi

else
	echo "Worktree 생성 실패"
	return 1 # Use exit for standalone scripts
fi


