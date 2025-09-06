Based off of a file renamer by James Faulkner of HowToGeek [https://www.howtogeek.com/57661/stupid-geek-tricks-randomly-rename-every-file-in-a-directory/]

For archiving purposes, I needed a version of this that renames the file based off the metadata, in this case, the date modified.

---
This is a Windows batch script that renames every file in the current directory to its last modified timestamp using the format:
YYYYMMDD-HHMM.ext

It also logs the original and new file names to '__Translation.txt' and allows changes to be undone.

---

How to Use

1. Drop 'Date_Renamer.bat' into the folder with files to rename.
2. Open the script in a text editor.
3. Set this line to rename files:

   set "Undo=0"

  [This should be enabled by default]
4. Run the script. It will:
  a. Rename all files except itself and the log file (__Translation.txt)
  b. Generate a log file (__Translation.txt) for back up/undo purposes.

How to Undo
1. Modify this line in the script:
  set "Undo=1"
2. Run the script again. It will:
  a. Read the translation file and rename the files back to their original names.
  b. Delete the log file.
