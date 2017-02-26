import wx
import wx.grid as gridlib
import my as my


class registerTable(my.myTable):
    def __init__(self, parent, data):
        my.myTable.__init__(self, parent, data)
        self.labels = ('Name', 'DisplayName', 'Description', 'Offset', 'Size', 'Access', 'ResetValue')

    def GetRowLabelValue(self, row):
        return self.labels[row]

    def GetNumberRows(self):
        return 7

    def GetNumberCols(self):
        # we should create extra col otherwise GetAttr not fired properly (mb bug in wx)
        return 2

    def IsEmptyCell(self, row, col):
        return self.get_data(row, col) is None

    def GetValue(self, row, col):
        val = self.get_data(row, col)
        return val if val is not None else ''

    def GetAttr(self, row, col, kind):
        data = self.data
        if data is None:
            return None
        elif row == 4:
            return None if data.rsize else self.Attr('Gray')
        elif row == 5:
            return self.Attr('DropDown') if data.access else self.Attr('DropGray')
        elif row == 6:
            return None if data.rvalue else self.Attr('Gray')
        else:
            return None

    def SetValue(self, row, col, val):
        data = self.data
        if data is None:
            return
        elif row == 0:
            if val and data.name != val:
                data.name = val
                my.post_event(self.parent, my.EVT_REG_NAME_CHANGED, data)
        elif row == 1:
            data.dispname = val
        elif row == 2:
            data.desc = val
        elif row == 3:
            data.offset = val
        elif row == 4:
            data.rsize = val
        elif row == 5:
            if data.access != val:
                data.access = val
                my.post_event(self.parent, my.EVT_REG_ACCS_CHANGED, data)
        elif row == 6:
            data.rvalue = val

    def get_data(self, row, col):
        return {
            0: self.data.name,
            1: self.data.dispname,
            2: self.data.desc,
            3: self.data.offset,
            4: self.data.vsize,
            5: self.data.vaccess,
            6: self.data.vvalue
        }.get(row, None)


class fieldsTable(my.myTable):
    def __init__(self, parent, data):
        my.myTable.__init__(self, parent, data)
        self.labels = ('BO', 'BW', ' Field ', 'Description', ' Access ')
        self.workset = self.init_workset(data)
        self.rowcount = len(self.workset)

    def GetColLabelValue(self, col):
        return self.labels[col]

    def GetNumberRows(self):
        return self.rowcount

    def GetNumberCols(self):
        return 5

    def IsEmptyCell(self, row, col):
        return self.get_data(row, col) is None

    def GetValue(self, row, col):
        val = self.get_data(row, col)
        return val if val is not None else ''

    def GetAttr(self, row, col, kind):
        data = self.workset[row]
        if col == 4:
            return self.Attr('DropDown') if data[1].access else self.Attr('DropGray')
        return self.Attr('Gray') if data.atrib == 'new' else None

    def SetValue(self, row, col, val):
        data = self.workset[row]
        if col == 0:
            data.item.bito = val
        if col == 1:
            data.item.bitw = val
        if col == 2:
            data.item.name = val if val else data.name
        if col == 3:
            data.item.desc = val
        if col == 4:
            data.item.access = val
        # checking for data add
        if data.atrib == 'new' and data.item.valid:
            self.data.addField(data.item)
            my.post_event(self.parent, my.EVT_FIELD_ADDED, data.item)

    def Reload(self):
        self.workset = self.init_workset(self.data)
        ext = len(self.workset)
        if ext == self.rowcount:
            return
        if ext > self.rowcount:
            msg = gridlib.GridTableMessage(self, gridlib.GRIDTABLE_NOTIFY_ROWS_APPENDED, ext - self.rowcount)
        else:
            msg = gridlib.GridTableMessage(self, gridlib.GRIDTABLE_NOTIFY_ROWS_DELETED, ext, self.rowcount - ext)
        self.rowcount = ext
        self.GetView().ProcessTableMessage(msg)

    def DelRecord(self, index):
        record = self.workset[index]
        if record.atrib == 'main':
            self.data.delField(record.item)
            my.post_event(self.parent, my.EVT_FIELD_DELETED, record.item)

    def init_workset(self, data):
        workset = [self.wItem('main', x) for x in data.fields]
        newitem = data.newField()
        if newitem:
            workset.append(self.wItem('new', newitem))
        return workset

    def get_data(self, row, col):
        return {
            0: self.workset[row].item.bito,
            1: self.workset[row].item.bitw,
            2: self.workset[row].item.name,
            3: self.workset[row].item.desc,
            4: self.workset[row].item.vaccess
        }.get(col, None)


