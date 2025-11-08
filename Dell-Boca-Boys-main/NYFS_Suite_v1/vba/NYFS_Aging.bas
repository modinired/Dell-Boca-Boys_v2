\
Attribute VB_Name = "NYFS_Aging"
Option Explicit

Private Function AgeBucket(ByVal daysPast As Long) As String
    If daysPast <= 0 Then AgeBucket = "Current": Exit Function
    If daysPast <= 30 Then AgeBucket = "1-30": Exit Function
    If daysPast <= 60 Then AgeBucket = "31-60": Exit Function
    If daysPast <= 90 Then AgeBucket = "61-90": Exit Function
    AgeBucket = "90+"
End Function

Public Sub BuildARAging()
    Dim ws As Worksheet, outWs As Worksheet
    Set ws = ThisWorkbook.Worksheets("ar_entries")
    On Error Resume Next
    Set outWs = ThisWorkbook.Worksheets("AR_Aging")
    If outWs Is Nothing Then
        Set outWs = ThisWorkbook.Worksheets.Add
        outWs.Name = "AR_Aging"
    End If
    On Error GoTo 0

    outWs.Cells.Clear
    outWs.Range("A1:F1").Value = Array("CustomerID", "Current", "1-30", "31-60", "61-90", "90+")

    Dim lastRow As Long: lastRow = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
    Dim dict, cust As Variant
    Set dict = CreateObject("Scripting.Dictionary")

    Dim i As Long
    For i = 2 To lastRow
        Dim custId As String: custId = ws.Cells(i, 2).Value
        Dim dueDate As Date: dueDate = ws.Cells(i, 5).Value
        Dim amt As Double: amt = ws.Cells(i, 7).Value + ws.Cells(i, 8).Value - ws.Cells(i, 9).Value
        Dim daysPast As Long: daysPast = Date - dueDate
        Dim b As String: b = AgeBucket(daysPast)
        If Not dict.Exists(custId) Then
            dict.Add custId, Array(0, 0, 0, 0, 0)
        End If
        Dim arr: arr = dict(custId)
        Select Case b
            Case "Current": arr(0) = arr(0) + amt
            Case "1-30": arr(1) = arr(1) + amt
            Case "31-60": arr(2) = arr(2) + amt
            Case "61-90": arr(3) = arr(3) + amt
            Case "90+": arr(4) = arr(4) + amt
        End Select
        dict(custId) = arr
    Next i

    Dim r As Long: r = 2
    For Each cust In dict.Keys
        Dim vals: vals = dict(cust)
        outWs.Cells(r, 1).Value = cust
        outWs.Cells(r, 2).Resize(1, 5).Value = vals
        r = r + 1
    Next cust
    outWs.Columns.AutoFit
    MsgBox "AR Aging built.", vbInformation
End Sub
