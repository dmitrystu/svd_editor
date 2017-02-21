import wx
import wx.grid as gridlib
import my


class deviceTable(my.myTable):
    def __init__(self, parent, data):
        my.myTable.__init__(self, parent, data)
        self.labels = ('Name', 'Description', 'Vendor', 'Data bitwidth',
                       'Default size', 'Default access', 'Default reset value')

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
        if row == 5:
            return self.Attr('DropDown')
        return None

    def SetValue(self, row, col, val):
        data = self.data
        if row == 0:
            data.name = val
            wx.PostEvent(self.parent.GetGrandParent(), my.Evt(my.EVTID_TREE_RITEM))
        elif row == 1:
            data.desc = val
        elif row == 2:
            data.vendor = val
        elif row == 3:
            data.width = val
        elif row == 4:
            data.rsize = val
        elif row == 5:
            data.access = val
        elif row == 6:
            data.rvalue = val

    def get_data(self, row, col):
        data = self.data
        if row == 0:
            return data.name
        elif row == 1:
            return data.desc
        elif row == 2:
            return data.vendor
        elif row == 3:
            return data.width
        elif row == 4:
            return data.rsize
        elif row == 5:
            return data.vaccess
        elif row == 6:
            return data.rvalue
        else:
            return None


class panlCpu(wx.Panel):
    def __init__(self, parent, data):
        wx.Panel.__init__(self, parent)
        self.data = data

        self.arch = wx.Choice(self, choices=('ARM Cortex-M0', 'ARM Cortex-M0+'))
        self.revno = wx.TextCtrl(self)
        self.endi = wx.Choice(self, choices=('little', 'big', 'selectable'))

        self.mpu = wx.CheckBox(self, style=wx.ALIGN_RIGHT)
        self.mpu.SetToolTipString('Indicate whether the processor is equipped with a memory protection unit (MPU)')

        self.fpu = wx.CheckBox(self, style=wx.ALIGN_RIGHT)
        self.fpu.SetToolTipString('Indicate whether the processor is equipped with a hardware floating point unit (FPU)')

        self.dbl = wx.CheckBox(self, style=wx.ALIGN_RIGHT)
        self.dbl.SetToolTipString('Indicate whether the processor is equipped with a double precision FPU')

        self.icache = wx.CheckBox(self, style=wx.ALIGN_RIGHT)
        self.icache.SetToolTipString('Indicate whether the processor has an instruction cache')

        self.dcache = wx.CheckBox(self, style=wx.ALIGN_RIGHT)
        self.dcache.SetToolTipString('Indicate whether the processor has a data cache')

        self.itcm = wx.CheckBox(self, style=wx.ALIGN_RIGHT)
        self.itcm.SetToolTipString('Indicate whether the processor has an instruction tightly coupled memory')

        self.dtcm = wx.CheckBox(self, style=wx.ALIGN_RIGHT)
        self.itcm.SetToolTipString('Indicate whether the processor has an data tightly coupled memory')

        self.vtor = wx.CheckBox(self, style=wx.ALIGN_RIGHT)
        self.vtor.SetToolTipString('Indicate whether the Vector Table Offset Register (VTOR) is implemented in Cortex-M0+ based devices')

        self.syst = wx.CheckBox(self, style=wx.ALIGN_RIGHT)
        self.syst.SetToolTipString('Indicate whether the processor implements a vendor-specific System Tick Timer')

        archBox = wx.FlexGridSizer(1, 6, 0, 2)
        archBox.AddGrowableCol(1, 0)
        archBox.AddGrowableCol(5, 0)
        archBox.Add(wx.StaticText(self, label='Architecture'), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 0)
        archBox.Add(self.arch, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)
        archBox.Add(wx.StaticText(self, label='Revision'), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.LEFT, 10)
        archBox.Add(self.revno, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)
        archBox.Add(wx.StaticText(self, label='Endianess'), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.LEFT, 10)
        archBox.Add(self.endi, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)

        featBox = wx.GridSizer(2, 9, 0, 0)
        featBox.Add(wx.StaticText(self, label='MPU'), 0, wx.ALIGN_CENTER, 0)
        featBox.Add(wx.StaticText(self, label='FPU'), 0, wx.ALIGN_CENTER, 0)
        featBox.Add(wx.StaticText(self, label='DBL'), 0, wx.ALIGN_CENTER, 0)
        featBox.Add(wx.StaticText(self, label='iCache'), 0, wx.ALIGN_CENTER, 0)
        featBox.Add(wx.StaticText(self, label='dCache'), 0, wx.ALIGN_CENTER, 0)
        featBox.Add(wx.StaticText(self, label='iTCM'), 0, wx.ALIGN_CENTER, 0)
        featBox.Add(wx.StaticText(self, label='dTCM'), 0, wx.ALIGN_CENTER, 0)
        featBox.Add(wx.StaticText(self, label='VTOR'), 0, wx.ALIGN_CENTER, 0)
        featBox.Add(wx.StaticText(self, label='vSYSTICK'), 0, wx.ALIGN_CENTER, 0)
        featBox.Add(self.mpu, 0, wx.ALIGN_CENTER | wx.ALL, 3)
        featBox.Add(self.fpu, 0, wx.ALIGN_CENTER | wx.ALL, 3)
        featBox.Add(self.dbl, 0, wx.ALIGN_CENTER | wx.ALL, 3)
        featBox.Add(self.icache, 0, wx.ALIGN_CENTER | wx.ALL, 3)
        featBox.Add(self.dcache, 0, wx.ALIGN_CENTER | wx.ALL, 3)
        featBox.Add(self.itcm, 0, wx.ALIGN_CENTER | wx.ALL, 3)
        featBox.Add(self.dtcm, 0, wx.ALIGN_CENTER | wx.ALL, 3)
        featBox.Add(self.vtor, 0, wx.ALIGN_CENTER | wx.ALL, 3)
        featBox.Add(self.syst, 0, wx.ALIGN_CENTER | wx.ALL, 3)

        mainBox = wx.BoxSizer(wx.VERTICAL)
        mainBox.Add(archBox, 0, wx.EXPAND | wx.ALL, 3)
        mainBox.Add(featBox, 0, wx.EXPAND | wx.ALL, 3)
        self.SetSizerAndFit(mainBox)


