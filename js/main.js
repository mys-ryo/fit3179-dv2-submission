// Draws the charts: each Vega-Lite spec (.vg.json in this folder) goes into the <div> with the matching id.
// The "actions": false option hides the three-dot menu of Vega-Embed.
var charts = [
  ["#tsx", "js/01_tsx_index_line.vg.json"],
  ["#waffle", "js/02_status_waffle.vg.json"],
  ["#choropleth", "js/03_state_share_choropleth.vg.json"],
  ["#status", "js/04_status_by_state_stacked_bar.vg.json"],
  ["#lollipop", "js/05_threatened_records_lollipop.vg.json"],
  ["#binmap", "js/06_threatened_share_bin_map.vg.json"],
  ["#year", "js/07_records_per_year_line.vg.json"],
  ["#symbolmap", "js/08_records_by_area_symbol_map.vg.json"],
  ["#slope", "js/09_state_share_slope.vg.json"],
  ["#heat", "js/10_month_state_heat_map.vg.json"],
  ["#gantt", "js/11_calling_season_gantt.vg.json"],
  ["#stream", "js/12_species_month_streamgraph.vg.json"],
  ["#bump", "js/13_species_rank_bump.vg.json"]
];
// Text sizes shared by all charts (the default Vega-Lite sizes, 10 to 11 px, are small next to the 18 px body text)
var chartConfig = {
  "axis": { "labelFontSize": 13, "titleFontSize": 14 },
  "legend": { "labelFontSize": 13, "titleFontSize": 14 }
};
charts.forEach(function (c) {
  vegaEmbed(c[0], c[1], { "actions": false, "config": chartConfig }).catch(console.error);
});
