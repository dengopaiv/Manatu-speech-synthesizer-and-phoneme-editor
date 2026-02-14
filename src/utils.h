/*
This file is a part of the NV Speech Player project. 
URL: https://bitbucket.org/nvaccess/speechplayer
Copyright 2014 NV Access Limited.
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License version 2.0, as published by
the Free Software Foundation.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
This license can be found at:
http://www.gnu.org/licenses/old-licenses/gpl-2.0.html
*/

#ifndef SPEECHPLAYER_UTILS_H
#define SPEECHPLAYER_UTILS_H

#include <cmath>

// Perlin quintic smootherstep: C2-continuous S-curve
// Maps linear t [0,1] to smooth curve with zero 1st AND 2nd derivatives at endpoints
// Eliminates perceptible acceleration discontinuity at transition boundaries
inline double smoothstep(double t) {
	return t * t * t * (t * (t * 6.0 - 15.0) + 10.0);
}

inline double calculateValueAtFadePosition(double oldVal, double newVal, double curFadeRatio) {
	if(std::isnan(newVal)) return oldVal;
	// Apply smoothstep for gentler start/end of transitions
	double smoothRatio = smoothstep(curFadeRatio);
	return oldVal + ((newVal - oldVal) * smoothRatio);
}

#endif
