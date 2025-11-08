\
Attribute VB_Name = "NYFS_Refresh"
Option Explicit

Public Sub NormalizeDates()
    Dim ws As Worksheet
    For Each ws In ThisWorkbook.Worksheets
        If ws.Name <> "READ_ME" Then
            ws.Cells.Replace What:="/", Replacement:"-", LookAt:=xlPart
        End If
    Next ws
    MsgBox "Date normalization done.", vbInformation
End Sub

Public Sub ValidateCOA()
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Worksheets("chart_of_accounts")
    Dim lastRow As Long: lastRow = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
    Dim i As Long
    For i = 2 To lastRow
        If ws.Cells(i, 1).Value = "" Or ws.Cells(i, 3).Value = "" Then
            ws.Cells(i, 1).Interior.Color = RGB(255, 200, 200)
        End If
    Next i
    MsgBox "COA validation complete. Empty AccountID/Type flagged.", vbInformation
End Sub
