import wx
import wx.grid as gridlib
import my as my


class peripheralTable(my.myTable):
    def __init__(self, parent, data):
        my.myTable.__init__(self, parent, data)
        self.labels = ('Name', 'Description', 'Group', 'Reference', 'Address', 'Offset', 'Block size')
        self.data = data

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
        if self.data is None:
            return None
        if row == 1:
            return self.Attr('Gray') if not self.data.desc and self.data.ref else None
        if row == 2:
            return self.Attr('Gray') if not self.data.group and self.data.ref else None
        if row == 4:
            return self.Attr('Gray') if not self.data.address and self.data.ref else None
        if row == 5:
            return self.Attr('Gray') if not self.data.aoffset and self.data.ref else None
        if row == 6:
            return self.Attr('Gray') if not self.data.asize and self.data.ref else None
        return None

    def SetValue(self, row, col, val):
        data = self.data
        if data is None:
            return
        elif row == 0:
            if val and data.name != val:
                data.name = val
                my.post_event(self.parent, my.EVT_PER_NAME_CHANGED, data)
        elif row == 1:
            data.desc = val
        elif row == 2:
            data.group = val
        elif row == 3:
            if data.setRef(val):
                my.post_event(self.parent, my.EVT_PER_REF_CHANGED, data)
        elif row == 4:
            data.address = val
        elif row == 5:
            data.aoffset = val
        elif row == 6:
            data.asize = val

    def get_data(self, row, col):
        data = self.data
        if data is None:
            return None
        elif row == 0:
            return data.name
        elif row == 1:
            return data.desc if data.desc else (data.ref.desc if data.ref else None)
        elif row == 2:
            return data.group if data.group else (data.ref.group if data.ref else None)
        elif row == 3:
            return ('->' + data.ref.name) if data.ref else 'no reference'
        elif row == 4:
            return data.address if data.address else (data.ref.address if data.ref else None)
        elif row == 5:
            return data.aoffset if data.aoffset else (data.ref.aoffset if data.ref else None)
        elif row == 6:
            return data.asize if data.asize else (data.ref.asize if data.ref else None)
        else:
            return None


class intsTable(my.myTable):
    def __init__(self, parent, data):
        my.myTable.__init__(self, parent, data)
        self.labels = ('Vector', 'Interrupt name', 'Interrupt description')
        self.workset = self.init_workset(data)
        self.rowcount = len(self.workset)

    def GetColLabelValue(self, col):
        return self.labels[col]

    def GetNumberRows(self):
        return self.rowcount

    def GetNumberCols(self):
        return 3

    def IsEmptyCell(self, row, col):
        return self.get_data(row, col) is None

    def GetValue(self, row, col):
        val = self.get_data(row, col)
        return val if val is not None else ''

    def SetValue(self, row, col, val):
        data = self.workset[row]
        if col == 0:
            data.item.value = val
        elif col == 1:
            data.item.name = val
        elif col == 2:
            data.item.desc = val
        if data.atrib == 'new' and data.item.valid:
            self.data.addInterrupt(data.item)
            my.post_event(self.parent, my.EVT_INT_ADDED, data.item)

    def GetAttr(self, row, col, kind):
        data = self.workset[row]
        return self.Attr('Gray') if data.atrib == 'new' else None

    def DelRecord(self, index):
        record = self.workset[index]
        if record.atrib == 'main':
            self.data.delInterrupt(record.item)
            my.post_event(self.parent, my.EVT_INT_DELETED, record.item)

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

    def init_workset(self, data):
        workset = [self.wItem('main', x) for x in data.interrupts]
        newitem = data.newInterrupt()
        if newitem:
            workset.append(self.wItem('new', newitem))
        return workset

    def get_data(self, row, col):
        return {
            0: self.workset[row].item.value,
            1: self.workset[row].item.name,
            2: self.workset[row].item.desc,
        }.get(col, None)


