\
Attribute VB_Name = "NYFS_Menu"
Option Explicit

Public Sub NYFS_Menu()
    Dim choice As Variant
    choice = Application.InputBox("NYFS Actions:" & vbCrLf & _
        "1 = Normalize Dates" & vbCrLf & _
        "2 = Validate Chart of Accounts" & vbCrLf & _
        "3 = Build AR Aging", "NYFS Suite", Type:=1)
    If choice = False Then Exit Sub
    Select Case CLng(choice)
        Case 1: Call NYFS_Refresh.NormalizeDates
        Case 2: Call NYFS_Refresh.ValidateCOA
        Case 3: Call NYFS_Aging.BuildARAging
        Case Else: MsgBox "Unknown option"
    End Select
End Sub
