// Draws the charts: each Vega-Lite spec (.vg.json in this folder) goes into the <div> with the matching id.
// The "actions": false option hides the three-dot menu of Vega-Embed. The "svg" renderer keeps the text sharp at every zoom level and in screenshots.
var charts = [
  ["#tsx", "js/01_tsx_index_line.vg.json"],
  ["#waffle", "js/02_status_waffle.vg.json"],
  ["#choropleth", "js/03_state_share_choropleth.vg.json"],
  ["#status", "js/04_status_by_state_stacked_bar.vg.json"],
  ["#binmap", "js/05_threatened_share_bin_map.vg.json"],
  ["#lollipop", "js/06_threatened_records_lollipop.vg.json"],
  ["#year", "js/07_records_per_year_line.vg.json"],
  ["#symbolmap", "js/08_records_by_area_symbol_map.vg.json"],
  ["#slope", "js/09_state_share_slope.vg.json"],
  ["#bump", "js/10_species_rank_bump.vg.json"],
  ["#heat", "js/11_month_state_heat_map.vg.json"],
  ["#gantt", "js/12_calling_season_gantt.vg.json"],
  ["#stream", "js/13_species_month_streamgraph.vg.json"]
];
// Text sizes shared by all charts (the default Vega-Lite sizes, 10 to 11 px, are small next to the 18 px body text)
var chartConfig = {
  "axis": { "labelFontSize": 13, "titleFontSize": 14, "labelColor": "#1f2933", "titleColor": "#1f2933" },
  "legend": { "labelFontSize": 13, "titleFontSize": 14, "labelColor": "#1f2933", "titleColor": "#1f2933" }
};
charts.forEach(function (c) {
  vegaEmbed(c[0], c[1], { "actions": false, "renderer": "svg", "config": chartConfig }).catch(console.error);
});
