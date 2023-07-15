#!/usr/bin/perl -w \

# project: https://github.com/DE-cr/NEPviewerCR
# file: NEPviewerCR.pl

use strict;
use warnings;

undef $/;  # slurp mode

open STDIN, 'wget -qO- --post-data=token=<<token>> '
           .'http://nep.nepviewer.com/pv_monitor/appservice/detail/<<SN>> |'
  unless @ARGV;

while (<>) {
  my ($kwh, $prev_time, $prev_watt) = 0;
  my $re = qr/(\d+)000,(\d+)/;                 # straight from the net
  $re = qr/(?m:^(.+) = +(\d+))/ unless /$re/;  # ...or our own text output?
  while (/$re/g) {
    my ($time, $watt) = ($1, $2);
    my ($date, $hm) = split / /, $time;
    if (defined $hm) { $time = 60 * (60 * substr($hm,0,2) + substr($hm,3,2)); }
    else {  # ^- our own text output / v- straight from the net
      my ($s, $m, $h, $D, $M, $Y) = gmtime $time;
      $date = sprintf '%04d-%02d-%02d', $Y+1900, $M+1, $D;
      $hm = sprintf '%02d:%02d', $h, $m;
    }
    if (defined $prev_time)
    { $kwh += ($time - $prev_time) / 3600 * ($watt + $prev_watt) / 2 / 1000; }
    else {  # first data point
      my $options = q(--y2 1 --domain --timefmt %H:%M --set 'format x "%H"');
      my @special = -t STDOUT && $ENV{DISPLAY}  # graphic or text output?
                    ? qw(--terminal x11 --lines
                         --title 'Date: $date'
                         --xlabel 'Time [hour]'
                         --ylabel 'Power [W]' --y2label 'Energy [kWh]'
                         --legend 0 Power --legend 1 Energy)
                    : '--terminal dumb | tr AB -o';
      ($options .= " @special") =~ s/\$date/$date/g;
      open PLOT, "| feedgnuplot $options";
    }
    printf "%s %s = %3d W\n", $date, $hm, $watt;
    printf PLOT "%s\t%d\t%g\n", $hm, $watt, $kwh;
    ($prev_time, $prev_watt) = ($time, $watt);
  }
  printf "%.3f kWh\n", $kwh;
}
