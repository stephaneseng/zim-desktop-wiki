
from zim.plugins.versioncontrol import VCS
import zim.plugins.versioncontrol.hg
import zim.plugins.versioncontrol.git
#####################################################
#
# BAZAAR BACKEND TEST
#
#####################################################
@tests.skipUnless(VCS.check_dependencies(VCS.BZR), 'Missing dependencies')
		zim.plugins.versioncontrol.TEST_MODE = False
		zim.plugins.versioncontrol.TEST_MODE = True
		vcs = VCS.create(VCS.BZR, root)
		self.assertEqual(versions[0][0], '1')
		self.assertEqual(versions[1][0], '2')


#####################################################
#
# GIT BACKEND TEST
#
#####################################################
@tests.slowTest
@tests.skipUnless(VCS.check_dependencies(VCS.GIT), 'Missing dependencies')
class TestGit(tests.TestCase):

	def setUp(self):
		zim.plugins.versioncontrol.TEST_MODE = False

	def tearDown(self):
		zim.plugins.versioncontrol.TEST_MODE = True

	def runTest(self):
		'''Test Git version control'''
		print '\n!! Some raw output from Git could appear here !!'

		root = get_tmp_dir('versioncontrol_TestGit')
		vcs = VCS.create(VCS.GIT, root)
		vcs.init()

		#~ for notebookdir in (root, root.subdir('foobar')):
			#~ detected = VersionControlPlugin._detect_vcs(notebookdir)
			#~ self.assertEqual(detected.__class__, BazaarVCS)
			#~ del detected # don't keep multiple instances around

		subdir = root.subdir('foo/bar')
		file = subdir.file('baz.txt')
		file.write('foo\nbar\n')
		self.assertEqual(''.join(vcs.get_status()), '''\
# On branch master
#
# Initial commit
#
# Changes to be committed:
#   (use "git rm --cached <file>..." to unstage)
#
#	new file:   .gitignore
#	new file:   foo/bar/baz.txt
#
''' )

		vcs.update_staging()
		vcs.commit('test 1')
#[master 0f4132e] test 1
# 1 files changed, 3 insertions(+), 0 deletions(-)
# create mode 100644 foo/bar/baz.txt

		# git plugin doesnt support this atm
		#self.assertRaises(NoChangesError, vcs.commit, 'test 1')

		file = subdir.file('bar.txt')
		file.write('second\ntest\n')

		self.assertEqual(''.join(vcs.get_status()), '''\
# On branch master
# Changes to be committed:
#   (use "git reset HEAD <file>..." to unstage)
#
#	new file:   foo/bar/bar.txt
#
''' )

		vcs.update_staging()
		vcs.commit('test 2')
#[master dbebdf1] test 2
# 0 files changed, 0 insertions(+), 0 deletions(-)
# create mode 100644 foo/bar/bar.txt

		# git plugin doesnt support this atm
		#self.assertRaises(NoChangesError, vcs.commit, 'test 2')

		# these lines contain file perms & hashes
		ignorelines = lambda line: not (line.startswith('new') or line.startswith('index'))
		diff = vcs.get_diff(versions=('HEAD'))
# john@joran:~/code/zim/TEST$ git diff master^
# diff --git a/foo/bar/bar.txt b/foo/bar/bar.txt
# new file mode 100644
# index 0000000..e69de29
		diff = ''.join(filter(ignorelines, diff))
		self.assertEqual(diff, '''\
diff --git a/foo/bar/bar.txt b/foo/bar/bar.txt
--- /dev/null
+++ b/foo/bar/bar.txt
@@ -0,0 +1,2 @@
+second
+test
''' )

		file.write('second\nbaz\n')
		diff = vcs.get_diff()
		diff = ''.join(filter(ignorelines, diff))
		self.assertEqual(diff, '''\
diff --git a/foo/bar/bar.txt b/foo/bar/bar.txt
--- a/foo/bar/bar.txt
+++ b/foo/bar/bar.txt
@@ -1,2 +1,2 @@
 second
-test
+baz
''' )

		vcs.revert()
		self.assertEqual(vcs.get_status(), [
'# On branch master\n',
'nothing to commit (working directory clean)\n'
] )

		file.write('second\nbaz\n')
		vcs.commit_async('test 3')
		diff = vcs.get_diff(versions=('HEAD', 'HEAD^'))
		diff = ''.join(filter(ignorelines, diff))
		self.assertEqual(diff, '''\
diff --git a/foo/bar/bar.txt b/foo/bar/bar.txt
--- a/foo/bar/bar.txt
+++ b/foo/bar/bar.txt
@@ -1,2 +1,2 @@
 second
-test
+baz
''' )

		versions = vcs.list_versions()

		self.assertTrue(isinstance(versions,list))
		#~ print 'VERSIONS>>', versions
		self.assertTrue(len(versions) == 3)
		self.assertTrue(isinstance(versions[0],tuple))
		self.assertTrue(len(versions[0]) == 4)
		self.assertTrue(isinstance(versions[0][0],str))
		self.assertTrue(isinstance(versions[0][1],str))
		self.assertTrue(isinstance(versions[0][2],str))
		self.assertTrue(isinstance(versions[0][3],unicode))
		self.assertEqual(versions[0][3], u'test 1\n')
		self.assertTrue(len(versions[1]) == 4)
		self.assertEqual(versions[1][3], u'test 2\n')
		self.assertTrue(len(versions[2]) == 4)
		self.assertEqual(versions[2][3], u'test 3\n')

		# slightly different, we check the 2nd file
		lines = vcs.get_version(file, version='HEAD^')
		self.assertEqual(''.join(lines), '''\
second
test
''' )

