#!/usr/bin/python

import wx
import modules.svd as svd
import modules.my as my
import modules.regview as regview
import modules.perview as perview
import modules.devview as devview
import modules.tview as tview

from collections import defaultdict
import gc


class MyFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title)

        self.dev = svd.device()
        self.filename = None
        self.saved = True

        MainMenu = wx.MenuBar()
        FileMenu = wx.Menu()
        NewFile = FileMenu.Append(wx.ID_NEW, 'New', 'New SVD')
        LoadFile = FileMenu.Append(wx.ID_OPEN, 'Load', 'Load SVD')
        SaveFile = FileMenu.Append(wx.ID_SAVE, 'Save', 'Save SVD')
        SaveAsFile = FileMenu.Append(wx.ID_SAVEAS, 'Save As', 'Save SVD')
        AppExit = FileMenu.Append(wx.ID_EXIT, 'Exit', 'Exit application')

        EditMenu = wx.Menu()
        AddItem = EditMenu.Append(wx.ID_ADD, 'Add Item', 'Add Item')
        DelItem = EditMenu.Append(wx.ID_DELETE, 'Delete Item', 'Delete Item')
        CloneItem = EditMenu.Append(wx.ID_DUPLICATE, 'Clone Item', 'Clone Item')
        ValidItem = EditMenu.Append(wx.ID_APPLY, 'Validate', 'Run Validation')

        InfoMenu = wx.Menu()
        AboutNfo = InfoMenu.Append(wx.ID_ABOUT, 'About', 'About this program')

        MainMenu.Append(FileMenu, '&File')
        MainMenu.Append(EditMenu, '&Edit')
        MainMenu.Append(InfoMenu, '&Info')
        self.SetMenuBar(MainMenu)

        self.Bind(wx.EVT_MENU, self.OnLoad, LoadFile)
        self.Bind(wx.EVT_MENU, self.OnNew, NewFile)
        self.Bind(wx.EVT_MENU, self.OnSave, SaveFile)
        self.Bind(wx.EVT_MENU, self.OnSaveAs, SaveAsFile)
        self.Bind(wx.EVT_MENU, self.OnExit, AppExit)

        self.Bind(wx.EVT_MENU, self.OnAddItem, AddItem)
        self.Bind(wx.EVT_MENU, self.OnDelItem, DelItem)
        self.Bind(wx.EVT_MENU, self.OnCloneItem, CloneItem)
        self.Bind(wx.EVT_MENU, self.OnValidItem, ValidItem)

        self.Bind(wx.EVT_MENU, self.OnAbout, AboutNfo)

        self.Bind(my.MY_EVT, self.OnMyCommand)

        # Create a main window
        self.splitter = wx.SplitterWindow(self)
        self.tree = tview.View(self.splitter, self.dev)
        self.view = devview.View(self.splitter, self.dev)
        self.splitter.SplitVertically(self.tree, self.view)

        self.OnNew(None)

        mSizer = wx.BoxSizer(wx.VERTICAL)
        mSizer.Add(self.splitter, 1, wx.EXPAND | wx.ALL, 0)
        self.SetSizerAndFit(mSizer)

        p = self.splitter.GetSashPosition()
        self.splitter.SetSashPosition(p)

        self.Bind(wx.EVT_SPLITTER_DCLICK, self.onTryUnsplit)

        self.Centre()

    def onTryUnsplit(self, event):
        event.Veto()

    def OnMyCommand(self, event):
        eid = event.GetId()
        eobj = event.GetClientData()
        if eid == my.EVT_SELECTED:
            old = self.view
            new = None
            self.splitter.Freeze()
            if isinstance(eobj, svd.register):
                new = regview.View(self.splitter, eobj)
            if isinstance(eobj, svd.peripheral):
                new = perview.View(self.splitter, eobj)
            if isinstance(eobj, svd.device):
                new = devview.View(self.splitter, eobj)
            if new:
                self.splitter.ReplaceWindow(old, new)
                self.view = new
                old.Destroy()
            self.splitter.Thaw()
            return
        elif eid == my.EVT_REG_NAME_CHANGED or eid == my.EVT_PER_NAME_CHANGED or eid == my.EVT_DEV_NAME_CHANGED:
            self.tree.Reload(eobj)
        elif eid == my.EVT_REG_DELETED or eid == my.EVT_PER_DELETED:
            self.tree.Remove(eobj)
        elif eid == my.EVT_REG_ADDED or eid == my.EVT_PER_ADDED:
            self.tree.Append(eobj)
        if self.saved:
            self.SetLabel('* %s' % (self.GetLabel()))
            self.saved = False

    def OnValidItem(self, event):
        try:
            self.dev.validate()
            wx.MessageBox('No errors found')
        except svd.SVD_error as e:
            self.tree.SelectItem(e.obj)
            wx.MessageBox(e.msg, 'Error', wx.OK | wx.ICON_ERROR)

    def OnAddItem(self, event):
        obj = self.FindFocus()
        self.view.AddItem(obj)
        self.tree.AddItem(obj)

    def OnCloneItem(self, event):
        obj = self.FindFocus()
        self.view.CloneItem(obj)
        self.tree.CloneItem(obj)

    def OnDelItem(self, event):
        obj = self.FindFocus()
        self.view.DelItem(obj)
        self.tree.DelItem(obj)

    def OnNew(self, event):
        self.dev.fromString(svd.default_xml)
        self.tree.LoadDevice(self.dev)
        self.filename = None
        self.SetLabel('New - SVD editor')

    def OnLoad(self, event):
        LoadSvdDialog = wx.FileDialog(self,
                                      'Open System View Ddescription file', '', '',
                                      'SVD files(*.svd)|*.svd', wx.FD_OPEN)
        if LoadSvdDialog.ShowModal() == wx.ID_OK:
            self.filename = LoadSvdDialog.GetPath()
            self.dev.load(self.filename)
            self.tree.LoadDevice(self.dev)
            self.saved = True
            self.SetLabel('%s - SVD editor' % (self.filename))

    def OnSave(self, event):
        if self.filename:
            self.dev.save(self.filename)
            self.saved = True
            self.SetLabel('%s - SVD editor' % (self.filename))

    def OnSaveAs(self, event):
        SaveSvdDialog = wx.FileDialog(self,
                                      'Save System View Description file', '', self.dev.name + '.svd',
                                      'SVD files(*.svd)|*.svd', wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if SaveSvdDialog.ShowModal() == wx.ID_OK:
            self.filename = SaveSvdDialog.GetPath()
            self.dev.save(self.filename)
            self.saved = True
            self.SetLabel('%s - SVD editor' % (self.filename))

    def OnAbout(self, event):
        info = wx.AboutDialogInfo()
        info.SetName('SVD editor')
        info.SetVersion('0.0.1 Beta')
        info.SetDescription('CMSIS System View Description editor tool')
        info.SetCopyright('(C) 2017 Dmitry Filimonchuk')
        lfile = open('LICENSE', 'r')
        info.SetLicense(lfile.read())
        info.WebSite = ('http://github.com/dmitrystu')
        wx.AboutBox(info)

    def OnExit(self, event):
        self.Destroy()


class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, 'SVD editor')
        frame.Show(True)
        self.SetTopWindow(frame)
        return True


if __name__ == '__main__':
    app = MyApp(0)
    app.MainLoop()
