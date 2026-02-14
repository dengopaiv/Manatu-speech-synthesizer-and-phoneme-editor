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

#ifndef NVDAHELPER_LOCK_H
#define NVDAHELPER_LOCK_H

#include <mutex>

/**
 * A class that provides a locking mechonism on objects.
 * The lock is reeentrant for the same thread.
 */
class LockableObject {
	private:
	std::recursive_mutex _mtx;

	public:

	void acquire() {
		_mtx.lock();
	}

	void release() {
		_mtx.unlock();
	}

	virtual ~LockableObject() {}

};

#endif
