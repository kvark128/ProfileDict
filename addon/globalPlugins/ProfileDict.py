# Copyright (C) 2020 - 2023 Alexander Linkov <kvark128@yandex.ru>
# This file is covered by the GNU General Public License.
# See the file COPYING.txt for more details.
# Ukrainian Nazis and their accomplices are not allowed to use this plugin. Za pobedu!

import globalPluginHandler
import wx
import gui
import config
import globalCommands
import os.path
import ui
import speechDictHandler
import addonHandler
from scriptHandler import script

addonHandler.initTranslation()

class DictionaryDialog(gui.speechDict.DictionaryDialog):

	def __init__(self, parent, title, speechDict):
		super().__init__(parent, title, speechDict)

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = globalCommands.SCRCAT_CONFIG

	def __init__(self):
		super(GlobalPlugin, self).__init__()
		self.profileDicts = {}
		config.post_configProfileSwitch.register(self._handlerProfileSwitch)

		dictMenu = gui.mainFrame.sysTrayIcon.preferencesMenu.FindItemByPosition(1).SubMenu
		self.dictMenuItem = dictMenu.Append(wx.ID_ANY, _("&Profile dictionary..."))
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.onProfileDictionaryCommand, self.dictMenuItem)

		self.dictName = "profile"
		self.defaultProfileName = "default"

		self._handlerProfileSwitch()
		speechDictHandler.dictTypes += (self.dictName,)

	def terminate(self):
		try:
			dictMenu = gui.mainFrame.sysTrayIcon.preferencesMenu.FindItemByPosition(1).SubMenu
			dictMenu.Remove(self.dictMenuItem)
		except Exception:
			pass

	def getProfileDict(self):
		p = config.conf.profiles[-1].name
		if p is None:
			p = self.defaultProfileName

		speechDict = self.profileDicts.get(p)
		if speechDict is None:
			speechDict = speechDictHandler.SpeechDict()
			speechDict.load(os.path.join(speechDictHandler.speechDictsPath, "profileDicts", "%s.dic" % p))
			self.profileDicts[p] = speechDict
		return speechDict

	def _handlerProfileSwitch(self):
		speechDict = self.getProfileDict()
		speechDictHandler.dictionaries[self.dictName] = speechDict

	@script(description=_("Shows the NVDA profile dictionary dialog"))
	def script_activateProfileDictionaryDialog(self, gesture):
		self.onProfileDictionaryCommand()

	@script(description=_("Turns profile dictionary on or off"))
	def script_toggleProfileDict(self, gesture):
		t = list(speechDictHandler.dictTypes)
		if self.dictName in t:
			t.remove(self.dictName)
			msg = _("Profile dictionary off")
		else:
			t.append(self.dictName)
			msg = _("Profile dictionary on")

		speechDictHandler.dictTypes = tuple(t)
		ui.message(msg)

	def onProfileDictionaryCommand(self, event=None):
		speechDict = self.getProfileDict()
		profileName = os.path.split(speechDict.fileName)[-1][:-4]
		if profileName == self.defaultProfileName:
			profileName = _("default")
		gui.mainFrame._popupSettingsDialog(DictionaryDialog, _("Profile dictionary for %s") % profileName, speechDict)