class regsTable(my.myTable):
    def __init__(self, parent, data):
        my.myTable.__init__(self, parent, data)
        self.labels = ('Offset', 'Register name', 'Register description', 'Access')
        self.workset = self.init_workset(data)
        self.rowcount = len(self.workset)

    def GetColLabelValue(self, col):
        return self.labels[col]

    def GetNumberRows(self):
        return self.rowcount

    def GetNumberCols(self):
        return 4

    def IsEmptyCell(self, row, col):
        return self.get_data(row, col) is None

    def GetValue(self, row, col):
        val = self.get_data(row, col)
        return val if val is not None else ''

    def GetAttr(self, row, col, kind):
        data = self.workset[row]
        if data.atrib == 'ref':
            return self.Attr('ReadOnly')
        if data.atrib == 'new':
            return self.Attr('DropGray') if col == 3 else self.Attr('Gray')
        if col == 3:
            return self.Attr('DropDown') if data.item.access else self.Attr('DropGray')

    def SetValue(self, row, col, val):
        data = self.workset[row]
        if data.atrib == 'ref':
            return
        if col == 0:
            data.item.offset = val
        elif col == 1:
            if data.atrib == 'main':
                my.post_event(self.parent, my.EVT_REG_NAME_CHANGED, data.item)
            data.item.name = val
        elif col == 2:
            data.item.desc = val
        elif col == 3:
            data.item.access = val
        if data.atrib == 'new' and data.item.valid:
            self.data.addRegister(data.item)
            my.post_event(self.parent, my.EVT_REG_ADDED, data.item)

    def DelRecord(self, index):
        record = self.workset[index]
        if record.atrib == 'main':
            self.data.delRegister(record.item)
            my.post_event(self.parent, my.EVT_REG_DELETED, record.item)

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

    def init_workset(self, data):
        offsets = [x._offset for x in data.registers]
        workset = [self.wItem('main', x) for x in data.registers]
        if data.ref:
            for x in data.ref.registers:
                if x._offset not in offsets:
                    workset.append(self.wItem('ref', x))
        workset.sort(key=lambda x: x.item._offset)
        newitem = data.newRegister()
        if newitem:
            workset.append(self.wItem('new', newitem))
        return workset

    def get_data(self, row, col):
        return {
            0: self.workset[row].item.offset,
            1: self.workset[row].item.name,
            2: self.workset[row].item.desc,
            3: self.workset[row].item.vaccess
        }.get(col, None)


