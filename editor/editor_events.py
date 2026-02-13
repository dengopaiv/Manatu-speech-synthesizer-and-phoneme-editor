"""Custom wx events for the phoneme editor."""

import wx.lib.newevent

StatusUpdateEvent, EVT_STATUS_UPDATE = wx.lib.newevent.NewEvent()
PlayDoneEvent, EVT_PLAY_DONE = wx.lib.newevent.NewEvent()
