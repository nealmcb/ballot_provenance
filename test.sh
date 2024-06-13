# Test process_package on a sample election
# Run in debug mode, and check resulting files and log against vetted results

election="sample-election-trimmed_package"
startdir=$PWD

dir=`mktemp -d`
cd $dir

process_package -d 20 $startdir/test/$election.zip > $election.hashfile 2> log

diff -r $startdir/test/$election.testout .  &&
    rm -rf $dir
