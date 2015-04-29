Function Formula(f As String)
  Formula = GetRangeFormulaFromFormula(Replace(Left(f, InStrRev(f, ",") - 1), ")", ""))
End Function


Function Expand(r As Range, r2 As Range) As Range

  If r Is Nothing Then
    Set Expand = r2
    Exit Function
  End If

  If r2 Is Nothing Then
    Set Expand = r
    Exit Function
  End If

  begincol = r.Column
  beginrow = r.Row
  endcol = r.Columns(r.Columns.Count).Column
  endrow = r.Rows(r.Rows.Count).Row

  If r2.Column < begincol Then
    begincol = r2.Column
  End If

  If r2.Row < beginrow Then
    beginrow = r2.Row
  End If

  If r2.Columns(r2.Columns.Count).Column > endcol Then
    endcol = r2.Columns(r2.Columns.Count).Column
  End If

  If r2.Rows(r2.Rows.Count).Row > endrow Then
    endrow = r2.Rows(r2.Rows.Count).Row
  End If

  Set Expand = r.Worksheet.Range(r.Worksheet.Cells(beginrow, begincol), r.Worksheet.Cells(endrow, endcol))
  s = Expand.Address(False, False)
End Function

Function GetRange(r As String) As Range

  innerbits = Mid(r, InStr(r, "(") + 1, InStrRev(r, ")") - InStr(r, "(") - 1)
  innerbits = Replace(Replace(innerbits, "(", ""), ")", "")
  parts = Split(innerbits, ",")


  Dim currange As Range

  For Each part In parts
    If Len(part) > 2 Then
      innerparts = Split(part, "!")
      sheetname = innerparts(0)
      If Left(sheetname, 1) = "'" And Right(sheetname, 1) = "'" Then
        sheetname = Mid(sheetname, 2, Len(sheetname) - 2)
      End If

      If InStr(part, "!") > 0 Then
        reference = innerparts(1)

        Dim rr As Range
        Set rr = Worksheets(sheetname).Range(reference)
        Set currange = Expand(currange, rr)
      End If
    End If
  Next part

  Set GetRange = currange
End Function

Function formatcollection(c As Collection, flatten As Boolean) As String
  If c.Count() = 1 And flatten = True Then
    formatcollection = "'" + c.Item(1) + "'"
  Else
    Dim s As String
    s = "["
    For pos = 1 To c.Count()
      s = s + "'" + c.Item(pos) + "'"
      If pos < c.Count() Then
        s = s + ", "
      End If
    Next pos
    s = s + "]"
    formatcollection = s
  End If


End Function

