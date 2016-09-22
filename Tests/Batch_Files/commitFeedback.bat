REM create & commit a bunch of unrelated files:
REM throughout these tests we should never add an 'unrelated' file
echo "Unrelated_File_Commited_Staged" > Unrelated_File_Commited_Staged.txt
echo "Unrelated_File_Commited_Changed_Staged" > Unrelated_File_Commited_Changed_Staged.txt
echo "Unrelated_File_Commited_Changed_Unstaged" > Unrelated_File_Commited_Changed_Unstaged.txt
git add Unrelated*

echo "Grade_Commited_Unchanged" > Grade_Commited_Unchanged.txt
echo "Commited_Unchanged" > Commited_Unchanged.txt
echo "Grade_Commited_Changed_Staged" > Grade_Commited_Changed_Staged.txt
echo "Grade_Commited_Changed_Unstaged" > Grade_Commited_Changed_Unstaged.txt
git add Grade_Commited*
git commit -m "added Grade_Commited*"

REM new file but still added:
echo "Grade_Commited_Staged" >> Grade_Commited_Staged.txt
echo "Unrelated_File_Commited_Staged" >> Unrelated_File_Commited_Staged.txt
git add Grade_Commited_Staged.txt Unrelated_File_Commited_Staged.txt

REM change a previously committed file but don't add it:
echo "Grade_Commited_Changed_Unstaged" >> Grade_Commited_Changed_Unstaged.txt
echo "Unrelated_File_Commited_Changed_Unstaged" >> Unrelated_File_Commited_Changed_Unstaged.txt
REM brand-new file, not added:
echo "Grade_Untracked" > Grade_Untracked.txt
echo "Unrelated_File_Untracked" > Unrelated_File_Untracked.txt

REM create untracked subdir (git won't traverse these for us)
mkdir SubdirTest
mkdir SubdirTest\AnotherDir
REM glt should add this:
cat > SubdirTest\AnotherDir\Grade_Untracked_Subdir.txt
REM glt should NOT add this:
cat > SubdirTest\AnotherDir\Untracked_Subdir.txt