class View(wx.Panel):
    def __init__(self, parent, data):
        wx.Panel.__init__(self, parent)
        self.data = data
        devbox = wx.StaticBox(self, label='Device base')
        # properties table
        self.dtable = deviceTable(self, data)
        self.dgrid = my.myGrid(devbox)
        self.dgrid.SetTable(self.dtable, True)
        self.dgrid.ShowScrollbars(wx.SHOW_SB_NEVER, wx.wx.SHOW_SB_NEVER)
        # we should create extra col (mb bug in wx)
        self.dgrid.HideCol(1)
        self.dgrid.HideColLabels()
        self.dgrid.SetRowLabelSize(-1)

        cpubox = wx.StaticBox(self, label='CPU features (not yet implemented)')
        self.cpanl = panlCpu(cpubox, data)

        self.Bind(wx.EVT_SIZE, self.onResize)
        self.Bind(my.MY_EVT, self.onMyEvt)

        dsizer = wx.StaticBoxSizer(devbox, wx.VERTICAL)
        dsizer.Add(self.dgrid, 0, wx.EXPAND | wx.ALL, 3)
        csizer = wx.StaticBoxSizer(cpubox, wx.VERTICAL)
        csizer.Add(self.cpanl, 0, wx.EXPAND | wx.ALL, 3)

        msizer = wx.BoxSizer(wx.VERTICAL)
        msizer.Add(dsizer, 0, wx.EXPAND | wx.ALL, 3)
        msizer.Add(csizer, 0, wx.EXPAND | wx.ALL, 3)

        self.SetSizerAndFit(msizer)

    def onMyEvt(self, event):
        pass

    def CloneItem(self, obj):
        pass

    def DelItem(self, obj):
        pass

    def AddItem(self, obj):
        pn = self.data.newPeripheral('NEW_PERIPHERAL')
        dlg = wx.TextEntryDialog(self, 'Enter new peripheral name', 'New peripheral', pn.name)
        if wx.ID_OK == dlg.ShowModal():
            pn.name = dlg.GetValue()
            names = [x.name for x in self.data.peripherals]
            if pn.name and pn.name not in names:
                self.data.addPeripheral(pn)
                my.post_event(self.GetGrandParent(), my.EVT_PER_ADDED, pn)
            else:
                wx.MessageBox('Incorrect or existed name', 'Error', wx.OK | wx.ICON_ERROR)

    def onResize(self, event):
        self.Layout()
        self.dgrid.FitWidth(0)
