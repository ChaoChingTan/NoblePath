#!/bin/bash

TOTAL=0
USER="kali"

echo "Grading tasks for $USER..."

# 1. Check folder creation
if [[ -d "/home/kali/week1/lab1/submission" ]]; then
  echo "Task 1: ✅"
  TOTAL=$((TOTAL + 10))
else
  echo "Task 1: ❌"
fi

# 2. Skip - runtime state
echo "Task 2: (Skipped - runtime state not verifiable)"

# 3. Check file copy - exact match
SRC_FILE="/etc/passwd"
DST_FILE="/home/kali/week1/lab1/submission/passwd"

if [[ -f "$DST_FILE" && -f "$SRC_FILE" ]]; then
  if cmp -s "$SRC_FILE" "$DST_FILE"; then
    echo "Task 3: ✅"
    TOTAL=$((TOTAL + 10))
  else
    echo "Task 3: ❌ (File exists but contents differ)"
  fi
else
  echo "Task 3: ❌ (File missing)"
fi

# 4. Check file2 copy - exact match with sudo
SRC_FILE2="/etc/shadow"
DST_FILE2="/home/kali/week1/lab1/submission/shadow"

if [[ -f "$DST_FILE2" ]]; then
  if sudo test -f "$SRC_FILE2"; then
    if sudo cmp -s "$SRC_FILE2" "$DST_FILE2"; then
      echo "Task 4: ✅"
      TOTAL=$((TOTAL + 10))
    else
      echo "Task 4: ❌ (File exists but contents differ)"
    fi
  else
    echo "Task 4: ❌ (Source file missing or unreadable)"
  fi
else
  echo "Task 4: ❌ (Destination file missing)"
fi

# 5. Ownership check
TARGET="$DST_FILE2"
OWNER=$(stat -c "%U" "$TARGET" 2>/dev/null)
GROUP_OWNER=$(stat -c "%G" "$TARGET" 2>/dev/null)
if [[ "$OWNER" == "kali" && "$GROUP_OWNER" == "root" ]]; then
  echo "Task 5: ✅"
  TOTAL=$((TOTAL + 10))
else
  echo "Task 5: ❌"
fi

# 6. Permissions check
PERMS_ACTUAL=$(stat -c "%a" "$TARGET" 2>/dev/null)
if [[ "$PERMS_ACTUAL" == "600" ]]; then
  echo "Task 6: ✅"
  TOTAL=$((TOTAL + 10))
else
  echo "Task 6: ❌"
fi

# 7. Check for file3
if [[ -f "/home/kali/week1/lab1/submission/empty" ]]; then
  echo "Task 7: ✅"
  TOTAL=$((TOTAL + 10))
else
  echo "Task 7: ❌"
fi

# 8. Grep $USER from passwd → output.txt
if grep -q "kali" "passwd"; then
  LINE=$(grep "kali" "passwd" | head -n1)
  OUT_CONTENT=$(head -n1 "/home/kali/week1/lab1/submission/output.txt" 2>/dev/null)
  if [[ "$LINE" == "$OUT_CONTENT" ]]; then
    echo "Task 8: ✅"
    TOTAL=$((TOTAL + 10))
  else
    echo "Task 8: ❌"
  fi
else
  echo "Task 8: ❌ (User not found in passwd)"
fi

# 9. Append from shadow → output.txt (with sudo)
if sudo grep -q "kali" "shadow"; then
  LINE=$(sudo grep "kali" "shadow" | head -n1)
  DEST_FILE="/home/kali/week1/lab1/submission/output.txt"
  if [[ -f "$DEST_FILE" && "$(tail -n1 "$DEST_FILE")" == "$LINE" ]]; then
    echo "Task 9: ✅"
    TOTAL=$((TOTAL + 10))
  else
    echo "Task 9: ❌"
  fi
else
  echo "Task 9: ❌ (User not found in shadow or unreadable)"
fi

# 10. Last line from /usr/share/dict/words → first line of output2.txt
if [[ -f "/usr/share/dict/words" ]]; then
  LAST=$(tail -n1 "/usr/share/dict/words")
  OUT2_FIRST=$(head -n1 "/home/kali/week1/lab1/submission/output2.txt" 2>/dev/null)
  if [[ "$LAST" == "$OUT2_FIRST" ]]; then
    echo "Task 10: ✅"
    TOTAL=$((TOTAL + 10))
  else
    echo "Task 10: ❌"
  fi
else
  echo "Task 10: ❌ (Missing /usr/share/dict/words)"
fi

# 11. First line from /usr/share/dict/words → appended to output2.txt
if [[ -f "/usr/share/dict/words" ]]; then
  FIRST=$(head -n1 "/usr/share/dict/words")
  DEST_FILE2="/home/kali/week1/lab1/submission/output2.txt"
  if [[ -f "$DEST_FILE2" && "$(tail -n1 "$DEST_FILE2")" == "$FIRST" ]]; then
    echo "Task 11: ✅"
    TOTAL=$((TOTAL + 10))
  else
    echo "Task 11: ❌"
  fi
else
  echo "Task 11: ❌ (Missing /usr/share/dict/words)"
fi

echo "-----------------------------"
echo "Final Score: $TOTAL / 100"
