#!/usr/bin/perl

# NEPviewerCR (https://github.com/DE-cr/NEPviewerCR)
# (file NEPstatusCR.pl)
# - (partial) replacement for the official nepviewer.com offer to monitor a
#   photovoltaic micro inverter registered with their site
# - usage: perl NEPstatusCR.pl sn ...
#   (sn = micro inverter serial number, as registered with nepviewer.com)

use strict;
use warnings;
use LWP::Simple;

foreach my $sn (@ARGV) {
  my $data = get("http://user.nepviewer.com/pv_monitor/proxy/status/$sn/0/2/");
  next unless defined $data and
  $data =~ /"LastUpDate":"([^"]+).*"now":(\d+).*"today":(\d+).*"total_status":(\d+)/;
  printf "%d W / %g kWh on %s (%g kWh total)\n", $2, $3/1000, $1, $4/1000;
}
