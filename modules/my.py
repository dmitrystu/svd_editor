from collections import namedtuple
import wx
import wx.grid as gridlib
import wx.lib.newevent

Evt, MY_EVT = wx.lib.newevent.NewCommandEvent()

EVT_FIELD_ADDED         = (100)
EVT_FIELD_DELETED       = (110)


EVT_REG_ADDED           = (200)
EVT_REG_DELETED         = (205)
EVT_REG_NAME_CHANGED    = (210)
EVT_REG_ACCS_CHANGED    = (220)


EVT_PER_ADDED           = (300)
EVT_PER_DELETED         = (305)
EVT_PER_NAME_CHANGED    = (310)
EVT_PER_OFFS_CHANGED    = (320)
EVT_PER_GROUP_CHANGED   = (330)
EVT_PER_REF_CHANGED     = (340)


EVT_DEV_NAME_CHANGED    = (405)

EVT_INT_ADDED           = (500)
EVT_INT_DELETED         = (505)

EVT_SELECTED            = (600)


def post_event(dest, event, object):
    ev = Evt(event)
    ev.SetClientData(object)
    wx.PostEvent(dest, ev)


class myTable(gridlib.PyGridTableBase):
    wItem = namedtuple('WorkItem', 'atrib, item')

    def __init__(self, parent, data):
        gridlib.PyGridTableBase.__init__(self)
        self.parent = parent
        self.data = data
        self.colorInactive = wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT)

        self.editor = gridlib.GridCellChoiceEditor(['default', 'read-only', 'read-write', 'write-only', 'writeOnce', 'read-writeOnce'])

        self.attr_dd = gridlib.GridCellAttr()
        self.attr_dd.SetEditor(self.editor)

        self.attr_dg = gridlib.GridCellAttr()
        self.attr_dg.SetEditor(self.editor)
        self.attr_dg.SetTextColour(self.colorInactive)

        self.attr_ro = gridlib.GridCellAttr()
        self.attr_ro.SetReadOnly(True)
        self.attr_ro.SetTextColour(self.colorInactive)

        self.attr_g = gridlib.GridCellAttr()
        self.attr_g.SetTextColour(self.colorInactive)

    def __del__(self):
        self.attr_dd.DecRef()
        self.attr_dg.DecRef()
        self.attr_ro.DecRef()
        self.attr_g.DecRef()
        self.editor.DecRef()
        gridlib.PyGridTableBase.__del__(self)

    def Attr(self, atype):
        attr = {'ReadOnly': self.attr_ro,
                'DropDown': self.attr_dd,
                'DropGray': self.attr_dg,
                'Gray': self.attr_g
        }.get(atype, None)
        if attr:
            attr.IncRef()
        return attr


class myGrid(gridlib.Grid):
    def __init__(self, parent):
        gridlib.Grid.__init__(self, parent)
        self.parent = parent
        self.DisableDragGridSize()

    def FitWidth(self, col):

        self.BeginBatch()
        pw, ph = self.GetClientSize()
        self.AutoSize()
        cw = self.GetRowLabelSize()
        for x in range(0, self.GetNumberCols()):
            cw += self.GetColSize(x)
        delta = pw - cw
        nw = self.GetColSize(col) + delta
        if nw > 20:
            self.SetColSize(col, nw)
            dw, dh = self.GetSize()
            dw += delta
            self.SetSize((dw, ph))
        self.EndBatch()
