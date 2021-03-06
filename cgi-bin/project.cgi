#!/usr/bin/perl -w
use strict;
use CGI qw(:standard);
use CGI::Carp qw ( fatalsToBrowser ); 
use DBI;
use lib "lib/";
use lib "lib/pangu";
use pangu;
use userCookie;

my $userCookie = new userCookie;
my $userId = (cookie('cid')) ? $userCookie->checkCookie(cookie('cid')) : 0;
exit if (!$userId);

my $commoncfg = readConfig("main.conf");
my $dbh=DBI->connect("DBI:mysql:$commoncfg->{DATABASE}:$commoncfg->{DBHOST}",$commoncfg->{USERNAME},$commoncfg->{PASSWORD});

undef $/;# enable slurp mode
my $html = <DATA>;

my $active = 0;
my $acitveDetector = 0;
my $cookieLibrary = cookie('library') || '';
my $cookieService = cookie('service') || '';
my $projectId = param ('projectId') || '';
my $button;
my $project = '';
if ($projectId)
{
	my $serviceInProject=$dbh->prepare("SELECT * FROM matrix WHERE container LIKE 'service' AND z = $projectId ORDER BY name");
	$serviceInProject->execute();
	while (my @serviceInProject = $serviceInProject->fetchrow_array())
	{
		$serviceInProject[2] = "Unknown service!" unless($serviceInProject[2]);
		$project = "<div id='inProject$projectId$$'><ul>\n" unless($project);
		$project .= "<li style='white-space: nowrap;'><a href='service.cgi?serviceId=$serviceInProject[0]' title ='Service: $serviceInProject[0]'><span style='left: 0px;top: 0px;display:inline-block;' class='ui-icon ui-icon-document-b'></span>$serviceInProject[2]</a></li>\n";
		$active = $acitveDetector if ($cookieService eq $serviceInProject[0]);
		$acitveDetector++;
	}
	my $libraryInProject=$dbh->prepare("SELECT * FROM matrix WHERE container LIKE 'library' AND z = $projectId ORDER BY name");
	$libraryInProject->execute();
	while (my @libraryInProject = $libraryInProject->fetchrow_array())
	{
		$project = "<div id='inProject$projectId$$'><ul>\n" unless($project);
		$project .= "<li style='white-space: nowrap;'><a href='library.cgi?libraryId=$libraryInProject[0]' title ='Library: $libraryInProject[2]'><span style='left: 0px;top: 0px;display:inline-block;' class='ui-icon ui-icon-folder-collapsed'></span>$libraryInProject[2]</a></li>\n";
		$active = $acitveDetector if ($cookieLibrary eq $libraryInProject[0]);
		$acitveDetector++;
	}
	my $project=$dbh->prepare("SELECT * FROM matrix WHERE id = ?");
	$project->execute($projectId);
	my @project = $project->fetchrow_array();
	$project[8] = escapeHTML($project[8]);
	$project[8] =~ s/\n/<br>/g;
	$button = "<div class='ui-state-highlight ui-corner-all' style='padding: 0 .7em;'>
		<button style='z-index: 1;float: right; margin-top: .3em; margin-right: .3em;' onclick='openDialog(\"serviceNew.cgi?projectId=$projectId\")'>New Service</button>
		<button style='z-index: 1;float: right; margin-top: .3em; margin-right: .3em;' onclick='openDialog(\"libraryNew.cgi?projectId=$projectId\")'>New Library</button>
		<button style='z-index: 1;float: right; margin-top: .3em; margin-right: .3em;' onclick='refresh(\"menu\")'>Refresh</button>
		<div style='position: relative;'><h2><a id='project$projectId$$' onmouseover='editIconShow(\"project$projectId$$\")' onmouseout='editIconHide(\"project$projectId$$\")' onclick='openDialog(\"projectEdit.cgi?projectId=$projectId\")' title='Edit/Delete Project'>$project[2]</a></h2></div>";
	$button .= "<p>$project[8]</p>" if ($project[8]);
	unless($project)
	{
		$button .= "<p class='ui-state-error ui-corner-all' style='padding: .7em;'><span class='ui-icon ui-icon-alert' style='float: left; margin-right: .3em;'></span>
			<strong>No library/item in this project.</strong></p>";
	}
	$button .= "</div>";
	$project .= "</ul></div>\n" if($project);
	print header(-cookie=>cookie(-name=>'project',-value=>$projectId));
}
else
{
	print header(-type=>'text/html',-status=>'402 Invalid operation');
	exit;
}
$html =~ s/\$projectId/$projectId/g;
$html =~ s/\$\$/$$/g; #plus extra id
$html =~ s/\$button/$button/g;
$html =~ s/\$project/$project/g;
$html =~ s/\$active/$active/g;
$html =~ s/\$commoncfg->{HTDOCS}/$commoncfg->{HTDOCS}/g;

print $html;

__DATA__
$button
$project
<script>
buttonInit();
loadingHide();
$( "#inProject$projectId$$" ).tabs({
	// loading spinner
	beforeLoad: function(event, ui) {
		ui.panel.html('<img src="$commoncfg->{HTDOCS}/css/images/loading.gif" style="vertical-align:middle;"> Loading...');
	},
	create: function (e, ui) {
		loadingShow();
	},
	activate: function (e, ui) {
		loadingShow();
	},
	active: $active
}).addClass( "ui-tabs-vertical ui-helper-clearfix" );
$( "#inProject$projectId$$ li" ).removeClass( "ui-corner-top" ).addClass( "ui-corner-left" );
</script>