class View(wx.Panel):
    def __init__(self, parent, data=None):
        wx.Panel.__init__(self, parent)
        self.data = data

        rbox = wx.StaticBox(self, label='Register')
        self.rtable = registerTable(self, data)
        self.rgrid = my.myGrid(rbox)
        self.rgrid.SetTable(self.rtable, True)
        self.rgrid.ShowScrollbars(wx.SHOW_SB_NEVER, wx.SHOW_SB_NEVER)
        # we should create extra col (mb bug in wx)
        self.rgrid.HideCol(1)
        self.rgrid.HideColLabels()
        self.rgrid.SetRowLabelSize(-1)

        fbox = wx.StaticBox(self, label='Register Bitfields')
        self.ftable = fieldsTable(self, data)
        self.fgrid = my.myGrid(fbox)
        self.fgrid.SetTable(self.ftable, True)
        self.fgrid.SetColLabelSize(-1)
        self.fgrid.SetSelectionMode(gridlib.Grid.wxGridSelectRows)
        self.fgrid.ShowScrollbars(wx.SHOW_SB_NEVER, wx.SHOW_SB_ALWAYS)
        self.fgrid.HideRowLabels()

        self.Bind(wx.EVT_SIZE, self.onResize)
        self.Bind(my.MY_EVT, self.OnMyEvent)

        rsizer = wx.StaticBoxSizer(rbox, wx.VERTICAL)
        rsizer.Add(self.rgrid, 0, wx.EXPAND | wx.ALL, 3)

        fsizer = wx.StaticBoxSizer(fbox, wx.VERTICAL)
        fsizer.Add(self.fgrid, 1, wx.EXPAND | wx.ALL, 3)

        msizer = wx.BoxSizer(wx.VERTICAL)
        msizer.Add(rsizer, 0, wx.EXPAND | wx.ALL, 3)
        msizer.Add(fsizer, 1, wx.EXPAND | wx.ALL, 3)

        self.SetSizerAndFit(msizer)

    def OnMyEvent(self, event):
        eid = event.GetId()
        if eid == my.EVT_REG_ACCS_CHANGED:
            self.fgrid.ForceRefresh()
        elif eid == my.EVT_FIELD_ADDED or eid == my.EVT_FIELD_DELETED:
            self.ftable.Reload()
        wx.PostEvent(self.GetGrandParent(), event)

    def DelItem(self, obj):
        if obj == self.fgrid:
            if wx.OK == wx.MessageBox('Selected fields will be deleted',
                                      'Confirm item deletion',
                                      wx.OK | wx.CANCEL | wx.ICON_QUESTION):
                for x in reversed(self.fgrid.GetSelectedRows()):
                    self.ftable.DelRecord(x)
                obj.ClearSelection()

    def AddItem(self, obj):
        dlg = wx.TextEntryDialog(self, 'Enter new Field name', 'New bitfield', 'NEW_BITFIELD')
        if wx.ID_OK == dlg.ShowModal():
            nf = self.data.newField(dlg.GetValue())
            names = [x.name for x in self.data.fields]
            if nf and nf.name and nf.name not in names:
                self.data.addField(nf)
                my.post_event(self, my.EVT_FIELD_ADDED, nf)
            else:
                wx.MessageBox('Incorrect or existed name', 'Error', wx.OK | wx.ICON_ERROR)

    def CloneItem(self, obj):
        pass

    def onResize(self, event):
        self.Layout()
        self.fgrid.FitWidth(3)
        self.rgrid.FitWidth(0)