Sub DumpStuff()
  '
  ' DumpStuff Macro
  '

  ' This was used to extract the chart information from the excel spreadsheets provided by GARD



  Dim Workb As Workbook
  For Each Workb In Workbooks
    Workb.Activate

    workbookname = Workb.Name

    ' Declare a FileSystemObject.
    Dim fso As FileSystemObject

    ' Create a FileSystemObject.
    Set fso = New FileSystemObject
    ' Declare a TextStream.
    Dim stream As TextStream

    ' Create a TextStream.
    Set stream = fso.CreateTextFile(ActiveWorkbook.FullName + "-Charts.py", True)

    Dim collectedCharts As Collection

    Set collectedCharts = New Collection

    For Each thissheet In Worksheets
      Dim thischarto As ChartObject
      For Each thischarto In thissheet.ChartObjects
        collectedCharts.Add thischarto.Chart
      Next thischarto
    Next thissheet

    Dim thischart As Chart
    For Each thischart In Charts
      collectedCharts.Add thischart
    Next thischart


    Dim Chart As Chart


    For Each Chart In collectedCharts

      Dim ser As Series

      Dim b As String
      Dim e As String
      Dim Sheet As String

      chartname = ""
      If Not IsNull(Chart.Parent.Parent) Then
        If Chart.Parent.Parent.Name <> "Microsoft Excel" Then
          chartname = Chart.Parent.Parent.Name
        Else
          chartname = Chart.Name
        End If
      Else
        chartname = Chart.Name
      End If

      Sheet = Chart.SeriesCollection(1).Formula
      Dim paren As Integer
      paren = InStr(Sheet, "(")
      Dim exclamation As Integer
      exclamation = InStr(Sheet, "!")
      fullrangestr = ""
      For i = 1 To Chart.SeriesCollection.Count
        Dim obj As Series
        Set obj = Chart.SeriesCollection(i)
        curr = obj.Formula
        fullrangestr = fullrangestr + curr + ";"
      Next i


      superrange = Expand(GetRange(Chart.SeriesCollection(1).Formula), GetRange(Chart.SeriesCollection(Chart.SeriesCollection.Count).Formula)).Address

      Sheet = Mid(Sheet, paren + 1, exclamation - paren - 1)
      comma = InStr(Sheet, ",")
      If comma > 0 Then
        Sheet = Mid(Sheet, comma + 1)
      End If

      If Left(Sheet, 1) = "'" And Right(Sheet, 1) = "'" Then
        Sheet = Mid(Sheet, 2, Len(Sheet) - 2)
      End If

      Dim horizontalAxisText As Collection
      Dim verticalAxisText As Collection

      Set horizontalAxisText = New Collection
      Set verticalAxisText = New Collection

      Dim a As Axis

      For Each a In Chart.Axes
        If a.HasTitle Then
          If a.Type = xlValue Then
            verticalAxisText.Add Trim(a.AxisTitle.Text)
          ElseIf a.Type = xlCategory Then
            horizontalAxisText.Add Trim(a.AxisTitle.Text)
          End If
        End If
      Next a

      Dim notes As Collection
      Set notes = New Collection

      Dim s As Shape
      For Each s In Chart.Shapes
        If Trim(s.TextFrame2.TextRange.Text) <> "" And s.TextFrame2.TextRange.Text <> "EnergyPlus Version 8.2.0" Then
          notes.Add Trim(s.TextFrame2.TextRange.Text)
          'MsgBox (Asc(Mid(notes(notepos), Len(notes(notepos)), 1)))
          'MsgBox ("'" + notes(notepos) + "'")
        End If
      Next s

      Dim charttype As String

      Select Case Chart.charttype
        Case xlLine
          charttype = "Line"
        Case xlColumnClustered
          charttype = "ColumnClustered"
        Case xlBarClustered
          charttype = "BarClustered"
        Case xlBarStacked
          charttype = "BarStacked"
        Case xlXYScatter
          charttype = "Scatter"
        Case xlXYScatterLines
          charttype = "ScatterLines"
        Case xlXYScatterLinesNoMarkers
          charttype = "ScatterLinesNoMarkers"
        Case xlLineMarkers
          charttype = "ScatterLines"
        Case xlXYScatterSmooth
          charttype = "ScatterSmooth"
        Case -4111
          charttype = "Combo"
        Case Else
          MsgBox ("Unknown!")
      End Select

      Dim r As Range
      Worksheets(Sheet).Activate

      firstparen = InStr(fullrangestr, "(")
      firstexcl = InStr(fullrangestr, "!")

      sheetname = Mid(fullrangestr, firstparen + 1, firstexcl - firstparen - 1)

      morethanonesheet = False

      For Each splitsheet In Split(fullrangestr, "!")
        If InStr(fullrangestr, sheetname) = 0 Then
          morethanonesheet = True
          Exit For
        End If
      Next splitsheet

      If Not morethanonesheet Then
        fullrangestr = Replace(fullrangestr, sheetname + "!", "")
      Else
        superrange = ""
      End If

      If Left(sheetname, 1) = "'" Then
        sheetname = Mid(sheetname, 2, Len(sheetname) - 2)
      End If

      ct = ""
      If Chart.HasTitle Then
        ct = Chart.ChartTitle.Text
      End If
      chartdescription = "engine.write_chart('" + charttype + "', '" + chartname + "', '" + ct + "', " + formatcollection(horizontalAxisText, True) + ", " + formatcollection(verticalAxisText, True) + ", '" + ActiveWorkbook.Name + "', '" + sheetname + "', '" + superrange + "', """ + fullrangestr + """"
      chartdescription = chartdescription + ", "
      chartdescription = chartdescription + formatcollection(notes, False)


      chartdescription = chartdescription + ")"
      chartdescription = Replace(Replace(chartdescription, Chr(13), "\n"), Chr(10), "\n")
      chartdescription = Replace(chartdescription, "$", "")
      chartdescription = Replace(chartdescription, "=SERIES", "")
      chartdescription = Replace(chartdescription, "\n ", "\n")

      If charttype <> "Skip" Then
        stream.WriteLine (chartdescription)
      End If
    Next Chart
  Next Workb
End Sub


