# Analysis outputs — NIKE

- [Excel model](NKE_Financial_Analysis.xlsx): Summary → Drivers → Historical → Forecast → Valuation → Sensitivity → Peers → Segments → Sources.
- [Historical financials](historical_financials.csv): one fiscal year per row; dollar amounts and shares in millions, ratios as decimals.
- [Model results](valuations.json): assumptions, all forecast rows, scenario values, sensitivity and reverse DCF.
- [Selected SEC facts](sec_provenance.json) and [peer facts](peer_provenance.json): original tags, units, periods, filing dates and accession numbers.
- [Peer comparison](peers.json): TTM calculation components and dated market capitalisation inputs.
- [Segment data](segments.json): disclosed revenue components and their reporting basis.

**How to explore:** open Excel and change **Drivers B3** to 1, 2 or 3. The financial statements and valuation recalculate. Change blue inputs to test your own view. Keep WACC above terminal growth.

**Evidence:** worksheet images are rendered directly from the generated Excel workbook; report screenshots are captured from native Power BI Desktop. They are not a company's original Excel file.

![Valuation model](../evidence/Valuation.png)