#john@joran:/tmp/test_versioncontrol/versioncontrol_TestGit$ git annotate -t foo/bar/bar.txt
#09be0483        (John Drinkwater        1309533637 +0100        1)second
#526fb2b5        (John Drinkwater        1309533637 +0100        2)baz
#john@joran:/tmp/test_versioncontrol/versioncontrol_TestGit$ git blame -s foo/bar/bar.txt
#09be0483 1) second
#526fb2b5 2) baz

		annotated = vcs.get_annotated(file)
		lines = []
		for line in annotated:
			# get rid of commit hash, its unique
			commit, num, text = line.split(' ')
			lines.append(num+' '+text)
		self.assertEqual(''.join(lines), '''\
1) second
2) baz
''' )

# XXX ignore renames and deletions?

# Below is a test that we dont need to handle, as we can be quite ignorant of them. Especially considering
# how git tracks file moves, ie, it doesnt.

#		file.rename(root.file('bar.txt'))
#		diff = vcs.get_diff()
#john@joran:~/code/zim/TEST$ git diff
#diff --git a/foo/bar/bar.txt b/foo/bar/bar.txt
#deleted file mode 100644
#…

#john@joran:~/code/zim/TEST$ git commit -a -m "Moved test 4"
#[master b099d98] Moved test 4
# 1 files changed, 0 insertions(+), 0 deletions(-)
# rename foo/bar/{bar.txt => boo.txt} (100%)


#####################################################
#
# MERCURIAL BACKEND TEST
#
#####################################################
@tests.slowTest
@tests.skipUnless(VCS.check_dependencies(VCS.HG), 'Missing dependencies')
class TestMercurial(tests.TestCase):

	def setUp(self):
		zim.plugins.versioncontrol.TEST_MODE = False

	def tearDown(self):
		zim.plugins.versioncontrol.TEST_MODE = True

	def runTest(self):
		'''Test Mercurial version control'''
		print '\n!! Some raw output from Mercurial expected here !!'

		root = get_tmp_dir('versioncontrol_TestMercurial')
		vcs = VCS.create(VCS.HG, root)
		vcs.init()

		#~ for notebookdir in (root, root.subdir('foobar')):
			#~ detected = VersionControlPlugin._detect_vcs(notebookdir)
			#~ self.assertEqual(detected.__class__, BazaarVCS)
			#~ del detected # don't keep multiple instances around

		subdir = root.subdir('foo/bar')
		file = subdir.file('baz.txt')
		file.write('foo\nbar\n')

		self.assertEqual(''.join(vcs.get_status()), '''\
A .hgignore
A foo/bar/baz.txt
''' )

		vcs.commit('test 1')
		self.assertRaises(NoChangesError, vcs.commit, 'test 1')

		ignorelines = lambda line: not (line.startswith('+++') or line.startswith('---'))
		# these lines contain time stamps

		file.write('foo\nbaz\n')
		diff = vcs.get_diff()
		diff = ''.join(filter(ignorelines, diff))
		self.assertEqual(diff, '''\
diff --git a/foo/bar/baz.txt b/foo/bar/baz.txt
@@ -1,2 +1,2 @@
 foo
-bar
+baz
''' )

		vcs.revert()
		self.assertEqual(vcs.get_diff(), ['=== No Changes\n'])


		file.write('foo\nbaz\n')
		vcs.commit_async('test 2')
		diff = vcs.get_diff(versions=(0, 1))
		diff = ''.join(filter(ignorelines, diff))
		self.assertEqual(diff, '''\
diff --git a/foo/bar/baz.txt b/foo/bar/baz.txt
@@ -1,2 +1,2 @@
 foo
-bar
+baz
''' )

		versions = vcs.list_versions()
		#~ print 'VERSIONS>>', versions
		self.assertTrue(len(versions) == 2)
		self.assertTrue(len(versions[0]) == 4)
		self.assertEqual(versions[0][0], str(0))
		self.assertEqual(versions[0][3], u'test 1\n')
		self.assertTrue(len(versions[1]) == 4)
		self.assertEqual(versions[1][0], str(1))
		self.assertEqual(versions[1][3], u'test 2\n')


		lines = vcs.get_version(file, version=0)
		self.assertEqual(''.join(lines), '''\
foo
bar
''' )

		annotated = vcs.get_annotated(file)
		lines = []
		for line in annotated:
			# get rid of user name
			ann, text = line.split(':')
			lines.append(ann[0]+':'+text)
		self.assertEqual(''.join(lines), '''\
0: foo
1: baz
''' )

		#~ print 'TODO - test moving a file'
		file.rename(root.file('bar.txt'))

		diff = vcs.get_diff()
		diff = ''.join(filter(ignorelines, diff))
		self.assertEqual(diff, '''\
diff --git a/foo/bar/baz.txt b/bar.txt
rename from foo/bar/baz.txt
rename to bar.txt
''' )