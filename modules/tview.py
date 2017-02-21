import wx
import svd
import my


class View(wx.Panel):
    def __init__(self, parent, data=None):
        wx.Panel.__init__(self, parent)
        self.data = {}
        self.tree = wx.TreeCtrl(self)
        self.tree.AddRoot('FROM_RUSSIA_WITH_LOVE')

        self.Bind(wx.EVT_SIZE, self.onResize)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged)

        msizer = wx.BoxSizer(wx.VERTICAL)
        msizer.Add(self.tree, 1, wx.EXPAND | wx.ALL, 3)
        self.SetSizerAndFit(msizer)

    def OnSelChanged(self, event):
        item = self.tree.GetFocusedItem()
        obj = self.tree.GetPyData(item)
        my.post_event(self.GetGrandParent(), my.EVT_SELECTED, obj)

    def Reload(self, obj):
        item = self.data.get(obj, 0)
        if item:
            self.tree.SetItemText(item, obj.name)

    def Remove(self, obj):
        item = self.data.pop(obj, 0)
        if item:
            if self.tree.IsSelected(item):
                self.tree.SelectItem(self.tree.GetPrevVisible(item))
            self.tree.Delete(item)

    def Append(self, obj):
        pi = self.data.get(obj.parent, 0)
        ni = self.tree.AppendItem(pi, obj.name)
        self.tree.SetPyData(ni, obj)
        self.data[obj] = ni
        if isinstance(obj, svd.peripheral):
            for x in obj.registers:
                self.Append(x)

    def LoadDevice(self, device):
        tree = self.tree
        tree.Freeze()
        tree.DeleteAllItems()
        self.data.clear()
        root = tree.AddRoot(device.name)
        tree.SetPyData(root, device)
        self.data[device] = root
        for p in device.peripherals:
            pi = tree.AppendItem(root, p.name)
            tree.SetPyData(pi, p)
            self.data[p] = pi
            for r in p.registers:
                ri = tree.AppendItem(pi, r.name)
                tree.SetPyData(ri, r)
                self.data[r] = ri
        tree.UnselectAll()
        tree.Expand(root)
        tree.SelectItem(root)
        tree.Thaw()

    def AddItem(self, obj):
        pass

    def DelItem(self, obj):
        if obj == self.tree:
            item = self.tree.GetSelection()
            if item.IsOk():
                data = self.tree.GetPyData(item)
                if isinstance(data, svd.device):
                    return
                if wx.OK != wx.MessageBox('%s will be deleted' % (data.name),
                                          'Confirm item deletion',
                                          wx.OK | wx.CANCEL | wx.ICON_QUESTION):
                    return
                if isinstance(data, svd.register):
                    data.parent.delRegister(data)
                if isinstance(data, svd.peripheral):
                    data.parent.delPeripheral(data)
                self.Remove(data)

    def CloneItem(self, obj):
        if obj == self.tree:
            item = self.tree.GetSelection()
            if item.IsOk():
                data = self.tree.GetPyData(item)
                if isinstance(data, svd.device):
                    return
                if wx.OK != wx.MessageBox('%s will be cloned' % (data.name),
                                          'Confirm item clone',
                                          wx.OK | wx.CANCEL | wx.ICON_QUESTION):
                    return
                if isinstance(data, svd.peripheral):
                    xml = data.toXML()
                    p = data.parent
                    new = svd.peripheral(p, xml)
                    new.name = '%s_CLONE' % (data.name)
                    p.addPeripheral(new)
                elif isinstance(data, svd.register):
                    xml = data.toXML()
                    p = data.parent
                    new = svd.register(p, xml)
                    new.name = '%s_CLONE' % (data.name)
                    p.addRegister(new)
                self.Append(new)

    def onResize(self, event):
        self.Layout()