class View(wx.Panel):
    def __init__(self, parent, data):
        wx.Panel.__init__(self, parent)
        self.data = data
        # properties table
        pbox = wx.StaticBox(self, label='Peripheral')
        self.ptable = peripheralTable(self, data)
        self.pgrid = my.myGrid(pbox)
        self.pgrid.SetTable(self.ptable, True)
        # we should create extra col (mb bug in wx)
        self.pgrid.HideCol(1)
        self.pgrid.HideColLabels()
        self.pgrid.SetRowLabelSize(-1)
        self.pgrid.ShowScrollbars(wx.SHOW_SB_NEVER, wx.SHOW_SB_NEVER)

        ibox = wx.StaticBox(self, label='Peripheral Interrupts')
        self.itable = intsTable(self, data)
        self.igrid = my.myGrid(ibox)
        self.igrid.SetTable(self.itable, True)
        self.igrid.HideRowLabels()
        self.igrid.SetColLabelSize(-1)
        self.igrid.ShowScrollbars(wx.SHOW_SB_NEVER, wx.SHOW_SB_NEVER)
        self.igrid.SetSelectionMode(gridlib.Grid.wxGridSelectRows)

        rbox = wx.StaticBox(self, label='Peripheral Registers')
        self.rtable = regsTable(self, data)
        self.rgrid = my.myGrid(rbox)
        self.rgrid.SetTable(self.rtable, True)
        self.rgrid.HideRowLabels()
        self.rgrid.SetColLabelSize(-1)
        self.rgrid.ShowScrollbars(wx.SHOW_SB_NEVER, wx.SHOW_SB_ALWAYS)
        self.rgrid.SetSelectionMode(gridlib.Grid.wxGridSelectRows)

        self.Bind(wx.EVT_SIZE, self.onResize)
        self.Bind(my.MY_EVT, self.onMyEvt)

        psizer = wx.StaticBoxSizer(pbox, wx.VERTICAL)
        psizer.Add(self.pgrid, 0, wx.EXPAND | wx.ALL, 3)

        isizer = wx.StaticBoxSizer(ibox, wx.VERTICAL)
        isizer.Add(self.igrid, 0, wx.EXPAND | wx.ALL, 3)

        rsizer = wx.StaticBoxSizer(rbox, wx.VERTICAL)
        rsizer.Add(self.rgrid, 1, wx.EXPAND | wx.ALL, 3)

        msizer = wx.BoxSizer(wx.VERTICAL)
        msizer.Add(psizer, 0, wx.EXPAND | wx.ALL, 3)
        msizer.Add(isizer, 0, wx.EXPAND | wx.ALL, 3)
        msizer.Add(rsizer, 1, wx.EXPAND | wx.ALL, 3)

        self.SetSizerAndFit(msizer)

    def onMyEvt(self, event):
        eid = event.GetId()

        if eid == my.EVT_PER_REF_CHANGED or eid == my.EVT_REG_ADDED or eid == my.EVT_REG_DELETED:
            self.rtable.Reload()
            self.rgrid.ForceRefresh()
        if eid == my.EVT_INT_ADDED or eid == my.EVT_INT_DELETED:
            self.itable.Reload()
            self.Layout()

        wx.PostEvent(self.GetGrandParent(), event)

    def onResize(self, event):
        self.Layout()
        self.pgrid.FitWidth(0)
        self.igrid.FitWidth(2)
        self.rgrid.FitWidth(2)

    def DelItem(self, obj):
        if obj == self.rgrid:
            if wx.OK == wx.MessageBox('Selected registers will be deleted',
                                      'Confirm item deletion',
                                      wx.OK | wx.CANCEL | wx.ICON_QUESTION):
                for x in reversed(self.rgrid.GetSelectedRows()):
                    self.rtable.DelRecord(x)
                obj.ClearSelection()

        elif obj == self.igrid:
            if wx.OK == wx.MessageBox('Selected registers will be deleted',
                                      'Confirm item deletion',
                                      wx.OK | wx.CANCEL | wx.ICON_QUESTION):
                for x in reversed(self.igrid.GetSelectedRows()):
                    self.itable.DelRecord(x)
                obj.ClearSelection()

    def AddItem(self, obj):
        if obj == self.igrid:
            dlg = wx.TextEntryDialog(self, 'Enter new Interrupt name', 'New interrupt', 'NEW_INTERRUPT')
            if wx.ID_OK == dlg.ShowModal():
                ni = self.data.newInterrupt(dlg.GetValue())
                names = [x.name for x in self.data.interrupts]
                if ni.name and ni.name not in names:
                    self.data.addInterrupt(ni)
                    my.post_event(self, my.EVT_INT_ADDED, ni)
                else:
                    wx.MessageBox('Incorrect or existed name', 'Error', wx.OK | wx.ICON_ERROR)
        else:
            dlg = wx.TextEntryDialog(self, 'Enter new Register name', 'New register', 'NEW_REGISTER')
            if wx.ID_OK == dlg.ShowModal():
                nr = self.data.newRegister(dlg.GetValue())
                names = [x.name for x in self.data.registers]
                if nr.name and nr.name not in names:
                    self.data.addRegister(nr)
                    my.post_event(self, my.EVT_REG_ADDED, nr)
                else:
                    wx.MessageBox('Incorrect or existed name', 'Error', wx.OK | wx.ICON_ERROR)

    def CloneItem(self, obj):
        pass
