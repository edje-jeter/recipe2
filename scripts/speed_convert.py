#!/usr/bin/env python

"""
Purpose: convert miles per hour to different units.

The units and the conversion factors were provided.
"""

# Time Conversions
s_per_hour = 3600
hours_per_day = 24
day_per_wk = 7
wk_per_frtnt = 2

# Distance Conversions
m_per_mile = 1609.34
bc_per_m = 117.647
yd_per_m = 1.09361
yd_per_frlng = 220
ft_per_yd = 3

# Other
speed_of_sound_fps = 1130
c = 299792458


def mph_to_meters_per_second(mph):
    return mph * m_per_mile / s_per_hour


def barleycorns_per_day(mps):
    return mps * bc_per_m * s_per_hour * hours_per_day


def furlongs_per_fortnight(mps):
    m_to_frlng = mps * yd_per_m / yd_per_frlng
    s_to_frtnt = s_per_hour * hours_per_day * day_per_wk * wk_per_frtnt

    return m_to_frlng * s_to_frtnt


def mach_num(mps):
    fps = mps * yd_per_m * ft_per_yd

    return fps / speed_of_sound_fps


def percent_of_c(mps):
    return mps * 100 / c


mph = float(raw_input("Enter a value (>= 1) in miles per hour: "))
mps = mph_to_meters_per_second(mph)

bcd = barleycorns_per_day(mps)
fpf = furlongs_per_fortnight(mps)
mch = mach_num(mps)
poc = percent_of_c(mps)

print "\nThe speed %.0f miles per hour is equivalent to: \n" % mph
print "%s barleycorns per day" % "{:,.0f}".format(bcd)
print "%s furlongs per fortnight" % "{:,.0f}".format(fpf)
print "Mach %s" % "{:,.5f}".format(mch)
print "%s %% of the speed of light" % "{:,.9f}".format(poc)
print "\n"
