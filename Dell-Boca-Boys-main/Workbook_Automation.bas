Attribute VB_Name = "Workbook_Automation"
Option Explicit

Public Sub Refresh_All()
    Application.CalculateFullRebuild
End Sub

' Create PDF invoice from Invoice_Template
Public Sub Export_Invoice_PDF()
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Worksheets("Invoice_Template")
    Dim tmp As String
    tmp = Environ$("TEMP") & "\Invoice_" & Format(Now, "yyyymmdd_hhnnss") & ".pdf"
    ws.ExportAsFixedFormat Type:=xlTypePDF, Filename:=tmp, OpenAfterPublish:=True
End Sub

' Simple AR late-fee applier: adds finance charge to overdue invoices
Public Sub Apply_AR_LateFees()
    Dim ws As Worksheet: Set ws = ThisWorkbook.Worksheets("AR_Register")
    Dim i As Long, last As Long: last = ws.Cells(ws.Rows.Count, 1).End(xlUp).Row
    Dim apr As Double: apr = ThisWorkbook.Names("Late_Fee_APR").RefersToRange.Value
    For i = 2 To last
        If ws.Cells(i, 11).Value = "Overdue" Then
            Dim bal As Double: bal = ws.Cells(i, 9).Value
            Dim fee As Double: fee = bal * apr / 12
            ws.Cells(i, 6).Value = ws.Cells(i, 6).Value + fee
        End If
    Next i
End Sub
