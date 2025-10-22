#!/bin/bash

# --- Configuration ---
SCORE=0
MAX_SCORE=10
GRADE_DIR="/home/kali/week1/lab1/submission"
PASSWD_FILE="${GRADE_DIR}/passwd"
SHADOW_FILE="${GRADE_DIR}/shadow"
OUTPUT_FILE="${GRADE_DIR}/output.txt"
EMPTY_FILE="${GRADE_DIR}/empty"
KALI_LINE_PASSWD=$(grep "^kali:" /etc/passwd)
KALI_LINE_SHADOW=$(grep "^kali:" /etc/shadow)

echo "--- Grading Script for Lab 1 ---"

# --- Helper Function for Grading ---
check_step() {
    local condition=$1
    local success_msg=$2
    local failure_msg=$3
    if eval "$condition"; then
        echo "✅ [1pt] $success_msg"
        SCORE=$((SCORE + 1))
    else
        echo "❌ [0pt] $failure_msg"
    fi
}

# --- 1 & 2: Folder Creation and Working Directory ---
echo
echo "## Step 1 & 2: Directory Structure"
check_step "[[ -d \"$GRADE_DIR\" ]]" \
    "Directory $GRADE_DIR exists." \
    "Directory $GRADE_DIR does not exist."

# Note: We can't easily check 'cd' or 'mkdir' commands, only the result.

# --- 3 & 4: Copying Files ---
echo
echo "## Step 3 & 4: File Copy"
# Check passwd copy
check_step "[[ -f \"$PASSWD_FILE\" ]] && cmp -s \"$PASSWD_FILE\" /etc/passwd" \
    "File passwd copied correctly." \
    "File passwd is missing or its content is incorrect."

# Check shadow copy
check_step "[[ -f \"$SHADOW_FILE\" ]]" \
    "File shadow exists in the submission folder." \
    "File shadow is missing from the submission folder."

# --- 5: Change Owner and Group ---
echo
echo "## Step 5: Ownership Change (shadow file)"
# Check owner is kali
check_step "stat -c '%U' \"$SHADOW_FILE\" | grep -q 'kali'" \
    "Owner of shadow file is 'kali'." \
    "Owner of shadow file is not 'kali'."

# Check group owner is root
check_step "stat -c '%G' \"$SHADOW_FILE\" | grep -q 'root'" \
    "Group owner of shadow file is 'root'." \
    "Group owner of shadow file is not 'root'."

# --- 6: Change Permissions ---
echo
echo "## Step 6: Permission Change (shadow file)"
# Check permissions are rw------- (600)
check_step "stat -c '%a' \"$SHADOW_FILE\" | grep -q '600'" \
    "Permissions of shadow file are '600' (rw-------)." \
    "Permissions of shadow file are not '600' (Found: $(stat -c '%a' "$SHADOW_FILE"))."

# --- 7: Empty File Creation ---
echo
echo "## Step 7: Empty File"
# Check if file exists AND size is zero
check_step "[[ -f \"$EMPTY_FILE\" ]] && [[ ! -s \"$EMPTY_FILE\" ]]" \
    "Empty file 'empty' created and is size zero." \
    "Empty file 'empty' is missing or not empty."

# --- 8 & 9: Redirection and Appending (CORRECTED) ---
echo
echo "## Step 8 & 9: Content Redirection (output.txt) - FIXED"
OUTPUT_FILE="${GRADE_DIR}/output.txt"

if [[ -f "$OUTPUT_FILE" ]]; then
    # Check if the file has exactly 2 lines
    if [[ $(wc -l < "$OUTPUT_FILE") -ne 2 ]]; then
        echo "❌ [0pt] output.txt has the wrong number of lines (Expected: 2, Found: $(wc -l < "$OUTPUT_FILE"))."
    else
        # Check Step 8 (Redirection - passwd file content)
        # passwd line starts with 'kali:' and contains fields separated by colons
        LINE1_OK=$(head -n 1 "$OUTPUT_FILE" | grep -qE "^kali:[^:]*:[0-9]+:[0-9]+:" && echo $?)
        check_step "[[ \"$LINE1_OK\" -eq 0 ]]" \
            "First line of output.txt is the kali entry from passwd (Redirection)." \
            "First line of output.txt is incorrect (Check content and redirection). Found: $(head -n 1 "$OUTPUT_FILE")"

        # Check Step 9 (Appending - shadow file content)
        # shadow line starts with 'kali:' and the password field usually starts with '$' (e.g., $6$ or $5$)
        LINE2_OK=$(tail -n 1 "$OUTPUT_FILE" | grep -qE "^kali:\$[^:]*:[0-9]+:[0-9]+:" && echo $?)
        check_step "[[ \"$LINE2_OK\" -eq 0 ]]" \
            "Second line of output.txt is the kali entry from shadow (Appending)." \
            "Second line of output.txt is incorrect (Check content and appending). Found: $(tail -n 1 "$OUTPUT_FILE")"
    fi
else
    echo "❌ [0pt] output.txt is missing."
fi
#
# --- 10: Software Installation (CORRECTED) ---
echo
echo "## Step 10: Nginx Installation - FIXED"
# Check specifically for the 'nginx' package, using the 'ii' status for fully installed
check_step "dpkg -l | grep '^ii.*nginx\s' | grep -q -E '\snginx\s'" \
    "The main 'nginx' server package is fully installed." \
    "The main 'nginx' server package is NOT fully installed. (Found only common files or package is missing/broken)."


# --- Final Grade ---
echo
echo "-------------------------------------"
echo "FINAL GRADE: $SCORE / $MAX_SCORE"
echo "-------------------------------------"
