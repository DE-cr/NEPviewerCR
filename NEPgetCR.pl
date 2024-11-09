#!/usr/bin/perl

# NEPviewerCR (https://github.com/DE-cr/NEPviewerCR)
# (file NEPgetCR.pl: get each day's output data and store it locally)
# - (partial) replacement for the official nepviewer.com offer to monitor a
#   photovoltaic micro inverter registered with their site
# - usage: perl NEPgetCR.pl serno yyyy-mm-dd
#   (serno = micro inverter serial number, as registered with nepviewer.com)
#   (yyyy-mm-dd = date of micro inverter registration with nepviewer.com)

use strict;
use warnings;
use Date::Calc qw(Today Add_Delta_Days);
use LWP::Simple;

die "Usage: $0 serno yyyy-mm-dd\n"
  unless "@ARGV" =~ /^[0-9a-f]{8} 20\d\d-[01]\d-[0-3]\d$/;

my ($sn,$install_date) = @ARGV;

my ($y,$m,$d) = Today();
while ( ($y,$m,$d) = Add_Delta_Days($y,$m,$d,-1) ) {
  my $ymd = sprintf "%04d-%02d-%02d", $y, $m, $d;
  exit if $ymd lt $install_date;
  my $fn = $sn."_$ymd.json";
  next if -f $fn;
  $ymd =~ tr/-//d;
  my $url = "https://user.nepviewer.com/pv_monitor/proxy"
          . "/history/$sn/$ymd/$ymd/0/1/2";
  warn "$ymd\n";
  exit unless 200 == getstore($url, $fn);
}
